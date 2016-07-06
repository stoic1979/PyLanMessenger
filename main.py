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

        # start
        self.root.mainloop()

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
