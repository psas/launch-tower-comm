/* - Servo multi -
 * This example is very similar to the Servo-full example, except that this example demonstrates attaching and using two Phidget
 * Servo Controllers simultaneously.  Please note the two serial number variables declared at the beginning of the class.
 * These are used to store the serial numbers of the Phidgets Servos that we are attaching.  Please change these to reflect the serial
 * numbers of your own phidgets before running the program or you will find that it won't work.
 *
 * Note: This example can be easily modified to support more than two Phidget Servos.  To do this you simply need to create
 * seperate servo objects for each new Phidget Servo Controller you wish to be able to control and supply the serial number of each
 * subsequent device to the respect object's open() method.
 *
 * Copyright 2007 Phidgets Inc.  
 * This work is licensed under the Creative Commons Attribution 2.5 Canada License. 
 * To view a copy of this license, visit http://creativecommons.org/licenses/by/2.5/ca/
 */
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Text;
using System.Windows.Forms;
using Phidgets;             // for the phidget class and the exceptions class
using Phidgets.Events;      // for the event handling classes
using System.Collections;

/* 
 * =======================================================================================================
 *
 * 2012-08-02
 * Added code to read settings from external text file
 * 
 * 
 * =======================================================================================================
 */





/*
 * TO DO LIST
 * Animated graphs - http://www.codeproject.com/Articles/32836/A-simple-C-library-for-graph-plotting
 * */


namespace Servo_Multi
{
    public partial class Form1 : Form
    {

        string inputFile = "c:\\config.txt";                        // input file - which sensors in which location
        
        string outputFileStatus = "c:\\programstatus.txt";          // output file - program messages


        // ----- MODIFY THIS ARRAY TO TELL WHAT SENSOR IN WHAT ANALOG SLOT -----
        private string[] analogSensorInput = new string[8] {
            "voltageIgnition",         // sensor on analog input 0
            "temperatureEnclosure",        // sensor on analog input 1
            "temperatureTower",      // sensor on analog input 2
            "humidityTower",        // sensor on analog input 3
            "voltageSolar",            // sensor on analog input 4
            "voltageRocket",     // sensor on analog input 5
            "voltageSystem",        // sensor on analog input 6
            "windSpeed"  // sensor on analog input 7
        };

        // ----- MODIFY THIS ARRAY TO TELL WHAT EACH RELAY IS TRIGGERING -----
        private string[] digitalRelayOutput = new string[4] {
            "relayRocketFire",       // relay on digital output 0
            "relaySiren",           // relay on digital output 1
            "relayLight",           // relay on digital output 2
            "relayUmbilical",      // relay on digital output 3
        };

        // ----- MODIFY THIS ARRAY TO TELL WHAT EACH GPIO IS TRIGGERING -----
        private string[] gpioOutput = new string[8] {
            "gpioUmbilical",        // item on digital output 0
            "z1",        // item on digital output 1
            "z2",        // item on digital output 2
            "z3",        // item on digital output 3
            "z4",        // item on digital output 4
            "z5",        // item on digital output 5
            "z6",        // item on digital output 6
            "z7",        // item on digital output 7
        };

        
        private double maxVoltageSolar = 24;                // maximum voltage on solar panel - before error thrown
        private double maxVoltageBattSystem = 24;           // maximum voltage on system battery - before error thrown
        private double maxVoltageBattIgnition = 24;         // maximum voltage on ignition battery - before error thrown
        private double maxVoltageRocket = 20;               // maximum voltage on rocket umbilical - before error thrown

        private double minVoltageSolar = 8;                 // minimum default on solar panel - before error thrown
        private double minVoltageBattSystem = 8;            // minimum default on system battery - before error thrown
        private double minVoltageBattIgnition = 8;          // minimum default voltage on ignition battery - before error thrown
        private double minVoltageRocket = 15;               // minimum default voltage on rocket umbilical - before error thrown

        private int sensorDataRate = 2;                     // default analog sensor rate

        private int windSensorCount = 0;                    // holds the current count
        private double TriggersPerSecondMPH = 1;            // how many triggers per timer tick = 1 MPH
        private int timerTickInterval = 1000;               // tick interval (MS)
        


        // ----- PHIDGET SERIAL NUMBERS -----
        int serialNuminterface1 = 178346;
        int serialNumEncoder1   = 82292;
        int serialNumRelay1     = 259173;



        // ----- NON-MODIFIABLE VARIABLES -----
        Phidgets.Encoder encoder;                           // Declare an encoder object
        private InterfaceKit ifKit;                         // Declare an interface kit object
        private InterfaceKit relayKit;                      // Declare a relay interface kit object

        private ArrayList inputArray;
        private ErrorEventBox errorBox;
        private TextBox[] sensorInArray = new TextBox[8];   // stores analog sensor value

        public bool phidgetEncoderFound = false;            // stores if phidget device found
        public bool phidgetInterfaceFound = false;          // stores if phidget device found
        public bool phidgetRelayFound = false;              // stores if phidget device found

        string phidgetServerIpAddress = "";                 // will store IP Address
        int phidgetServerPortNumber = 0;                    // will store port number
        string phidgetServerPassword = "";                  // will store password

        private HiPerfTimer pt;

        const int velQueueSize = 50;                        // ??? - may be used for rotary encoder
        Queue velData = new Queue(velQueueSize);            // ??? - may be used for rotary encoder


        // initialize dictionary to hold phidget values
        public Dictionary<string, float> phidgetValues = new Dictionary<string, float>();

        string outputFileSensor = "";                // will hold output filename - sensor logs

        
            


        /*
         * ====================================================================================================
         * ====================== FORM FUNCTIONS ==============================================================
         * ====================================================================================================
        */

        // ----- FUNCTION :: Application is starting up
        public Form1()
        {
            InitializeComponent();                                          // initialize this form controls
            
            LogScreen("Welcome to Launch Control v1.0");                    // log message
            LogScreen("Initializing Form");                                 // log message
            
            ifKit_Uninitialize_Display();                                   // handle form elements related to ifKit
            relayKit_Uninitialize_Display();                                // handle form elements related to relayKit
            encoder_Uninitialize_Display();                                 // handle form elements related to encoder

            errorBox = new ErrorEventBox();                                 // declare error handling class
            
            LogScreen("Processing Phidget device status.");                 // log message
            NetworkDisplayDisconnected();                                   // handle initial network config

            TextFromFile ZtxtObj = new TextFromFile();                      // instantiate the class
            string theOutput = ZtxtObj.readFile(inputFile);                 // open and read the file
            txtTempOutput.Text = theOutput;


            initializeLogfile();                                            // create the logfile (with unique name)
            initializePhidgetValueDictionary();                             // initialize the dictionaty holding phidget log values
            timerLogfileInitialize();                                       // initialize the logfile timer

            
            
        }

        // ----- FUNCTION :: Application is terminating
        private void Form1_FormClosed(object sender, FormClosedEventArgs e)
        {
            Application.DoEvents();     // ----- Run any events in the message queue - otherwise close will hang if there are any outstanding events
            PhidgetsDisconnect();       // disconnect all phidget devices
        }

        private void btnGPIO1_Click(object sender, EventArgs e)
        {
            processGPIOButton("gpioUmbilical", btnGPIO1);

            if (btnGPIO1.Text == "ON")
            {
                grpRocketFire.Enabled = false;      // disable rocket fire if umbillical is on
                btnRelay4.Visible = false;          // hide the button
                lblRocketFire.Text = "Umbilical Power Must Be Off";
            }
            else
            {
                grpRocketFire.Enabled = true;       // disable rocket fire if umbillical is on
                btnRelay4.Visible = true;           // show the button
                lblRocketFire.Text = "Rocket Fire:";
            }
        }

        private void btnRelay1_Click(object sender, EventArgs e)
        {
            processRelayButton("relayUmbilical", btnRelay1);
        }

        private void btnRelay2_Click(object sender, EventArgs e)
        {
            processRelayButton("relaySiren", btnRelay2);
        }

        private void btnRelay3_Click(object sender, EventArgs e)
        {
            processRelayButton("relayLight", btnRelay3);
        }

