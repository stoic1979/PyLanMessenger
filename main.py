from Tkinter import *
import tkFileDialog
import socket
import thread

from utils import *
from settings import *


class MainGui:

    def __init__(self):
        self.root = Tk()

        self.hostname = socket.gethostname()
        self.root.wm_title("Lan Messenger - %s" % self.hostname) 
    
        # gui frame
        fm = Frame(self.root, width=300, height=200, bg="blue")
        fm.pack(side=TOP, expand=NO, fill=NONE)
    
        # dimensions
        self.root.geometry("640x480") 

        # buttons
        Button(fm, text="Send File", width=10, command=self.send_file).pack(side=LEFT)
        Button(fm, text="Send", width=10, command=self.send_msg).pack(side=LEFT)
        Button(fm, text="Refresh", width=10, command=self.refresh).pack(side=LEFT)

        self.text = Text(fm, relief=SUNKEN)
        self.text.pack(side=LEFT, expand=YES, fill=BOTH)  

        scrollbar = Scrollbar(fm)
        scrollbar.pack(side=RIGHT, fill=Y)

        mylist = Listbox(fm, yscrollcommand=scrollbar.set)
        for line in range(100):
            mylist.insert(END, "This is line number " + str(line))
        mylist.pack(side=LEFT, fill=NONE)

        self.mylist = mylist
        
        scrollbar.config(command=mylist.yview)

        self.add_menus()

        # getting IP Address of system
        self.ip = get_ip_address()

        self.start_msg_receiver()

        # start
        self.root.mainloop()

    def refresh(self):
        # broadcast a message that IAI - "I Am In" the n/w
        self.send_broadcast_message("IAI%s" % self.ip)

    def send_msg(self):
        msg = self.text.get("1.0",END)
        print "send msg: ", self.text.get("1.0",END)
        #print "selected is: ", self.mylist.get(self.mylist.curselection())
        self.send_broadcast_message(msg)

    def send_broadcast_message(self, msg):
        """
        function to send UDP message to all users in LAN
        at given port
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        for i in range(2, 255):
            recv_ip = "%s.%d" % (get_ip_prefix(self.ip), i)
            # dont send to self
            if self.ip == recv_ip:
                continue
            sock.sendto(msg, (recv_ip, UDP_PORT))

    def monitor_messages(self, thread_name, delay):
        sock = socket.socket(socket.AF_INET, # Internet
                            socket.SOCK_DGRAM) # UDP
        sock.bind(('', UDP_PORT))

        while True:
            # buffer size is 1024 bytes
            data, addr = sock.recvfrom(1024)
            print "received message:", data

    def start_msg_receiver(self):
        """
        function starts a thread to receive messages
        """
        try:
            thread.start_new_thread(self.monitor_messages, ("MsgRecvThread", 2, ) )
        except Exception as exp:
            print "Error: unable to start message recevier thread"
            print exp

    def hello(self):
        print "hello"

    def add_menus(self):
        menubar = Menu(self.root)

        # create a pulldown menu, and add it to the menu bar
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open", command=self.hello)
        filemenu.add_command(label="Save", command=self.hello)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=filemenu)

        # create more pulldown menus
        editmenu = Menu(menubar, tearoff=0)
        editmenu.add_command(label="Cut", command=self.hello)
        editmenu.add_command(label="Copy", command=self.hello)
        editmenu.add_command(label="Paste", command=self.hello)
        menubar.add_cascade(label="Edit", menu=editmenu)

        helpmenu = Menu(menubar, tearoff=0)
        helpmenu.add_command(label="About", command=self.hello)
        menubar.add_cascade(label="Help", menu=helpmenu)

        # display the menu
        self.root.config(menu=menubar)

    def quit(self):
        self.root.quit()

    def send_file(self):
        file_types = [('All files', '*')]
        open = tkFileDialog.Open(self.root, filetypes = file_types)
        statusbar = Label(self.root, text="", bd=1, relief=SUNKEN, anchor=W)
        statusbar.pack(side=BOTTOM, fill=X)
        file_path = open.show()
        statusbar.config(text = file_path)
        print "Will send file", file_path


#########################
#   STARTING MAIN GUI   #
#########################
MainGui()
