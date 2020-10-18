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

class MyGrid:
    def my_grid(self,**kw):
        parent = self.master
        for i,t in kw.items():
            if i in ('row','column'):
                if (len_t:=len(t))==0:
                    continue
                # row-1,col-1
                t=(t[0]-1,*t[1:])
                if len_t == 4:
                    # row , row_span , uniform_id , weight
                    kw2 = {i: t[0] , f'{i}span':t[1]}
                    self.grid(**kw2) # CORE
                    method = getattr(tk.Grid,f'grid_{i}configure')
                    method(parent , t[0] , uniform = t[2] , weight = t[3]) # CORE
                elif len_t == 3:
                    # row , row_span , uniform_id
                    kw2 = {i: t[0] , f'{i}span':t[1]}
                    self.grid(**kw2) # CORE
                    method = getattr(tk.Grid,f'grid_{i}configure')
                    method(parent , t[0] , uniform = t[2]) # CORE
                elif len_t == 2:
                    # row , row_span
                    kw2 = {i: t[0] , f'{i}span':t[1]}
                    self.grid(**kw2) # CORE
                elif len_t == 1:
                    # row
                    kw2 = {i: t[0]}
                    self.grid(**kw2) # CORE
            elif i == 'sti':
                # sticky
                self.grid_configure(sticky = t)
    
class MyButton(tk.Button , MyGrid):
    def __init__(self,parent,**kw):
        super().__init__(parent,**kw)
           
root = MyTk(400,300)
b = MyButton(root,text='b1')
bb = MyButton(root,text='b2')
b.my_grid(row=(1,1,),column=(1,1,0,1),sti='nswe')
bb.my_grid(row=(1,1),column=(2,1,0,12),sti='nswe')
root.mainloop()