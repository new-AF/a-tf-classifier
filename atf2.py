import tkinter as tk
import tkinter.ttk as ttk
from PIL import Image
from PIL import ImageTk

class MyTk(tk.Tk):
    def resize(self, w = None , h = None):
        self.w = w if w else self.winfo_reqwidth()
        self.h = h if h else self.winfo_reqheight()
        self.geometry(f'{self.w}x{self.h}')
    
    def center(self):
        self.W = self.winfo_screenwidth()
        self.H = self.winfo_screenheight()
        x = self.W//2 - self.w//2
        y = self.H//2 - self.h//2
        self.geometry(f'+{x}+{y}')
    
    def __init__(self, w = None , h = None , title = 'MyTk' , center:bool = True):
        super().__init__()
        self.resize(w, h) # to set self.w & self.h
        self.title(title)
        if center:
            self.center()

root = MyTk(400,100)

root.mainloop()