        private void btnRelay4_Click(object sender, EventArgs e)
        {
            processRelayButton("relayRocketFire", btnRelay4);
        }

        private void btnConnectPhidgets_Click(object sender, EventArgs e)
        {
            PhidgetsConnectSetup();         // connect to phidget devices
            NetworkDisplayConnected();      // run cleanup on the netowrk display (???)
        }

        private void btnDisconnectPhidgets_Click(object sender, EventArgs e)
        {
            PhidgetsDisconnect();           // disconnect from phidget devices
            NetworkDisplayDisconnected();   // run cleanup on the netowrk display
        }

        void processGPIOButton(string gpioTitle, Button btn)
        {
            if (ifKit != null)
            {
                string colorOn = "LightGreen";
                string colorOff = "DarkRed";
                string colorTextOn = "Black";
                string colorTextOff = "White";

                int GPIONum = Array.IndexOf(gpioOutput, gpioTitle);                         // figure out the GPIO number based on array position
                bool curStatus = ifKit.outputs[GPIONum];                                    // get current status of this GPIO
                bool newStatus = !curStatus;                                                // swap the GPIO high/low status
                string newText = (newStatus == true) ? "ON" : "OFF";                        // determine what button text should be
                string tmpColorBackground = (newStatus == true) ? colorOn : colorOff;       // determine what button background color should be
                string tmpColorText = (newStatus == true) ? colorTextOn : colorTextOff;     // determine what button forecolor should be

                string cbName = "cbGPIOStatus" + GPIONum;                                   // create name of checkbox
                CheckBox cb = (CheckBox)this.Controls.Find(cbName, true)[0];                // find checkbox control

                cb.Checked = newStatus;                                                     // check the visual checkbox indicator
                ifKit.outputs[GPIONum] = newStatus;                                         // toggle the actual GPIO
                btn.Text = newText;                                                         // set button text
                btn.BackColor = Color.FromName(tmpColorBackground);                         // set button background color
                btn.ForeColor = Color.FromName(tmpColorText);                               // set button forecolor
            }
        }

        void processRelayButton(string relayTitle, Button btn)
        {
            if (relayKit != null)
            {
                string colorOn = "LightGreen";
                string colorOff = "DarkRed";
                string colorTextOn = "Black";
                string colorTextOff = "White";

                int relayNum = Array.IndexOf(digitalRelayOutput, relayTitle);               // figure out the relay number based on array position
                bool curStatus = relayKit.outputs[relayNum];                                // get current status of this relay
                bool newStatus = !curStatus;                                                // swap the relay on/off status
                string newText = (newStatus == true) ? "ON" : "OFF";                        // determine what button text should be
                string tmpColorBackground = (newStatus == true) ? colorOn : colorOff;       // determine what button background color should be
                string tmpColorText = (newStatus == true) ? colorTextOn : colorTextOff;     // determine what button forecolor should be

                string cbName = "cbRelayStatus" + relayNum;                                 // create name of checkbox
                CheckBox cb = (CheckBox)this.Controls.Find(cbName, true)[0];                // find checkbox control

                cb.Checked = newStatus;                                                     // check the visual checkbox indicator
                relayKit.outputs[relayNum] = newStatus;                                     // toggle the actual relay
                btn.Text = newText;                                                         // set button text
                btn.BackColor = Color.FromName(tmpColorBackground);                         // set button background color
                btn.ForeColor = Color.FromName(tmpColorText);                               // set button forecolor
            }
        }


        // ----- FUNCTION :: Connect to all phidget devices over network
        private void PhidgetsConnectSetup()
        {
            bool passChecks = true;
            phidgetServerIpAddress = txtIPAddress.Text;
            phidgetServerPassword = txtServerPassword.Text;
            phidgetServerPortNumber = (isInt32(txtPortAddress.Text)) ? Convert.ToInt32(txtPortAddress.Text) : 0;
            
            if (phidgetServerPortNumber == 0) {
                MessageBox.Show("ERROR :: Port number is not a valid sequence of digits.");
                passChecks = false;
            }

            if (phidgetServerIpAddress == "")
            {
                MessageBox.Show("ERROR :: ENTER AN IP ADDRESS");
                passChecks = false;
            }

            if (passChecks) {

                NetworkDisplayConnected();      // disable connection area

                InitializePhidgetEncoder();     // INITIALIZE THE ROTARY ENCODER
                InitializePhidgetInterface();   // INITIALIZE THE INTERFACE KIT
                InitializePhidgetRelay();       // INITIALIZE THE RELAY INTERFACE KIT

                makeSensorInArray();            // initialize the sensor array textfield values - analog inputs
                makeDigiOutArray();             // initialize the sensor array textfield values - digital outputs



                // ----- INITIALIZE THE HIGH PERFORMANCE COUNTER (for wind speed calculation) -----
                //pt = new HiPerfTimer();     // create a new PerfTimer object
                //pt.Start();                             // start the timer

                tmrWindSpeed.Interval = timerTickInterval;      // Interval in MS
                tmrWindSpeed.Enabled = true;                    // Turn on the timer

            } //end ipAddress check
        }










        // ----- FUNCTION :: Calculate the actual windspeed from inputs
        void calculateWindSpeed()
        {
            
        }


        private void tmrWindSpeed_Tick(object sender, EventArgs e)
        {
            double speed = (windSensorCount / TriggersPerSecondMPH);
            speed = Math.Round(speed, 2);

            // 1. Count rotations for 30 seconds
            // 2. Multiply # of rotation by diameter of anemometer in inches and divide by 168 = wind speed in MPH
            // 3. Multiply # of rotations by the diameter in centimeters and divide by 265  = wind speed in KPH.

            //revolutions = 178
            //diameter = 6.5 inches
            //Circumference = DataBindings * Pi
            //Circumference = 20.41 inches
            //figure out how far the anemometer travels in one rotation 20.41inches/1 X 1ft/12inches = 1.70 feet
            //how many feet travelling in one minute ==> 1.70feet/1 X 178revolutions/1minute = 302.6 feet/minute
            //302.6feet/1minute X 60min/1hr = 18,156ft/hr
            //18156feet/1hr X 1mi/5280feet = 3.44 MPH

            // v = r*w
            // v = linear speed
            // r = radius
            // w = angular speed



            lblTowerWindSpeed2.Text = windSensorCount.ToString();
            lblTowerWindSpeed2.Text += " -> " + speed + " MPH";

            windSensorCount = 0;    // Reset the counter
        }


        //Modify the sensitivity of the analog inputs. In other words, the amount that the inputs
        //must change before triggering sensorchange events.
        private void inputIKTrk_Scroll(object sender, EventArgs e)
        {
            try
            {
                for (int i = 0; i < ifKit.sensors.Count; i++)
                {
                    ifKit.sensors[i].Sensitivity = inputIKTrk.Value;
                }
                sensitivityIKTxt.Text = inputIKTrk.Value.ToString();
            }
            catch (PhidgetException ex)
            {
                MessageBox.Show(ex.Description);
            }
        }


        // This method will associate the sensorInArray with text boxes that display the current values 
        // of the analog inputs on the interface kit. It will also initialize the visibility of the
        // text boxes and analog input labeling to false.
        private void makeSensorInArray()
        {
            for (int i = 0; i < 8; i++)
            {
                ((Label)analogInputsGroupBox.Controls["analogInputLabel" + i.ToString()]).Visible = true;
                sensorInArray[i] = (TextBox)analogInputsGroupBox.Controls["textBox" + (i + 1).ToString()];
                sensorInArray[i].Visible = true;
            }
        }






        /*
         * ====================================================================================================
         * ====================== INTERFACE KIT FUNCTIONS =====================================================
         * ====================================================================================================
        */

