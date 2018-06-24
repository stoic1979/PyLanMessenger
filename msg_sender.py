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
# UDP message sender
#
# It sends messages to given IP
#
import socket

from packetizer import Packet
from utils import *
from settings import *

# getting an instance of singleton logger
from logger import get_logger
log = get_logger()


class MessageSender():

    def __init__(self, host, ip):
        super(MessageSender, self).__init__()
        self.host = host
        self.ip = ip

    def send_to_ip(self, ip, other_host, msg):
        """
        function to send UDP message to given ip
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        pkt = Packet(
                op="TCM", ip=self.ip, host=self.host, msg=msg).to_json()
        sock.sendto(bytes(pkt, "utf-8"), (ip, UDP_PORT))

    def send_broadcast_message(self, msg):
        """
        function to send UDP message to all users in LAN
        at given port
        """
        log.debug("send broadcast: %s" % msg)

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        for i in range(2, 255):
            recv_ip = "%s.%d" % (get_ip_prefix(self.ip), i)
            # dont send to self
            if self.ip == recv_ip:
                continue
            sock.sendto(bytes(msg, "utf-8"), (recv_ip, UDP_PORT))
