from Tkinter import *


root = Tk()
root.wm_title("Lan Messenger") 

fm = Frame(root, width=300, height=200, bg="blue")
fm.pack(side=TOP, expand=NO, fill=NONE)
    
root.geometry("640x480") 

Button(fm, text="Send File", width=10).pack(side=LEFT)
Button(fm, text="Send", width=10).pack(side=LEFT)


root.mainloop()