        // ----- FUNCTION :: Manage display when phidget is disconnected
        void ifKit_Uninitialize_Display()
        {
            string colorOff = "DarkRed";
            string colorOffText = "White";

            lblTowerTemp.Text = "err";
            lblTowerHumidity.Text = "err";
            lblEnclosureTemp.Text = "err";
            grpPowerSystems.Enabled = false;
            grpAtmosphericConditions.Enabled = false;
            grpUmbilicalPower.Enabled = false;

            picBattSolar.Image = imgListBatteryLevel.Images[0];
            picBattSystem.Image = imgListBatteryLevel.Images[0];
            picBattIgnition.Image = imgListBatteryLevel.Images[0];
            picBattRocket.Image = imgListBatteryLevel.Images[0];

            txtBattSolarLevelSet.Text = 0.ToString();                  // initial minimum voltage value
            txtBattSystemLevelSet.Text = 0.ToString();                 // initial minimum voltage value
            txtBattIgnitionLevelSet.Text = 0.ToString();               // initial minimum voltage value
            txtRocketLevelSet.Text = 0.ToString();                     // initial minimum voltage value

            lblPowerSolar.Text = "ERROR: --v";
            lblPowerSystem.Text = "ERROR: --v";
            lblPowerIgnition.Text = "ERROR: --v";
            lblPowerRocket.Text = "ERROR: --v";

            btnGPIO1.BackColor = Color.FromName(colorOff);
            btnGPIO1.ForeColor = Color.FromName(colorOffText);
        }

        // ----- FUNCTION :: Manage display when phidget is connected
        void ifKit_Initialize_Display()
        {
            string colorOff = "DarkRed";
            string colorOffText = "White";

            lblTowerTemp.Text = "-- *F";
            lblTowerHumidity.Text = "-- %";
            lblEnclosureTemp.Text = "-- *F";
            grpPowerSystems.Enabled = true;
            grpAtmosphericConditions.Enabled = true;
            grpUmbilicalPower.Enabled = true;

            picBattSolar.Image = imgListBatteryLevel.Images[0];
            picBattSystem.Image = imgListBatteryLevel.Images[0];
            picBattIgnition.Image = imgListBatteryLevel.Images[0];
            picBattRocket.Image = imgListBatteryLevel.Images[0];

            txtBattSolarLevelSet.Text = minVoltageSolar.ToString();                 // initial minimum voltage value
            txtBattSystemLevelSet.Text = minVoltageBattSystem.ToString();           // initial minimum voltage value
            txtBattIgnitionLevelSet.Text = minVoltageBattIgnition.ToString();       // initial minimum voltage value
            txtRocketLevelSet.Text = minVoltageRocket.ToString();                   // initial minimum voltage value

            lblPowerSolar.Text = "INIT: 0v";
            lblPowerSystem.Text = "INIT: 0v";
            lblPowerIgnition.Text = "INIT: 0v";
            lblPowerRocket.Text = "INIT: 0v";

            btnGPIO1.BackColor = Color.FromName(colorOff);
            btnGPIO1.ForeColor = Color.FromName(colorOffText);
        }

        // ----- FUNCTION :: Handle ifKit being attached and initialized
        public void ifKit_Attach(object sender, AttachEventArgs e)
        {
            InterfaceKit ifKit = (InterfaceKit)sender;

            phidgetInterfaceFound = (ifKit.Attached) ? true : false;     // stores if phidget device found
            string msg = (phidgetInterfaceFound) ? "Phidget interface kit found" : "NO Phidget interface kit found";
            LogScreen("MSG :: " + msg);

            // ----- display various items about this IF Kit
            txtIKAttached.Text = ifKit.Attached.ToString();
            txtIKName.Text = ifKit.Name;
            txtIKSerial.Text = ifKit.SerialNumber.ToString();
            txtIKVersion.Text = ifKit.Version.ToString();
            txtIKInputDigNum.Text = ifKit.inputs.Count.ToString();
            txtIKOutputDigNum.Text = ifKit.outputs.Count.ToString();
            txtIKInputAnlgNum.Text = ifKit.sensors.Count.ToString();


            // ----- configure input sensors
            int i;
            if (ifKit.sensors.Count > 0)
            {
                // set the sensor rate
                for (i = 0; i < ifKit.sensors.Count; i++)
                {
                    /*
                    if (ifKit.ID == Phidget.PhidgetID.INTERFACEKIT_2_2_2
                        || ifKit.ID == Phidget.PhidgetID.INTERFACEKIT_8_8_8
                        || ifKit.ID == Phidget.PhidgetID.INTERFACEKIT_8_8_8_w_LCD)
                        ifKit.sensors[i].DataRate = sensorDataRate;  
                     */
                }

                // enable sensor rate change slider 
                inputIKTrk.Value = sensorDataRate;
                inputIKTrk.Visible = true;
                inputIKTrk.Enabled = true;
                sensitivityIKTxt.Text = sensorDataRate.ToString();

                try
                {
                    if (ifKit.sensors.Count > 0)
                        inputIKTrk.Value = ifKit.sensors[0].Sensitivity;
                    sensitivityIKTxt.Text = inputIKTrk.Value.ToString();
                }
                catch { }

            }

            // ----- configure digital outputs
            //ifKit.outputs[outputIndex] = outputChk.Checked;
            if (ifKit.outputs.Count > 0)
            {
                for (i = 0; i < ifKit.outputs.Count; i++)
                {
                    ifKit.outputs[i] = false;
                }

                
                cbGPIOStatus0.Checked = false;
                cbGPIOStatus1.Checked = false;
                cbGPIOStatus2.Checked = false;
                cbGPIOStatus3.Checked = false;
                cbGPIOStatus4.Checked = false;
                cbGPIOStatus5.Checked = false;
                cbGPIOStatus6.Checked = false;
                cbGPIOStatus7.Checked = false;

                //ifKit.outputs[2] = true;
            }

            // initialize form display
            ifKit_Initialize_Display();
        }

        // ----- FUNCTION :: Handle ifKit being detached
        public void ifKit_Detach(object sender, DetachEventArgs e)
        {
            InterfaceKit ifKit = (InterfaceKit)sender;

            // ----- clear various items about this IF Kit
            txtIKAttached.Text = ifKit.Attached.ToString();
            txtIKName.Text = "";
            txtIKSerial.Text = "";
            txtIKVersion.Text = "";
            txtIKInputDigNum.Text = "";
            txtIKOutputDigNum.Text = "";
            txtIKInputAnlgNum.Text = "";

            // ----- disable sensor rate change slider 
            label26.Visible = false;
            inputIKTrk.Value = 0;
            inputIKTrk.Visible = false;
            inputIKTrk.Enabled = false;

            
            cbGPIOStatus0.Checked = false;
            cbGPIOStatus1.Checked = false;
            cbGPIOStatus2.Checked = false;
            cbGPIOStatus3.Checked = false;
            cbGPIOStatus4.Checked = false;
            cbGPIOStatus5.Checked = false;
            cbGPIOStatus6.Checked = false;
            cbGPIOStatus7.Checked = false;


            //if ((advSensorForm != null) && (advSensorForm.IsDisposed == false))
            //    advSensorForm.Close();

            // uninitialize form display
            ifKit_Uninitialize_Display();
        }

        // ----- FUNCTION :: Error event handler
        public void ifKit_Error(object sender, ErrorEventArgs e)
        {
            Phidget phid = (Phidget)sender;
            DialogResult result;
            switch (e.Type)
            {
                case PhidgetException.ErrorType.PHIDGET_ERREVENT_BADPASSWORD:
                    phid.close();
                    TextInputBox dialog = new TextInputBox("Error Event",
                        "Authentication error: This server requires a password.", "Please enter the password, or cancel.");
                    result = dialog.ShowDialog();
                    if (result == DialogResult.OK)
                        openCmdLine(phid, dialog.password);
                    else
                        Environment.Exit(0);
                    break;
                case PhidgetException.ErrorType.PHIDGET_ERREVENT_PACKETLOST:
                    //Ignore this error - it's not useful in this context.
                    return;
                case PhidgetException.ErrorType.PHIDGET_ERREVENT_OVERRUN:
                    //Ignore this error - it's not useful in this context.
                    return;
                default:
                    if (!errorBox.Visible)
                        errorBox.Show();
                    break;
            }
            errorBox.addMessage(DateTime.Now.ToLongDateString() + " " + DateTime.Now.ToLongTimeString() + ": " + e.Description);
        }





