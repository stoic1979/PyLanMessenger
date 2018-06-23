#
# UDP message handler
#
# It emits/sends messages recevied via nw to UI
#
import _thread as thread
import socket
from PyQt5.QtCore import QObject, pyqtSignal

from settings import *


class MessageHandler(QObject):

    # define signal to inform UI about a received message
    message_received = pyqtSignal('QString')

    def __init__(self):
        super(MessageHandler, self).__init__()

        self.start_msg_receiver()

    def start_msg_receiver(self):
        """
        function starts a thread to receive messages
        """
        try:
            thread.start_new_thread(
                    self.monitor_messages, ("MsgRecvThread", 2, ))
        except Exception as exp:
            print("Error: unable to start message recevier thread")
            print(exp)

    def monitor_messages(self, thread_name, delay):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('', UDP_PORT))

        while True:
            # buffer size is 1024 bytes
            org_data, addr = sock.recvfrom(1024)
            data = org_data.decode("utf-8")

            print("[MessageHandler] :: received message:", data)
            self.message_received.emit(data)
