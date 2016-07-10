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
        self.init_messenger()
        
        
    def initUI(self):
      
        self.hostname = socket.gethostname()
        self.parent.title("Lan Messenger - %s" % self.hostname) 
        self.pack(fill=BOTH, expand=True)

        self.columnconfigure(1, weight=1)
        self.columnconfigure(3, pad=7)
        self.rowconfigure(4, weight=1)
        self.rowconfigure(5, pad=7)
        
        lbl = Label(self, text="Welcome - %s" % self.hostname)
        lbl.grid(sticky=W, pady=4, padx=5)

        # list....
        #scrollbar = Scrollbar(self)
        #scrollbar.grid(row=1, column=0, columnspan=2, rowspan=2, padx=5)

        #mylist = Listbox(self, yscrollcommand=scrollbar.set)
        mylist = Listbox(self)
        mylist.grid(row=0, column=0, columnspan=1, rowspan=8, padx=5, sticky=E+W+N+S)

        mylist.bind('<<ListboxSelect>>', self.on_user_selection_changed)

        self.mylist = mylist
        #scrollbar.config(command=mylist.yview)
        # list....
        

        frame2 = Frame(self)
        frame2.columnconfigure(1, weight=1)
        frame2.columnconfigure(3, pad=7)
        frame2.rowconfigure(3, weight=1)
        frame2.rowconfigure(5, pad=7)

        frame2.grid(row=0, column=1, columnspan=2, rowspan=8, padx=5, sticky=E+W+N+S)

        area = Listbox(frame2)
        area.grid(row=1, column=0, columnspan=2, rowspan=6, padx=5, sticky=E+W+S+N)
        self.msg_lst = area

        ma = Text(frame2)
        ma.grid(row=4, column=0, columnspan=2, rowspan=2, padx=5, sticky=E+W+S+N)
        self.text = ma
        
        abtn = Button(self, text="Refresh", command=self.refresh)
        abtn.grid(row=0, column=3)

        cbtn = Button(self, text="Send", command=self.send_msg)
        cbtn.grid(row=5, column=3, pady=4)

        dbtn = Button(self, text="Send File", command=self.send_file)
        dbtn.grid(row=2, column=3, pady=4)

              
        self.add_menus()


    def init_messenger(self):
        # getting IP Address of system
        self.ip = get_ip_address()
        self.start_msg_receiver()
        self.send_IAI()
        self.users = {}
        self.messages = {}

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

    def on_user_selection_changed(self, evt):
        # Note here that Tkinter passes an event object to on_user_selection_changed()
        w = evt.widget
        index = int(w.curselection()[0])
        sel_user = w.get(index)
        print 'You selected item %d: "%s"' % (index, sel_user)

        self.msg_lst.delete(0, END)

        # no need to continue if there are no messages for selected user
        if not self.messages.has_key(sel_user):
            return

        msgs = self.messages[sel_user]
        for m in msgs:
            self.mylist.insert(END, m)

    def hello(self):
        print "hello"

    def refresh(self):
        self.send_IAI()

    def send_IAI(self):
        # broadcast a message that IAI - "I Am In" the n/w
        self.send_broadcast_message("IAI%s:%s" % (self.ip, self.hostname))

    def send_MTI(self):
        # broadcast a message that MTI - "Me Too In" the n/w
        self.send_broadcast_message("MTI%s:%s" % (self.ip, self.hostname))

    def get_selected_user_ip(self, txt):
        for k,v in self.users.iteritems():
            if txt == "%s - %s" % (k,v):
                return v

    def send_msg(self):
        msg = self.text.get("1.0",END)
        print "send msg: ", self.text.get("1.0",END)

        try:
            txt = self.mylist.get(self.mylist.curselection())
        except:
            return

        self.send_to_ip(self.users[txt], msg.strip())

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

    def add_chat_msg(self, ip, host, msg):
        if not self.messages.has_key(host):
            self.messages[host] = []
        m = "%s: %s" % (host, msg)
        self.messages[ip].append(m)
        self.msg_lst.insert(END, m)

    def send_to_ip(self, ip, msg):
        """
        function to send UDP message to given ip
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto("TCM%s:%s:%s" % (self.ip, self.hostname, msg), (ip, UDP_PORT))
        self.add_chat_msg(ip, self.hostname, msg)

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
            if data[:3] == "MTI":
                self.handle_MTI(data)
            if data[:3] == "TCM":
                self.handle_TCM(data)

    def handle_IAI(self, msg):
        # reply with MTI for IAI
        # me too in when other says "i am in"
        self.send_MTI()

        status, ip, host = process_IAI(msg)
        if status:
            if not self.users.has_key(host):
                self.users[host] = ip
                self.mylist.insert(END, "%s" % host)

    def handle_MTI(self, msg):
        status, ip, host = process_MTI(msg)
        if status:
            if not self.users.has_key(host):
                self.users[host] = ip
                self.mylist.insert(END, "%s" % host)

    def show_popup(self):
        popup = Tk()
        popup.wm_title("Msg from %s" % host)
        popup.geometry("480x320+300+300")
        label = Label(popup, text=msg)
        label.pack(side="top", fill="x", pady=10)
        B1 = Button(popup, text="Okay", command = popup.destroy)
        B1.pack()
        popup.mainloop()

    def handle_TCM(self, msg):
        status, ip, host, msg = process_TCM(msg.strip())
        if not status:
            return

        self.add_chat_msg(ip, host, msg)
        print "Got message %s from %s" % (msg, ip)
    
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
    root.geometry("960x640+100+40")
    app = MainGui(root)
    root.mainloop()  

if __name__ == '__main__':
    main()  