        //Digital input change event handler
        //Here we check or uncheck the corresponding input checkbox based 
        //on the index of the digital input that generated the event
        public void ifKit_InputChange(object sender, InputChangeEventArgs e)
        {
            //digiInArray[e.Index].Checked = e.Value;
            //pt.Stop();



            string tmpText = e.Value.ToString();
            int newCount = (tmpText == "True") ? 1 : 0;
            windSensorCount += newCount;



        }

        //Digital output change event handler
        //Here we check or uncheck the corresponding output checkbox
        //based on the index of the output that generated the event
        public void ifKit_OutputChange(object sender, OutputChangeEventArgs e)
        {
            //digiOutDispArray[e.Index].Checked = e.Value;
        }

        //Sensor input change event handler
        //Set the textbox content based on the input index that is communicating
        //with the interface kit
        public void ifKit_SensorChange(object sender, SensorChangeEventArgs e)
        {
            sensorInArray[e.Index].Text = e.Value.ToString();

            string sensorInput = analogSensorInput[e.Index];
            double curVal, minVal, maxVal;

            switch (sensorInput)
            {
                case "voltageSolar":
                    // ----- VOLTAGE FOR SOLAR PANEL -----
                    Sensor_1135 sensorVoltage1 = new Sensor_1135();

                    curVal = sensorVoltage1.calcutateVoltage(e.Value);
                    minVal = (txtBattSolarLevelSet.Text != "" && isInt32(txtBattSolarLevelSet.Text)) ? double.Parse(txtBattSolarLevelSet.Text) : 0;
                    maxVal = maxVoltageSolar;

                    voltageModifyForm(curVal, minVal, maxVal, lblPowerSolar, picBattSolar);
                    lblPowerSolar.Text = lblPowerSolar.Text + curVal.ToString("0.###") + "V";
                    break;

                case "voltageSystem":
                    // ----- VOLTAGE FOR SYSTEM BATTERY -----
                    Sensor_1135 sensorVoltage2 = new Sensor_1135();

                    curVal = sensorVoltage2.calcutateVoltage(e.Value);
                    //minVal = double.Parse(txtBattSystemLevelSet.Text);
                    minVal = (isInt32(txtBattSystemLevelSet.Text)) ? double.Parse(txtBattSystemLevelSet.Text) : 0;
                    maxVal = maxVoltageBattSystem;

                    voltageModifyForm(curVal, minVal, maxVal, lblPowerSystem, picBattSystem);
                    lblPowerSystem.Text = lblPowerSystem.Text + curVal.ToString("0.###") + "V";
                    break;

                case "voltageIgnition":
                    // ----- VOLTAGE FOR IGNITION BATTERY -----
                    Sensor_1135 sensorVoltage3 = new Sensor_1135();

                    curVal = sensorVoltage3.calcutateVoltage(e.Value);
                    //minVal = double.Parse(txtBattIgnitionLevelSet.Text);
                    minVal = (isInt32(txtBattIgnitionLevelSet.Text)) ? double.Parse(txtBattIgnitionLevelSet.Text) : 0;
                    maxVal = maxVoltageBattIgnition;

                    voltageModifyForm(curVal, minVal, maxVal, lblPowerIgnition, picBattIgnition);
                    lblPowerIgnition.Text = lblPowerIgnition.Text + curVal.ToString("0.###") + "V";
                    break;

                case "voltageRocket":
                    // ----- VOLTAGE FOR ROCKET UMBILICAL -----
                    Sensor_1135 sensorVoltage4 = new Sensor_1135();

                    curVal = sensorVoltage4.calcutateVoltage(e.Value);
                    //minVal = double.Parse(txtRocketLevelSet.Text);
                    minVal = (isInt32(txtRocketLevelSet.Text)) ? double.Parse(txtRocketLevelSet.Text) : 0;
                    maxVal = maxVoltageRocket;

                    voltageModifyForm(curVal, minVal, maxVal, lblPowerRocket, picBattRocket);
                    lblPowerRocket.Text = lblPowerRocket.Text + curVal.ToString("0.###") + "V";
                    break;

                case "temperatureEnclosure":
                    // ----- TEMPERATURE INSIDE COMPUTER ENCLOSURE -----
                    Sensor_1124 sensorTemp1 = new Sensor_1124();
                    lblEnclosureTemp.Text = sensorTemp1.calcutateTempF(e.Value);
                    break;

                case "temperatureTower":
                    // ----- TEMPERATURE AT LAUNCH TOWER -----
                    Sensor_1125 sensorTemp2 = new Sensor_1125();
                    lblTowerTemp.Text = sensorTemp2.calcutateTempF(e.Value);
                    break;

                case "humidityTower":
                    // ----- HUMIDITY AT LAUNCH TOWER -----
                    Sensor_1125 sensorTemp3 = new Sensor_1125();
                    lblTowerHumidity.Text = sensorTemp3.calcutateHumidity(e.Value);
                    break;

                case "windSpeed":
                    break;
            }


            //if (advSensorForm != null)
            //    advSensorForm.SetValue(e.Index, e.Value);
        }






        /*
         * ====================================================================================================
         * ====================== RELAY INTERFACE KIT FUNCTIONS ===============================================
         * ====================================================================================================
        */

        // ----- FUNCTION :: Manage display when phidget is disconnected
        void relayKit_Uninitialize_Display()
        {
            string colorOff = "White";

            grpRelays.Enabled = false;
            grpRocketFire.Enabled = false;

            btnRelay1.Text = "--";         // set relay display values
            btnRelay2.Text = "--";
            btnRelay3.Text = "--";
            btnRelay4.Text = "--";

            btnRelay1.BackColor = Color.FromName(colorOff);
            btnRelay2.BackColor = Color.FromName(colorOff);
            btnRelay3.BackColor = Color.FromName(colorOff);
            btnRelay4.BackColor = Color.FromName(colorOff);

            btnRelay1.Enabled = false;
            btnRelay2.Enabled = false;
            btnRelay3.Enabled = false;
            btnRelay4.Enabled = false;

            cbRelayStatus0.Checked = false; // set relay checkbox values
            cbRelayStatus1.Checked = false;
            cbRelayStatus2.Checked = false;
            cbRelayStatus3.Checked = false;
        }

        // ----- FUNCTION :: Manage display when phidget is connected
        void relayKit_Initialize_Display()
        {
            string colorOff = "DarkRed";
            string colorOffText = "White";

            grpRelays.Enabled = true;
            grpRocketFire.Enabled = true;

            btnRelay1.Text = "OFF";         // set relay display values
            btnRelay2.Text = "OFF";
            btnRelay3.Text = "OFF";
            btnRelay4.Text = "OFF";

            btnRelay1.BackColor = Color.FromName(colorOff);
            btnRelay2.BackColor = Color.FromName(colorOff);
            btnRelay3.BackColor = Color.FromName(colorOff);
            btnRelay4.BackColor = Color.FromName(colorOff);

            btnRelay1.ForeColor = Color.FromName(colorOffText);
            btnRelay2.ForeColor = Color.FromName(colorOffText);
            btnRelay3.ForeColor = Color.FromName(colorOffText);
            btnRelay4.ForeColor = Color.FromName(colorOffText);

            btnRelay1.Enabled = true;
            btnRelay2.Enabled = true;
            btnRelay3.Enabled = true;
            btnRelay4.Enabled = true;

            cbRelayStatus0.Checked = false; // set relay checkbox values
            cbRelayStatus1.Checked = false;
            cbRelayStatus2.Checked = false;
            cbRelayStatus3.Checked = false;
        }

