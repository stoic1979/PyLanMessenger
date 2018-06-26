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
        QApplication, QWidget, QMenu, QMainWindow, QMessageBox,
        QListWidgetItem, QSystemTrayIcon, QStyle, QAction, qApp)
from PyQt5.uic import loadUi

from utils import *
from settings import *
from msg_listener import MessageListener
from msg_sender import MessageSender
from msg_manager import MessageManager
from packetizer import Packet

from about_dialog import AboutDialog
from prefs_dialog import PrefsDialog


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

        self.users = {}

        self.host = socket.gethostname()
        self.ip = get_ip_address()

        # button event handlers
        self.btnRefreshBuddies.clicked.connect(self.refreshBuddies)
        self.btnSend.clicked.connect(self.sendMsg)

        self.lstBuddies.currentItemChanged.connect(
                self.on_buddy_selection_changed)

        self.msg_manager = MessageManager()
        self.msg_sender = MessageSender(self.host, self.ip)

        self.message_listener = MessageListener()
        self.message_listener.message_received.connect(self.handle_messages)

        self.send_IAI()

        self.setup_tray_menu()

        # setting up handlers for menubar actions
        self.actionAbout.triggered.connect(self.about)
        self.actionExit.triggered.connect(qApp.quit)
        self.actionPreferences.triggered.connect(self.show_preferences)

    def about(self):
        print("about")
        ad = AboutDialog()
        ad.display()

    def show_preferences(self):
        print("preferences")
        pd = PrefsDialog()
        pd.display()

    def setup_tray_menu(self):

        # setting up QSystemTrayIcon
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(
                self.style().standardIcon(QStyle.SP_ComputerIcon))

        # tray actions
        show_action = QAction("Show", self)
        quit_action = QAction("Exit", self)
        hide_action = QAction("Hide", self)

        # action handlers
        show_action.triggered.connect(self.show)
        hide_action.triggered.connect(self.hide)
        quit_action.triggered.connect(qApp.quit)

        # tray menu
        tray_menu = QMenu()
        tray_menu.addAction(show_action)
        tray_menu.addAction(hide_action)
        tray_menu.addAction(quit_action)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def closeEvent(self, event):
        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            "PyLanMessenger",
            "PyLanMessenger was minimized to Tray",
            QSystemTrayIcon.Information,
            2000
        )

    def handle_messages(self, data):
        log.debug("UI handling message: %s" % data)
        pkt = Packet()
        pkt.json_to_obj(data)
        if pkt.op == "IAI":
            self.handle_IAI(pkt.ip, pkt.host)
        if pkt.op == "MTI":
            self.handle_MTI(pkt.ip, pkt.host)
        if pkt.op == "TCM":
            self.handle_TCM(pkt.ip, pkt.host, pkt.msg)

    def send_IAI(self):
        # broadcast a message that IAI - "I Am In" the n/w
        pkt = Packet(op="IAI", ip=self.ip, host=self.host).to_json()
        self.msg_sender.send_broadcast_message(pkt)

    def send_MTI(self):
        # broadcast a message that MTI - "Me Too In" the n/w
        pkt = Packet(op="MTI", ip=self.ip, host=self.host).to_json()
        self.msg_sender.send_broadcast_message(pkt)

    def handle_IAI(self, ip, host):
        """
        handle "I am In" packet

        reply with MTI for IAI
        me too in when other says "i am in"
        """
        self.send_MTI()

        if host not in self.users:
            print("adding host", host)
            self.users[host] = ip
            self.lstBuddies.addItem(str(host))

    def handle_MTI(self, ip, host):
        """
        handle Me Too In packet
        """

        if host not in self.users:
            self.users[host] = ip
            self.lstBuddies.addItem(str(host))

    def handle_TCM(self, ip, host, msg):
        self.add_chat_msg(ip, host, "%s: %s" % (host, msg))

    def refreshBuddies(self):
        self.lstBuddies.clear()
        self.users = {}
        self.send_IAI()

    def sendMsg(self):
        try:
            receiver_host = self.lstBuddies.currentItem().text()
        except:
            log.warning("no host found from selection")
            return

        msg = self.teMsg.toPlainText()

        receiver_ip = self.users[receiver_host]

        # sending msg to receiver
        self.msg_sender.send_to_ip(receiver_ip, receiver_host, msg.strip())

        # adding my message in chat area in UI
        self.add_chat_msg(
                receiver_ip, receiver_host, "%s: %s" % (self.host, msg))

        # cleaning up textbox for typed message in UI
        self.teMsg.setText("")

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
