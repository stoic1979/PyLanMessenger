from Tkinter import *
from ttk import Frame, Button, Label, Style

import tkFileDialog
import socket
import thread

from utils import *
from settings import *


class MainGui(Frame):
  
    def __init__(self, parent):
        Frame.__init__(self, parent)   
         
        self.parent = parent
        self.initUI()
        
        
    def initUI(self):
      
        self.hostname = socket.gethostname()
        self.parent.title("Lan Messenger - %s" % self.hostname) 
        #self.parent.title("Windows")
        self.pack(fill=BOTH, expand=True)

        self.columnconfigure(1, weight=1)
        self.columnconfigure(3, pad=7)
        self.rowconfigure(3, weight=1)
        self.rowconfigure(10, pad=7)
        
        lbl = Label(self, text="Welcome - %s" % self.hostname)
        lbl.grid(sticky=W, pady=4, padx=5)

        # list....
        scrollbar = Scrollbar(self)
        scrollbar.grid(row=1, column=0, columnspan=2, rowspan=2, padx=5)

        mylist = Listbox(self, yscrollcommand=scrollbar.set)
        mylist.grid(row=1, column=0, columnspan=2, rowspan=2, padx=5, sticky=E+W)

        self.mylist = mylist
        scrollbar.config(command=mylist.yview)
        # list....
        
        area = Text(self)
        area.grid(row=6, column=0, columnspan=2, rowspan=4, padx=5, sticky=E+W)
        self.text = area
        
        abtn = Button(self, text="Refresh", command=self.refresh)
        abtn.grid(row=0, column=3)

        cbtn = Button(self, text="Send", command=self.send_msg)
        cbtn.grid(row=1, column=3, pady=4)

        dbtn = Button(self, text="Send File", command=self.send_file)
        dbtn.grid(row=2, column=3, pady=4)
              
        self.add_menus()

        # getting IP Address of system
        self.ip = get_ip_address()

        self.start_msg_receiver()

        self.send_IAI()

    def add_menus(self):
        menubar = Menu(self.parent)

        # create a pulldown menu, and add it to the menu bar
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open", command=self.hello)
        filemenu.add_command(label="Save", command=self.hello)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.parent.quit)
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
        self.parent.config(menu=menubar)

    def hello(self):
        print "hello"

    def refresh(self):
        self.send_IAI()

    def send_IAI(self):
        # broadcast a message that IAI - "I Am In" the n/w
        self.send_broadcast_message("IAI%s:%s" % (self.ip, self.hostname))

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
            if data[:3] == "IAI":
                self.handle_IAI(data)

    def handle_IAI(self, msg):
        status, ip, host = process_IAI(msg)
        if status:
            self.mylist.insert(END, "%s - %s" % (host, ip))

    def start_msg_receiver(self):
        """
        function starts a thread to receive messages
        """
        try:
            thread.start_new_thread(self.monitor_messages, ("MsgRecvThread", 2, ) )
        except Exception as exp:
            print "Error: unable to start message recevier thread"
            print exp

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
def main():
    root = Tk()
    root.geometry("640x480+200+200")
    app = MainGui(root)
    root.mainloop()  

if __name__ == '__main__':
    main()  