        // ----- FUNCTION :: Handle relayKit being attached and initialized
        void relayKit_Attach(object sender, AttachEventArgs e)
        {
            InterfaceKit relayKit = (InterfaceKit)sender;

            // stores if phidget device found - should always be TRUE if in this function
            phidgetRelayFound = (relayKit.Attached) ? true : false;
            string msg = (phidgetRelayFound) ? "Phidget relay kit found" : "NO Phidget relay kit found";
            LogScreen("MSG :: " + msg);

            // display various items about this IF Kit
            txtRKAttached.Text = relayKit.Attached.ToString();
            txtRKName.Text = relayKit.Name;
            txtRKSerial.Text = relayKit.SerialNumber.ToString();
            txtRKVersion.Text = relayKit.Version.ToString();
            txtRKInputDigNum.Text = relayKit.inputs.Count.ToString();
            txtRKOutputDigNum.Text = relayKit.outputs.Count.ToString();
            
            // initialize form display
            relayKit_Initialize_Display();
        }

        // ----- FUNCTION :: Handle relayKit being detached
        void relayKit_Detach(object sender, DetachEventArgs e)
        {
            InterfaceKit relayKit = (InterfaceKit)sender;

            // stores if phidget device found - should always be FALSE if in this function
            phidgetRelayFound = (relayKit.Attached) ? true : false;
            string msg = (phidgetRelayFound) ? "Phidget relay kit found" : "NO Phidget relay kit found";
            LogScreen("MSG :: " + msg);

            // clear various items about this IF Kit
            txtRKAttached.Text = relayKit.Attached.ToString();
            txtRKName.Text = "";
            txtRKSerial.Text = "";
            txtRKVersion.Text = "";
            txtRKInputDigNum.Text = "";
            txtRKOutputDigNum.Text = "";

            // uninitialize form display
            relayKit_Uninitialize_Display();
        }

        // ----- FUNCTION :: Error event handler
        void relayKit_Error(object sender, ErrorEventArgs e)
        {
            Phidget phid = (Phidget)sender;
            DialogResult result;
            switch (e.Type)
            {
                case PhidgetException.ErrorType.PHIDGET_ERREVENT_BADPASSWORD:
                    phid.close();
                    TextInputBox dialog = new TextInputBox("Error Event",
                        "Authentication error: This server requires a password.", "Please enter the password, or cancel.");
                    result = dialog.ShowDialog();
                    if (result == DialogResult.OK)
                        openCmdLine(phid, dialog.password);
                    else
                        Environment.Exit(0);
                    break;
                case PhidgetException.ErrorType.PHIDGET_ERREVENT_PACKETLOST:
                    //Ignore this error - it's not useful in this context.
                    return;
                case PhidgetException.ErrorType.PHIDGET_ERREVENT_OVERRUN:
                    //Ignore this error - it's not useful in this context.
                    return;
                default:
                    if (!errorBox.Visible)
                        errorBox.Show();
                    break;
            }
            errorBox.addMessage(DateTime.Now.ToLongDateString() + " " + DateTime.Now.ToLongTimeString() + ": " + e.Description);
        }

        // ----- FUNCTION :: Handle a digital input change
        void relayKit_InputChange(object sender, InputChangeEventArgs e)
        {
            //digiInArray[e.Index].Checked = e.Value;
        }

        // ----- FUNCTION :: Handle a digital output change
        void relayKit_OutputChange(object sender, OutputChangeEventArgs e)
        {
            //digiOutDispArray[e.Index].Checked = e.Value;
        }


        //Modify the digital ouputs
        //From the properties window in the form designer, each of the CheckedChanged events for output 
        //checkboxes point to this event handler. The "tag" property for each check box stores user defined 
        //data associated with the control and has been used here to relate the box with an output index.
        private void CheckedChanged(object sender, EventArgs e)
        {
            CheckBox outputChk = (CheckBox)sender;

            int outputIndex = int.Parse((string)outputChk.Tag);

            ifKit.outputs[outputIndex] = outputChk.Checked;
        }

        //Sensor input change event handler
        //Set the textbox content based on the input index that is communicating
        //with the interface kit
        void relayKit_SensorChange(object sender, SensorChangeEventArgs e)
        {
            sensorInArray[e.Index].Text = e.Value.ToString();

            string sensorInput = analogSensorInput[e.Index];
            double curVal, minVal, maxVal;

            switch (sensorInput)
            {
                case "voltageSolar":
                    // ----- VOLTAGE FOR SOLAR PANEL -----
                    Sensor_1135 sensorVoltage1 = new Sensor_1135();

                    curVal = sensorVoltage1.calcutateVoltage(e.Value);
                    minVal = double.Parse(txtBattSolarLevelSet.Text);
                    maxVal = maxVoltageSolar;

                    voltageModifyForm(curVal, minVal, maxVal, lblPowerSolar, picBattSolar);
                    lblPowerSolar.Text = lblPowerSolar.Text + curVal.ToString("0.###") + "V";
                    break;

                case "voltageSystem":
                    // ----- VOLTAGE FOR SYSTEM BATTERY -----
                    Sensor_1135 sensorVoltage2 = new Sensor_1135();

                    curVal = sensorVoltage2.calcutateVoltage(e.Value);
                    minVal = double.Parse(txtBattSystemLevelSet.Text);
                    maxVal = maxVoltageBattSystem;

                    voltageModifyForm(curVal, minVal, maxVal, lblPowerSystem, picBattSystem);
                    lblPowerSystem.Text = lblPowerSystem.Text + curVal.ToString("0.###") + "V";
                    break;

                case "voltageIgnition":
                    // ----- VOLTAGE FOR IGNITION BATTERY -----
                    Sensor_1135 sensorVoltage3 = new Sensor_1135();

                    curVal = sensorVoltage3.calcutateVoltage(e.Value);
                    minVal = double.Parse(txtBattIgnitionLevelSet.Text);
                    maxVal = maxVoltageBattIgnition;

                    voltageModifyForm(curVal, minVal, maxVal, lblPowerIgnition, picBattIgnition);
                    lblPowerIgnition.Text = lblPowerIgnition.Text + curVal.ToString("0.###") + "V";
                    break;

                case "voltageRocket":
                    // ----- VOLTAGE FOR ROCKET UMBILICAL -----
                    Sensor_1135 sensorVoltage4 = new Sensor_1135();

                    curVal = sensorVoltage4.calcutateVoltage(e.Value);
                    minVal = double.Parse(txtRocketLevelSet.Text);
                    maxVal = maxVoltageRocket;

                    voltageModifyForm(curVal, minVal, maxVal, lblPowerRocket, picBattRocket);
                    lblPowerRocket.Text = lblPowerRocket.Text + curVal.ToString("0.###") + "V";
                    break;

                case "temperatureEnclosure":
                    // ----- TEMPERATURE INSIDE COMPUTER ENCLOSURE -----
                    Sensor_1124 sensorTemp1 = new Sensor_1124();
                    lblEnclosureTemp.Text = sensorTemp1.calcutateTempF(e.Value);
                    break;

                case "temperatureTower":
                    // ----- TEMPERATURE AT LAUNCH TOWER -----
                    Sensor_1125 sensorTemp2 = new Sensor_1125();
                    lblTowerTemp.Text = sensorTemp2.calcutateTempF(e.Value);
                    break;

                case "humidityTower":
                    // ----- HUMIDITY AT LAUNCH TOWER -----
                    Sensor_1125 sensorTemp3 = new Sensor_1125();
                    lblTowerHumidity.Text = sensorTemp3.calcutateHumidity(e.Value);
                    break;

                case "windSpeed":
                    break;
            }


            //if (advSensorForm != null)
            //    advSensorForm.SetValue(e.Index, e.Value);
        }


        //This method will associate the digiOutArray with check boxes that control the state of the
        //digital outputs on the interface kit. It will also associate the digiOutDispArray with check
        //boxes that represent the state of the outputs as reported on the interfacekit, and initialize 
        //the visibility of the check boxes and labeling to false.
        private void makeDigiOutArray()
        {
            for (int i = 0; i < 16; i++)
            {
                /*
                ((Label)digitalOutputsGroupBox.Controls["digitalOutputLabel" + i.ToString()]).Visible = false;
                digiOutArray[i] = (CheckBox)digitalOutputsGroupBox.Controls["checkBox" + (i + 17).ToString()];
                digiOutArray[i].Visible = false;
                digiOutDispArray[i] = (CheckBox)digitalOutputsGroupBox.Controls["checkBoxReport" + i.ToString()];
                digiOutDispArray[i].Visible = false;
                */
            }
        }






