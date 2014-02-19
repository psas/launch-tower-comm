# install_twisted_rector must be called before importing
# and using the reactor
from kivy.support import install_twisted_reactor
install_twisted_reactor()


from twisted.internet import reactor
from twisted.protocols.basic import LineOnlyReceiver
from twisted.internet.protocol import Factory


class EchoProtocol(LineOnlyReceiver):
    '''This handles communication. Passes messages to the Kivy app
    for processing.  Leave logic out of here.
    '''

    def connectionMade(self):
        self.factory.app.on_connection(self.transport, self.sendLine)

    def lineReceived(self, line):
        # Acknowledge
        self.sendLine('Got it.')
        # Process message
        response = self.factory.app.handle_message(line)
        if response:
            self.sendLine(response)


class EchoFactory(Factory):
    protocol = EchoProtocol

    def __init__(self, app):
        self.app = app

import random
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.config import Config
Config.set('graphics', 'width', '400')
Config.set('graphics', 'height', '300')


class TwistedServerApp(App):
    connection = None

    def build(self):
        self.label = Label(text="server started\n")
        self.button = Button(text="Set Remote State")
        self.button.bind(on_press=self.send_command)
        self.layout = BoxLayout(orientation='vertical')
        self.layout.add_widget(self.label)
        self.layout.add_widget(self.button)
        reactor.listenTCP(8000, EchoFactory(self))
        return self.layout

    def on_connection(self, connection, sender):
        self.connection = connection
        self.send = sender

    def handle_message(self, msg):
        print "message received"

        if '200' in msg:
            self.handle_confirmation(msg)
        elif 'alive' in msg:
            self.handle_heartbeat(msg)
        else:
            self.label.text += "responded: %s\n" % msg
            return msg

    def handle_confirmation(self, msg):
        self.label.text += 'Command Received.\n'

    def send_command(self, instance):
        state = random.randint(1, 10)
        self.send(" ".join(["SET STATE", str(state)]))

    def handle_heartbeat(self, msg):
        self.label.text += 'Still Alive.\n'

if __name__ == '__main__':
    TwistedServerApp().run()
