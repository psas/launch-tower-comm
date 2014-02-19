#install_twisted_rector must be called before importing the reactor
from kivy.support import install_twisted_reactor
install_twisted_reactor()

#A simple Client that send messages to the echo server
from twisted.internet import reactor, protocol
from twisted.protocols.basic import LineOnlyReceiver


class EchoClient(LineOnlyReceiver):
    def connectionMade(self):
        self.factory.app.on_connection(self.transport, self.sendLine)

    def lineReceived(self, msg):
        response = self.factory.app.handle_message(msg)
        if response:
            self.sendLine(response)


class EchoFactory(protocol.ClientFactory):
    protocol = EchoClient

    def __init__(self, app):
        self.app = app

    def clientConnectionLost(self, conn, reason):
        self.app.print_message("connection lost")
        self.app.connection = False
        self.app.send = None

    def clientConnectionFailed(self, conn, reason):
        self.app.print_message("connection failed")


from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.config import Config
Config.set('graphics', 'width', '400')
Config.set('graphics', 'height', '300')

# A simple kivy App, with a textbox to enter messages, and
# a large label to display all the messages received from
# the server


class TwistedClientApp(App):
    connection = None

    def build(self):
        root = self.setup_gui()
        self.connect_to_server()
        return root

    def setup_gui(self):
        self.textbox = TextInput(size_hint_y=.1, multiline=False)
        self.textbox.bind(on_text_validate=self.send_message)
        self.label = Label(text='connecting...\n')
        self.comm = BoxLayout(orientation='vertical')
        self.comm.add_widget(self.label)
        self.comm.add_widget(self.textbox)

        self.indicator = Label(text='System State\n')

        self.layout = BoxLayout(orientation='horizontal')
        self.layout.add_widget(self.indicator)
        self.layout.add_widget(self.comm)
        return self.layout

    def connect_to_server(self):
        reactor.connectTCP('localhost', 8000, EchoFactory(self))

    def on_connection(self, connection, send_function):
        self.print_message("connected succesfully!")
        self.connection = connection
        self.send = send_function

    def send_message(self, *args):
        msg = self.textbox.text
        if msg and self.connection:
            self.send(str(self.textbox.text))
            self.textbox.text = ""
        if not self.connection:
            self.connect_to_server()
            self.label.text += "Please try again." + "\n"

    def handle_message(self, msg):
        self.label.text += msg + "\n"
        print "handle_message called"
        if 'SET' in msg:
            response = self.handle_command(msg)
            return response

    def handle_command(self, msg):
        if 'SET' in msg:
            print "handling command"
            try:
                self.indicator.text = "SYSTEM:" + msg.split()[2]
                return "200"
            except:
                self.label.text += "Malformed message received." + "\n"
                return "Error 400"

    def print_message(self, msg):
        self.label.text += msg + "\n"

if __name__ == '__main__':
    TwistedClientApp().run()