        /*
         * ====================================================================================================
         * ====================== ENCODER FUNCTIONS ===========================================================
         * ====================================================================================================
        */

        // ----- FUNCTION :: Manage display when phidget is disconnected
        void encoder_Uninitialize_Display()
        {
            lblTowerWindSpeed.Text = "err";
            lblTowerWindDirection.Text = "err";
        }

        // ----- FUNCTION :: Manage display when phidget is connected
        void encoder_Initialize_Display()
        {
            lblTowerWindSpeed.Text = "-- MPH";
            lblTowerWindDirection.Text = "--* N";
        }

        // ----- FUNCTION :: Handle rotary encoder being attached and initialized
        void encoder_Attach(object sender, AttachEventArgs e)
        {

            Phidgets.Encoder encoderX = (Phidgets.Encoder)sender;

            phidgetEncoderFound = (encoder.Attached) ? true : false;     // stores if phidget device found
            string msg = (phidgetEncoderFound) ? "Phidget rotary encoder found" : "NO Phidget rotary encoder found";
            LogScreen("MSG :: " + msg);

            // ----- display various items about this IF Kit
            txtENCAttached.Text     = encoderX.Attached.ToString();
            txtENCName.Text         = encoderX.Name;
            txtENCSerial.Text       = encoderX.SerialNumber.ToString();
            txtENCVersion.Text      = encoderX.Version.ToString();

            switch (encoderX.ID)
            {
                case Phidget.PhidgetID.ENCODER_HS_4ENCODER:                    
                    lblENCTimeChange.Text = "Time since last change (μs):";
                    break;
                case Phidget.PhidgetID.ENCODER_HS_1ENCODER:
                case Phidget.PhidgetID.ENCODER_1ENCODER_1INPUT:
                    lblENCTimeChange.Text = "Time since last change (ms):";
                    
                    break;
                default:
                    break;
            }

            // initialize form display
            encoder_Initialize_Display();
        }

        // ----- FUNCTION :: Handle rotary encoder being detached
        void encoder_Detach(object sender, DetachEventArgs e)
        {
            Phidgets.Encoder encoderX = (Phidgets.Encoder)sender;

            // display various items about this IF Kit
            txtENCAttached.Text             = encoderX.Attached.ToString();
            txtENCName.Text                 = "";
            txtENCSerial.Text               = "";
            txtENCVersion.Text              = "";
            txtENCTimeSinceLastChange.Text  = "";
            txtENCPosition.Text             = "";

            // uninitialize form display
            encoder_Uninitialize_Display();
        }

        // ----- FUNCTION :: Error event handler
        void encoder_Error(object sender, ErrorEventArgs e)
        {
            Phidget phid = (Phidget)sender;
            DialogResult result;
            switch (e.Type)
            {
                case PhidgetException.ErrorType.PHIDGET_ERREVENT_BADPASSWORD:
                    phid.close();
                    TextInputBox dialog = new TextInputBox("Error Event",
                        "Authentication error: This server requires a password.", "Please enter the password, or cancel.");
                    result = dialog.ShowDialog();
                    if (result == DialogResult.OK)
                        openCmdLine(phid, dialog.password);
                    else
                        Environment.Exit(0);
                    break;
                default:
                    if (!errorBox.Visible)
                        errorBox.Show();
                    break;
            }
            errorBox.addMessage(DateTime.Now.ToLongDateString() + " " + DateTime.Now.ToLongTimeString() + ": " + e.Description);
        }

        // ----- FUNCTION :: Handle input change (pushbutton in the knob)
        void encoder_InputChange(object sender, InputChangeEventArgs e)
        {
            // Event arguements contain the input index (on current Phidget Encoders will only be 1) and the value, 
            // a bool to represent clicked or unlcicked state
            
            //((CheckBox)inputArray[e.Index]).Checked = e.Value;
        }

        // ----- FUNCTION :: Handle encoder position change (rotation of knob)
        void encoder_PositionChange(object sender, EncoderPositionChangeEventArgs e)
        {
            //Encoder Position Change event handler...the event arguements will provide the encoder index, value, and 
            //the elapsed time since the last event.  These value, including the current position value stored in the
            //corresponding element in the encoder objects encoder collection could be used to calculate velocity...
            
            int index = 0; // (int)encoderCmb.SelectedItem;
            if (index == e.Index)
            {
                txtENCPosition.Text = e.PositionChange.ToString();

                try
                {
                    txtENCTimeSinceLastChange.Text = e.Time.ToString();
                }
                catch
                {
                    txtENCTimeSinceLastChange.Text = "Unknown";
                }
                txtENCPosition.Text = encoder.encoders[e.Index].ToString();

                // Velocity calculated in counts per second - averaged over 50 samples
                double veloc = 0;
                try
                {
                    switch (encoder.ID)
                    {
                        case Phidget.PhidgetID.ENCODER_1ENCODER_1INPUT:
                        case Phidget.PhidgetID.ENCODER_HS_1ENCODER:
                            veloc = (((double)e.PositionChange * 1000) / ((double)e.Time));
                            break;
                        case Phidget.PhidgetID.ENCODER_HS_4ENCODER:
                            veloc = (((double)e.PositionChange * 1000000) / ((double)e.Time));
                            break;
                    }
                }
                catch
                { }
                

            }
        }






        /*
         * ====================================================================================================
         * ====================== PARSE COMMAND LINE ARGUMENT FUNCTIONS =======================================
         * ====================================================================================================
        */
        
        #region Command line open functions
        private void openCmdLine(Phidget p)
        {
            openCmdLine(p, null);
        }
        private void openCmdLine(Phidget p, String pass)
        {
            int serial = -1;
            int port = phidgetServerPortNumber;
            String host = null;
            bool remote = false, remoteIP = false;
            string[] args = Environment.GetCommandLineArgs();
            String appName = args[0];

            try
            { //Parse the flags
                for (int i = 1; i < args.Length; i++)
                {
                    if (args[i].StartsWith("-"))
                        switch (args[i].Remove(0, 1).ToLower())
                        {
                            case "n":
                                serial = int.Parse(args[++i]);
                                break;
                            case "r":
                                remote = true;
                                break;
                            case "s":
                                remote = true;
                                host = args[++i];
                                break;
                            case "p":
                                pass = args[++i];
                                break;
                            case "i":
                                remoteIP = true;
                                host = args[++i];
                                if (host.Contains(":"))
                                {
                                    port = int.Parse(host.Split(':')[1]);
                                    host = host.Split(':')[0];
                                }
                                break;
                            default:
                                goto usage;
                        }
                    else
                        goto usage;
                }

                if (remoteIP)
                    p.open(serial, host, port, pass);
                else if (remote)
                    p.open(serial, host, pass);
                else
                    p.open(serial);
                return; //success
            }
            catch { }
        usage:
            StringBuilder sb = new StringBuilder();
            sb.AppendLine("Invalid Command line arguments." + Environment.NewLine);
            sb.AppendLine("Usage: " + appName + " [Flags...]");
            sb.AppendLine("Flags:\t-n   serialNumber\tSerial Number, omit for any serial");
            sb.AppendLine("\t-r\t\tOpen remotely");
            sb.AppendLine("\t-s   serverID\tServer ID, omit for any server");
            sb.AppendLine("\t-i   ipAddress:port\tIp Address and Port. Port is optional, defaults to 5001");
            sb.AppendLine("\t-p   password\tPassword, omit for no password" + Environment.NewLine);
            sb.AppendLine("Examples: ");
            sb.AppendLine(appName + " -n 50098");
            sb.AppendLine(appName + " -r");
            sb.AppendLine(appName + " -s myphidgetserver");
            sb.AppendLine(appName + " -n 45670 -i 127.0.0.1:5001 -p paswrd");
            MessageBox.Show(sb.ToString(), "Argument Error", MessageBoxButtons.OK, MessageBoxIcon.Error);

            Application.Exit();
        }
        #endregion

        




