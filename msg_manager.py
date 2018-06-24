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
# Message manager
#
# It stores messages as received from nw and
# loads cached messages from local database
#
import _thread as thread
import socket
from PyQt5.QtCore import QObject, pyqtSignal

from settings import *


class MessageManager(QObject):

    # define signal to inform UI about a received message
    message_received = pyqtSignal('QString')

    def __init__(self):
        super(MessageManager, self).__init__()

        self.messages = {}

        self._load_msgs_from_db()

    def _load_msgs_from_db(self):
        pass

    def add_chat_msg(self, ip, other_host, msg):

        print("[MessageManager] msg:", msg)

        # NOTE:
        # we are storing msgs in dict as per other host
        # both sent/recvd msgs with other host
        if other_host not in self.messages:
            self.messages[other_host] = []

        self.messages[other_host].append(msg)

    def get_message_for_user(self, user):
        if user not in self.messages:
            return ""

        return self.messages[user]
