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

import sys
import os
import socket

from PyQt5 import QtGui, QtCore, uic
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import (
        QApplication, QWidget, QMainWindow, QMessageBox, QListWidgetItem)
from PyQt5.uic import loadUi

from utils import *
from settings import *
from msg_listener import MessageListener
from msg_manager import MessageManager
from packetizer import Packet


# getting an instance of singleton logger
from logger import get_logger
log = get_logger()

DIRPATH = os.path.join(os.path.dirname(os.path.abspath(__file__)))


class Window(QMainWindow):
    """
    Main GUI class for application
    """

    def __init__(self):
        QWidget.__init__(self)

        # loaind ui from xml
        uic.loadUi(os.path.join(DIRPATH, 'app.ui'), self)

        # self.show_msgbox("Info", "Lan Messenger")

        self.host = socket.gethostname()

        # button event handlers
        self.btnRefreshBuddies.clicked.connect(self.refreshBuddies)
        self.btnSend.clicked.connect(self.sendMsg)

        self.lstBuddies.currentItemChanged.connect(
                self.on_buddy_selection_changed)

        self.init_messenger()

        self.msg_manager = MessageManager()

        self.message_listener = MessageListener()
        self.message_listener.message_received.connect(self.handle_messages)

    def init_messenger(self):
        # getting IP Address of system
        self.ip = get_ip_address()
        self.send_IAI()
        self.users = {}

    def handle_messages(self, data):
        log.debug("handling message: %s" % data)
        if data[:3] == "IAI":
            self.handle_IAI(data)
        if data[:3] == "MTI":
            self.handle_MTI(data)
        if data[:3] == "TCM":
            self.handle_TCM(data)

    def send_IAI(self):
        # broadcast a message that IAI - "I Am In" the n/w
        pkt = Packet(op="IAI", ip=self.ip, host=self.host).to_json()
        self.send_broadcast_message(pkt)

    def send_MTI(self):
        # broadcast a message that MTI - "Me Too In" the n/w
        self.send_broadcast_message("MTI%s:%s" % (self.ip, self.host))

    def handle_IAI(self, msg):
        """
        handle "I am In" packet

        reply with MTI for IAI
        me too in when other says "i am in"
        """
        self.send_MTI()

        status, ip, host = process_IAI(msg)
        if status:
            if host not in self.users:
                print("adding host", host)
                self.users[host] = ip
                self.lstBuddies.addItem(str(host))

    def handle_MTI(self, msg):
        """
        handle Me Too In packet
        """

        status, ip, host = process_MTI(msg)
        if status:
            if host not in self.users:
                self.users[host] = ip
                self.lstBuddies.addItem(str(host))

    def handle_TCM(self, msg):
        status, ip, host, msg = process_TCM(msg.strip())
        if not status:
            return

        self.add_chat_msg(ip, host, "%s: %s" % (host, msg))

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

    def refreshBuddies(self):
        self.lstBuddies.clear()
        self.users = {}
        self.send_IAI()

    def sendMsg(self):
        try:
            host = self.lstBuddies.currentItem().text()
        except:
            log.warning("no host found from selection")
            return

        msg = self.teMsg.toPlainText()

        self.send_to_ip(self.users[host], host, msg.strip())
        self.teMsg.setText("")

    def send_to_ip(self, ip, other_host, msg):
        """
        function to send UDP message to given ip
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        pkt = Packet(
                op="TCM", ip=self.ip, host=self.host, msg=msg).to_json()
        #packet = "TCM%s:%s:%s" % (self.ip, self.host, msg)
        sock.sendto(bytes(pkt, "utf-8"), (ip, UDP_PORT))
        self.add_chat_msg(ip, other_host, "%s: %s" % (self.host, msg))

    def add_chat_msg(self, ip, other_host, msg):

        self.msg_manager.add_chat_msg(ip, other_host, msg)

        # showing msg in UI
        self.teMsgsList.append(msg)

    def on_buddy_selection_changed(self):
        if self.lstBuddies.count() == 0:
            return

        # no buddy selected
        if not self.lstBuddies.currentItem():
            return

        sel_user = self.lstBuddies.currentItem().text()
        log.debug("You selected buddy is: \"%s\"" % sel_user)

        self.teMsgsList.clear()

        msgs = self.msg_manager.get_message_for_user(sel_user)
        for m in msgs:
            self.teMsgsList.append(m)

    def show_msgbox(self, title, text):
        """
        Function for showing error/info message box
        """
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(text)
        msg.setWindowTitle(title)
        msg.setStandardButtons(QMessageBox.Ok)
        retval = msg.exec_()


##############################################################################
#                                                                            #
#                                 MAIN                                       #
#                                                                            #
##############################################################################
if __name__ == '__main__':

    app = QApplication(sys.argv)
    window = Window()
    # window.resize(1240, 820)
    window.show()
    sys.exit(app.exec_())