        /*
         * ====================================================================================================
         * ====================== CUSTOM FUNCTIONS ============================================================
         * ====================================================================================================
        */

        // ----- FUNCTION :: Write message to the on-screen log textbox
        public void LogScreen(string MSG)
        {
            if (MSG != "" && txtLogToScreen != null)
            {
                // create the log message string
                string message = MSG;
                string newline = (txtLogToScreen.Text != "") ? Environment.NewLine : "";        // figure out newline character
                
                // output log message to the program screen
                txtLogToScreen.Text += newline + message;                                       // put message in textbox
                txtLogToScreen.SelectionStart = txtLogToScreen.Text.Length;                     // get length of box
                txtLogToScreen.ScrollToCaret();                                                 // scroll to bottom of textbox
                
                // output log message to the program file (crash analysis)
                TextFromFile ZtxtObj = new TextFromFile();                                      // instantiate the textfile class
                bool result = ZtxtObj.appendFile(outputFileStatus, message);                    // open and write the file
            }
        }

        // ----- FUNCTION :: Determine if string is actually an integer
        private bool isInt32(string checkString)
        {
            // check if string passed in is actually an integer
            int checkVal;

            try
            {
                checkVal = Convert.ToInt32(txtPortAddress.Text);
                return true;
            }
            catch (FormatException e)
            {
                return false;
            }
            catch (OverflowException e)
            {
                return false;
            }
        }

        




        /*
         * ====================================================================================================
         * ====================== PHIDGET INITIALIZATION FUNCTIONS ============================================
         * ====================================================================================================
        */

        // ----- FUNCTION :: Initialize phidget encoder device and attach events
        private void InitializePhidgetEncoder()
        {
            // ----- INITIALIZE THE ROTARY ENCODER -----
            if (phidgetEncoderFound)
            {
                MessageBox.Show("ERROR :: Phidget encoder already attached. To connect - please restart program");
                LogScreen("ERROR :: Phidget encoder already attached. To connect - please restart program");
            }
            else
            {
                try
                {
                    LogScreen("Attempting to initialize phidget rotary encoder");

                    // initialize the encoder
                    encoder = new Phidgets.Encoder();
                    encoder.open(serialNumEncoder1);

                    // attach events to the encoder
                    encoder.Attach += new AttachEventHandler(encoder_Attach);   // Set the attach handler
                    encoder.Detach += new DetachEventHandler(encoder_Detach);   // Set the detach handler
                    encoder.Error += new ErrorEventHandler(encoder_Error);      // Set the error handler
                    encoder.InputChange += new InputChangeEventHandler(encoder_InputChange);                    // Set the input change handler
                    encoder.PositionChange += new EncoderPositionChangeEventHandler(encoder_PositionChange);    // Set the position change handler

                    openCmdLine(encoder);                       // Open the Phidget using the command line arguments
                }
                catch (PhidgetException ex)
                {
                    MessageBox.Show(ex.ToString()); // throw phidget errors
                }
            }
        }

        // ----- FUNCTION :: Initialize phidget interface device and attach events
        private void InitializePhidgetInterface()
        {
            // ----- INITIALIZE THE INTERFACE KIT -----
            if (phidgetInterfaceFound)
            {
                MessageBox.Show("ERROR :: Phidget interface already attached. To connect - please restart program");
                LogScreen("ERROR :: Phidget interface already attached. To connect - please restart program");
            }
            else
            {
                try
                {
                    LogScreen("Attempting to initialize phidget interface kit");

                    // initialize the ifKit
                    ifKit = new InterfaceKit();
                    ifKit.open(serialNuminterface1, phidgetServerIpAddress, phidgetServerPortNumber, phidgetServerPassword);

                    // attach events to the ifKit
                    ifKit.Attach += new AttachEventHandler(ifKit_Attach);
                    ifKit.Detach += new DetachEventHandler(ifKit_Detach);
                    ifKit.Error += new ErrorEventHandler(ifKit_Error);
                    ifKit.InputChange += new InputChangeEventHandler(ifKit_InputChange);
                    ifKit.OutputChange += new OutputChangeEventHandler(ifKit_OutputChange);
                    ifKit.SensorChange += new SensorChangeEventHandler(ifKit_SensorChange);

                    openCmdLine(ifKit);                         // Open the Phidget using the command line arguments
                }
                catch (PhidgetException ex)
                {
                    MessageBox.Show(ex.ToString()); // throw phidget errors
                }
            }
        }

        // ----- FUNCTION :: Initialize phidget relay device and attach events
        private void InitializePhidgetRelay()
        {
            // ----- INITIALIZE THE RELAY INTERFACE KIT -----
            if (phidgetRelayFound)
            {
                MessageBox.Show("ERROR :: Phidget relay already attached. To connect - please restart program");
                LogScreen("ERROR :: Phidget relay already attached. To connect - please restart program");
            }
            else
            {
                try
                {
                    LogScreen("Attempting to initialize phidget relay");

                    // initialize the relayKit
                    relayKit = new InterfaceKit();
                    //relayKit = new RelayKit();
                    relayKit.open(serialNumRelay1, phidgetServerIpAddress, phidgetServerPortNumber, phidgetServerPassword);

                    // attach events to the relayKit
                    relayKit.Attach += new AttachEventHandler(relayKit_Attach);
                    relayKit.Detach += new DetachEventHandler(relayKit_Detach);
                    relayKit.Error += new ErrorEventHandler(relayKit_Error);
                    relayKit.InputChange += new InputChangeEventHandler(relayKit_InputChange);
                    relayKit.OutputChange += new OutputChangeEventHandler(relayKit_OutputChange);
                    relayKit.SensorChange += new SensorChangeEventHandler(relayKit_SensorChange);

                    openCmdLine(relayKit);                      // Open the Phidget using the command line arguments
                }
                catch (PhidgetException ex)
                {
                    MessageBox.Show(ex.ToString());
                }
            }
        }

        




        /*
         * ====================================================================================================
         * ====================== HOLDING FUNCTIONS OUT OF THE WAY ============================================
         * ====================================================================================================
        */

        // ----- FUNCTION :: Handle form elements when connected to the network
        private void NetworkDisplayConnected()
        {
            btnConnectPhidgets.Enabled = false;
            btnConnectPhidgets.Visible = false;

            btnDisconnectPhidgets.Enabled = true;
            btnDisconnectPhidgets.Visible = true;

            txtIPAddress.Enabled = false;
            txtPortAddress.Enabled = false;
            txtServerPassword.Enabled = false;

            this.BackColor = Color.FromName("LightGreen"); //Control
            //tabControl1.
            LogScreen("Network connection established.");
        }

        // ----- FUNCTION :: Handle form elements when disconnected from the network
        private void NetworkDisplayDisconnected()
        {
            btnConnectPhidgets.Enabled = true;
            btnConnectPhidgets.Visible = true;

            btnDisconnectPhidgets.Enabled = false;
            btnDisconnectPhidgets.Visible = false;

            txtIPAddress.Enabled = true;
            txtPortAddress.Enabled = true;
            txtServerPassword.Enabled = true;

            this.BackColor = Color.FromName("DarkRed");
            LogScreen("Network connection disconnected.");
        }

