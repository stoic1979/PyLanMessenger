#!/usr/bin/python3

"""
 PyLanMessenger
 ______________

 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program.  If not, see <http://www.gnu.org/licenses/>.

 Project Author/Architect: Navjot Singh <weavebytes@gmail.com>

"""

#
# UDP message listener
#
# It emits/sends messages recevied via nw to UI
#
import _thread as thread
import socket
from PyQt5.QtCore import QObject, pyqtSignal

from settings import *

# getting an instance of singleton logger
from logger import get_logger
log = get_logger()


class MessageListener(QObject):

    # define signal to inform UI about a received message
    message_received = pyqtSignal('QString')

    def __init__(self):
        super(MessageListener, self).__init__()

        self.start_msg_receiver()

    def start_msg_receiver(self):
        """
        function starts a thread to receive messages
        """
        try:
            thread.start_new_thread(
                    self.monitor_messages, ("MsgRecvThread", 2, ))
        except Exception as exp:
            log.warning("Error: unable to start message recevier thread")
            log.warning(exp)

    def monitor_messages(self, thread_name, delay):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('', UDP_PORT))

        while True:
            try:
                # buffer size is 1024 bytes
                org_data, addr = sock.recvfrom(1024)
                data = org_data.decode("utf-8")

                log.info("received message: " + data)
                self.message_received.emit(data)
            except Exception as exp:
                log.warning("Got exception while monitoring messages")
                log.warning(exp)
