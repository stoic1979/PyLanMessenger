from Tkinter import *
import tkFileDialog


class MainGui:

    def __init__(self):
        self.root = Tk()
        self.root.wm_title("Lan Messenger") 
    
        # gui frame
        fm = Frame(self.root, width=300, height=200, bg="blue")
        fm.pack(side=TOP, expand=NO, fill=NONE)
    
        # dimensions
        self.root.geometry("640x480") 

        # buttons
        Button(fm, text="Send File", width=10, command=self.send_file).pack(side=LEFT)
        Button(fm, text="Send", width=10).pack(side=LEFT)

        self.add_menus()

        # start
        self.root.mainloop()

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
