import ltclogger as log

# Phidgets specific imports
from Phidget22.Devices.DigitalOutput import DigitalOutput
from Phidget22.Devices.VoltageInput import VoltageInput
from Phidget22.Devices.VoltageRatioInput import VoltageRatioInput
from Phidget22.Net import Net
from Phidget22.Phidget import Phidget
from Phidget22.PhidgetException import PhidgetException

########### Phidgets Setup ########

RED = (1, 0, 0, 1)
GREEN = (0, 1, 0, 1)

class LTCPhidget(Phidget):
    def __init__(self):
        super().__init__()
        # TODO: can the remote specific events find a disconnected usb cable?
        self._callback = {
            'attach': [],
            'detach': [],
            'error': [],
            'property': [],
        }

        self.setOnAttachHandler(self._on_attach)
        self.setOnDetachHandler(self._on_detach)
        self.setOnErrorHandler(self._on_error)
        self.setOnPropertyChangeHandler(self._on_property)

    def add_callback(self, cb, event_type):
        log.debug(f"Adding callback to {self.name}")
        self._callback[event_type].append(cb)

    def _on_attach(self):
        log.verbose(f"attach event received")
        for cb in self._callback['attach']:
            cb()

    def _on_detach(self):
        log.verbose(f"detach event received")
        for cb in self._callback['attach']:
            cb()

    def _on_error(self, code, description):
        log.debug(description)
        log.verbose(f"error code {code} received")
        for cb in self._callback['error']:
            cb(code)

    def _on_property(self, name):
        log.verbose("property {name} changed")
        for cb in self._callback['value']:
            cb(name)

class Relay(LTCPhidget, DigitalOutput):
    def __init__(self, name, devserial, channel, *, invert=False):
        super().__init__()
        self.setDeviceLabel(name)
        self.setDeviceSerialNumber(devserial)
        self.setChannel(channel)

        self._callback['value'] = self._callback['property']

        self.unit = ''
        self.name = name
        self.abnormal = 'Open' if invert else 'Closed'
        self.nominal = 'Closed' if invert else 'Open'

    def setState(self, state):
        log.info(f"Setting {self.name} state to {state}")
        super().setState(state)

    def convert(self, sample):
        return "Closed" if sample else "Open"

    def nominal_value(self, val):
        if val == self.abnormal:
            return RED
        if val == self.nominal:
            return GREEN
        raise TypeError


class TemperatureSensor(LTCPhidget, VoltageRatioInput):
    def __init__(self, name, devserial, channel, upper, lower):
        super().__init__()
        self._callback['value'] = []
        self.setOnVoltageRatioChangeHandler(self._on_voltage)

        self.setDeviceLabel(name)
        self.setDeviceSerialNumber(devserial)
        self.setChannel(channel)

        self.unit = "C"
        self.name = name
        self.upper = upper
        self.lower = lower

    def _on_voltage(self, ratio):
        log.verbose("ratio {ratio} changed")
        for cb in self._callback['value']:
            cb(ratio)

    def convert(self, sample):
        return (sample * 2.0 / 9.0) - 61.111

    def nominal_value(self, val):
        if self.lower < val < self.upper:
            return GREEN
        return RED


class VoltageSensor(LTCPhidget, VoltageInput):
    def __init__(self, name, devserial, channel, upper, lower):
        super().__init__()
        self._callback['value'] = []
        self.setOnVoltageChangeHandler(self._on_voltage)

        self.unit = "V"
        self.name = name
        self.upper = upper
        self.lower = lower

    def _on_voltage(self, value):
        log.verbose("voltage {value} changed")
        for cb in self._callback['value']:
            cb(value)

    def nominal_value(self, val):
        if self.lower < val < self.upper:
            return GREEN
        return RED

    def convert(self, sample):
        return (sample / 200.0 - 2.5) / 0.0681


class LTCbackend:
    def __init__(self, set_status):
        log.info("Starting Backend")
        # Interface Kit 0/0/4 with relays - 1014
        self.ignition = Relay('Ignition Relay', devserial=259173, channel=0)
        self.ignition.add_callback(self.attach, 'attach')
        self.shore = Relay('Shorepower Relay', devserial=259173, channel=3, invert=True)
        self.shore.add_callback(self.output, 'property')

        # Interface Kit 8/8/8 with sensors attached - 1018
        # Here, sensor[n] describes the nth sensor on the Interface Kit (IK),
        # following the Phidget convention. If sensor positions on the IK are
        # changed, the 'sensor' dictionary keys must be properly updated here.
        self.inputWindspeed = 7  # make a sensor?
        self.sensors = [
            TemperatureSensor("Internal Temperature", 178346, 0,  40.0, 10.0),
            VoltageSensor(    "Ignition Battery",     178346, 1, 4.1*4, 3.6*4),
            VoltageSensor(    "Humidity",             178346, 3,  1000,    0), # FIXME: type, maxmin
            TemperatureSensor("External Temperature", 178346, 4,  40.0, 10.0),
            VoltageSensor(    "Rocket Ready",         178346, 2,   5.0,  1.5),
            VoltageSensor(    "System Battery",       178346, 5,  15.0, 11.0),
            VoltageSensor(    "Solar Voltage",        178346, 6,  25.0, 11.0),
            VoltageSensor(    "Shore Power",          178346, 7,  20.0, 18.0),
        ]

        for sensor in self.sensors:
            sensor.add_callback(self.attach, 'attach')

        self.set_status = set_status

    def start(self, event):
        #Net.addServer('ltc', 'ltc.psas.lan', 5001, '', 0)
        Net.addServer('ltc', '10.0.3.2', 5001, '', 0)
        self.ignition.open()
        self.shore.open()
        for sensor in self.sensors:
            sensor.open()

    def attach(self, event):
        self.ignite(False)

    def output(self, name):
        print(name)
        # FIXME state might not even exist, use getState?
        # This also seems like unecesary indirection
        self.shorepower_state = name.state

    def close(self, event):
        log.debug("Closing LTCBackend")
        try:
            self.ignite(False)
        except PhidgetException:
            log.info("Unable to turn off ignite on quit")
        self.ignition.close()
        self.shore.close()
        for sensor in self.sensors:
            sensor.close()

    def ignite(self, state):
        try:
            if not state:
                self.ignition.setState(False)
            elif not self.shorepower_state:
                self.ignition.setState(True)
            else:
                # TODO: more descriptive errno?
                raise PhidgetException(1)  # noqa: TRY301 Not sure how to restructure this
        except PhidgetException:
            self.set_status("Phidget Call Failed")
            raise

    def shorepower(self, state):
        try:
            self.shore.setState(state)
            self.set_status("Nominal")
        except PhidgetException:
            self.set_status("Phidget Call Failed")
            raise


# Relays 1014-2
# Voltage 1135-0 x5
# Temp 1124-0
# missing external temp/himid?