        // ----- FUNCTION :: Disconnect from all phidget devices
        private void PhidgetsDisconnect()
        {
            // ----- Unhook the event handlers for encoder
            if (encoder != null)
            {
                LogScreen("Disconnecting Phidget rotary encoder.");
                encoder.Attach -= new AttachEventHandler(encoder_Attach);
                encoder.Detach -= new DetachEventHandler(encoder_Detach);
                encoder.Error -= new ErrorEventHandler(encoder_Error);
                encoder.PositionChange -= new EncoderPositionChangeEventHandler(encoder_PositionChange);
                encoder.InputChange -= new InputChangeEventHandler(encoder_InputChange);

                encoder.close();
                encoder = null;
            }

            // ----- Unhook the event handlers for interface kit
            if (ifKit != null)
            {
                LogScreen("Disconnecting Phidget interface kit.");
                ifKit.Attach -= new AttachEventHandler(ifKit_Attach);
                ifKit.Detach -= new DetachEventHandler(ifKit_Detach);
                ifKit.InputChange -= new InputChangeEventHandler(ifKit_InputChange);
                ifKit.OutputChange -= new OutputChangeEventHandler(ifKit_OutputChange);
                ifKit.SensorChange -= new SensorChangeEventHandler(ifKit_SensorChange);
                ifKit.Error -= new ErrorEventHandler(ifKit_Error);

                ifKit.close();
                ifKit = null;
            }

            // ----- Unhook the event handlers for relay interface kit
            if (relayKit != null)
            {
                LogScreen("Disconnecting Phidget relay kit.");
                relayKit.Attach -= new AttachEventHandler(relayKit_Attach);
                relayKit.Detach -= new DetachEventHandler(relayKit_Detach);
                relayKit.InputChange -= new InputChangeEventHandler(relayKit_InputChange);
                relayKit.OutputChange -= new OutputChangeEventHandler(relayKit_OutputChange);
                relayKit.SensorChange -= new SensorChangeEventHandler(relayKit_SensorChange);
                relayKit.Error -= new ErrorEventHandler(relayKit_Error);

                relayKit.close();
                relayKit = null;
            }

            LogScreen("Phidget disconnect complete.");
        }

        // ----- FUNCTION :: Change the form dispaly for a changing voltage
        private void voltageModifyForm(double curVal, double minVal, double maxVal, Label frmLabel, PictureBox frmPicture)
        {
            string colorBattOn = "DarkGreen";
            string colorBattLow = "DarkOrange";
            string colorBattOff = "DarkRed";

            string tmpColor, tmpText;
            int tmpImageIndex;

            if (curVal > minVal && curVal <= maxVal)
            {
                // - good battery level -
                tmpColor = colorBattOn;
                tmpText = "Curr: ";
                tmpImageIndex = 2;
            }
            else if (curVal <= minVal && curVal > 0)
            {
                // - low battery level -
                tmpColor = colorBattLow;
                tmpText = "Low: ";
                tmpImageIndex = 1;
            }
            else
            {
                // - error -
                tmpColor = colorBattOff;
                tmpText = "ERROR: 0V";
                tmpImageIndex = 0;
            }

            frmLabel.Text = tmpText;
            frmLabel.ForeColor = Color.FromName(tmpColor);
            frmPicture.Image = imgListBatteryLevel.Images[tmpImageIndex];
            frmPicture.Height = 130;
            frmPicture.Width = 130;

        }

        private void button1_Click(object sender, EventArgs e)
        {
            string message = "test line";
            string newline = (txtLogToScreen.Text != "") ? Environment.NewLine : "";        // figure out newline character
            string output = message;                                              // set the message
            
            // output log message to the program file (crash analysis)
            TextFromFile ZtxtObj = new TextFromFile();                                      // instantiate the textfile class
            bool result = ZtxtObj.appendFile(outputFileStatus, output);                     // open and write the file


        }


        public void initializeLogfile()
        {
            // create the filename based on current time
            string filenamePath = "c:\\";
            string filenamePre = "logfile";
            string filenameExt = ".txt";
            string datetime = string.Format("{0:yyyy-MM-dd_hh-mm-ss-tt}", DateTime.Now);
            outputFileSensor = filenamePath + filenamePre + "_" + datetime + filenameExt;

            // create the logfile
            string output = "timestamp, temp, humidity, wind direction, wind speed, temp electronics, pwr-solar, pwr-system, pwr-ignition, pwr-rocket, status-fire, relay-umbilical, relay-light, relay-siren, relay-other";
            TextFromFile ZtxtObj = new TextFromFile();                                      // instantiate the textfile class
            bool result = ZtxtObj.appendFile(outputFileSensor, output);                     // open and write the file
        }


        public void initializePhidgetValueDictionary()
        {
            // FUNCTION :: initialize the dictionaty holding phidget log values
            phidgetValues.Add("temperature-air", -1);
            phidgetValues.Add("humidity-air", -1);
            phidgetValues.Add("wind-direction", -1);
            phidgetValues.Add("wind-speed", -1);
            phidgetValues.Add("temperature-electronics", -1);
            phidgetValues.Add("power-solar", -1);
            phidgetValues.Add("power-system", -1);
            phidgetValues.Add("power-ignition", -1);
            phidgetValues.Add("power-rocket", -1);
            phidgetValues.Add("status-fire", -1);
            phidgetValues.Add("relay-umbilical", -1);
            phidgetValues.Add("relay-light", -1);
            phidgetValues.Add("relay-siren", -1);
            phidgetValues.Add("relay-other", -1);
        }

        public void timerLogfileInitialize()
        {
            // FUNCTION :: initialize the logfile timer

            tmrLogfile.Interval = 1000;     // time interval in milliseconds
            tmrLogfile.Enabled = true;      // enable the timer
        }

        private void tmrLogfile_Tick(object sender, EventArgs e)
        {
            // FUNCTION :: timer has incremented - write log

            string output = "";
            float value = 0;
            string datetime = string.Format("{0:yyyy-MM-dd_hh-mm-ss-tt}",DateTime.Now);

            /*
            DATETIME FORMATTING
            y (year), M (month), d (day), h (hour 12), H (hour 24), m (minute), s (second), f (second fraction), F (second fraction, trailing zeroes are trimmed), t (P.M or A.M) and z (time zone).
            */
            
            /*
            LOGFILE LINE
            timestamp, temp, humidity, wind direction, wind speed, temp electronics, pwr-solar, pwr-system, pwr-ignition, pwr-rocket, status-fire, relay-umbilical, relay-light, relay-siren, relay-other
            */
            
            
            // create the logfile line for output
            output += datetime;
            output += (phidgetValues.TryGetValue("temperature-air", out value)) ? "," + value.ToString() : "," + 0.ToString();
            value = 0;
            output += (phidgetValues.TryGetValue("humidity-air", out value)) ? "," + value.ToString() : "," + 0.ToString();
            value = 0;
            output += (phidgetValues.TryGetValue("wind-direction", out value)) ? "," + value.ToString() : "," + 0.ToString();
            value = 0;
            output += (phidgetValues.TryGetValue("wind-speed", out value)) ? "," + value.ToString() : "," + 0.ToString();
            value = 0; 
            output += (phidgetValues.TryGetValue("temperature-electronics", out value)) ? "," + value.ToString() : "," + 0.ToString();
            value = 0; 
            output += (phidgetValues.TryGetValue("power-solar", out value)) ? "," + value.ToString() : "," + 0.ToString();
            value = 0; 
            output += (phidgetValues.TryGetValue("power-system", out value)) ? "," + value.ToString() : "," + 0.ToString();
            value = 0; 
            output += (phidgetValues.TryGetValue("power-ignition", out value)) ? "," + value.ToString() : "," + 0.ToString();
            value = 0; 
            output += (phidgetValues.TryGetValue("power-rocket", out value)) ? "," + value.ToString() : "," + 0.ToString();
            value = 0; 
            output += (phidgetValues.TryGetValue("status-fire", out value)) ? "," + value.ToString() : "," + 0.ToString();
            value = 0; 
            output += (phidgetValues.TryGetValue("relay-umbilical", out value)) ? "," + value.ToString() : "," + 0.ToString();
            value = 0; 
            output += (phidgetValues.TryGetValue("relay-light", out value)) ? "," + value.ToString() : "," + 0.ToString();
            value = 0; 
            output += (phidgetValues.TryGetValue("relay-siren", out value)) ? "," + value.ToString() : "," + 0.ToString();
            value = 0; 
            output += (phidgetValues.TryGetValue("relay-other", out value)) ? "," + value.ToString() : "," + 0.ToString();
            value = 0;

            // output log message to the program file (crash analysis)
            TextFromFile ZtxtObj = new TextFromFile();                                      // instantiate the textfile class
            bool result = ZtxtObj.appendFile(outputFileSensor, output);                     // open and write the file

        }



    } //end class
} //end namespace