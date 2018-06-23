#!/usr/bin/python3

import sys
import os
import socket

from PyQt5 import QtGui, QtCore, uic
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QMessageBox, QListWidgetItem
from PyQt5.uic import loadUi

from utils import *
from settings import *
from msg_hndlr import MessageHandler

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

        self.hostname = socket.gethostname()

        # button event handlers
        self.btnRefreshBuddies.clicked.connect(self.refreshBuddies)
        self.btnSend.clicked.connect(self.sendMsg)

        self.lstBuddies.currentItemChanged.connect(self.on_buddy_selection_changed)

        self.init_messenger()

        self.message_handler = MessageHandler()
        self.message_handler.message_received.connect(self.handle_messages)

    def init_messenger(self):
        # getting IP Address of system
        self.ip = get_ip_address()
        self.send_IAI()
        self.users = {}
        self.messages = {}


    def handle_messages(self, data):
        print ("[Window] :: handling message:", data)
        if data[:3] == "IAI":
            self.handle_IAI(data)
        if data[:3] == "MTI":
            self.handle_MTI(data)
        if data[:3] == "TCM":
            self.handle_TCM(data)

    def send_IAI(self):
        # broadcast a message that IAI - "I Am In" the n/w
        self.send_broadcast_message("IAI%s:%s" % (self.ip, self.hostname))

    def send_MTI(self):
        # broadcast a message that MTI - "Me Too In" the n/w
        self.send_broadcast_message("MTI%s:%s" % (self.ip, self.hostname))

    def handle_IAI(self, msg):
        """
        handle "I am In" packet

        reply with MTI for IAI
        me too in when other says "i am in"
        """
        self.send_MTI()

        status, ip, host = process_IAI(msg)
        if status:
            if not host in self.users:
                print ("adding host", host)
                self.users[host] = ip
                self.lstBuddies.addItem(str(host))

    def handle_MTI(self, msg):
        """
        handle Me Too In packet
        """

        status, ip, host = process_MTI(msg)
        if status:
            if not host in self.users:
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
        print ("[INFO] send broadcast: %s" % msg)
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        for i in range(2, 255):
            recv_ip = "%s.%d" % (get_ip_prefix(self.ip), i)
            # dont send to self
            if self.ip == recv_ip:
                continue
            sock.sendto(bytes(msg, "utf-8"), (recv_ip, UDP_PORT))


    def refreshBuddies(self):
        print ("[INFO] refreshing buddy list")
        self.lstBuddies.clear()
        self.users = {}
        self.send_IAI()

    def sendMsg(self):
        print ("[INFO] send Msg")

        try:
            host = self.lstBuddies.currentItem().text()
            print ("recevier:", host)
        except:
            print ("[WARNING] no host found from selection")
            return

        msg = self.teMsg.toPlainText()
        print ("msg:", msg)

        self.send_to_ip(self.users[host], host, msg.strip())
        self.teMsg.setText("")

    def send_to_ip(self, ip, other_host, msg):
        """
        function to send UDP message to given ip
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        packet = "TCM%s:%s:%s" % (self.ip, self.hostname, msg)
        sock.sendto(bytes(packet, "utf-8"), (ip, UDP_PORT))
        self.add_chat_msg(ip, other_host, "%s: %s" % (self.hostname, msg) )

    def add_chat_msg(self, ip, other_host, msg):

        # NOTE:
        # we are storing msgs in dict as per other host
        # both sent/recvd msgs with other host
        if not other_host in self.messages:
            self.messages[other_host] = []

        self.messages[other_host].append(msg)
        self.teMsgsList.append(msg)

    def on_buddy_selection_changed(self):
        print("count", self.lstBuddies.count() )
        if self.lstBuddies.count() == 0:
            return

        # no buddy selected
        if not self.lstBuddies.currentItem():
            return

        sel_user = self.lstBuddies.currentItem().text()
        print ("You selected buddy is: \"%s\"" % sel_user)

        self.teMsgsList.clear()

        # no need to continue if there are no messages for selected user
        if not sel_user in self.messages:
            return

        msgs = self.messages[sel_user]
        print ("msgs:", msgs)
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
        print("[INFO] Value of pressed message box button:", retval)


##############################################################################
#                                                                            #
#                                 MAIN                                       #
#                                                                            #
##############################################################################
if __name__ == '__main__':

    app = QApplication(sys.argv)
    window = Window()
    window.resize(1240, 820)	
    window.show()
    sys.exit(app.exec_())
