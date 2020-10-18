import tkinter as tk
import tkinter.ttk as ttk
import tkinter.font as font
from PIL import Image
from PIL import ImageTk

class MyGrid:
    def my_grid(self,**kw):
        self.parent = self.master
        for i,t in kw.items():
            if i in ('row','column'):
                if (len_t:=len(t))==0:
                    continue
                # row-1,col-1
                t=(t[0]-1,*t[1:])
                if len_t == 2:
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
    def config_row_or_column(self,row,kw):
        # row is a tuple of row or columns
        new_kw = dict()
        row = [r-1 for r in row]
        for r in row:
            new_kw[r] = dict()
        for i,tmp in kw.items():
            if i in ('id','weight'):
                if i == 'id':
                    tmp = tmp.split(',')
                    i = 'uniform'
                elif type(tmp) not in (list,tuple):
                    tmp = [tmp]
                diff = len(row)-len(tmp)
                # elongate/replicate shorter tuple/list
                while diff > 0:
                    tmp += [tmp[-1]]
                    diff -= 1
                for r,other_value in zip(row,tmp):
                    new_kw[r][i] = other_value
        return new_kw
    
    def config_row(self,*row,**kw):
        new_kw = self.config_row_or_column(row, kw)
        for r,kw in new_kw.items():
            self.parent.grid_rowconfigure(r,kw)
    
    def config_column(self,*column,**kw):
        new_kw = self.config_row_or_column(column, kw)
        for c,kw in new_kw.items():
            self.parent.grid_columnconfigure(c,kw)

class Sizegrip(ttk.Sizegrip , MyGrid):
    def __init__(self,parent,**kw):
        super().__init__(parent,**kw)

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
        self.sizegrips = dict()
        if center:
            self.center()

    def sizegrip(self,r,c):
        self.sizegrips[r] = S = Sizegrip(self)
        S.my_grid(row=r,column=c,sti = 'we')

class MyButton(ttk.Button , MyGrid):
    def __init__(self,parent,**kw):
        super().__init__(parent,**kw)

class Label(tk.Label , MyGrid):
    def __init__(self,parent,**kw):
        super().__init__(parent,**kw)

class MyLabel(ttk.Label , MyGrid):
    def __init__(self,parent,**kw):
        super().__init__(parent,**kw)

class Classname(MyLabel):
    def __init__(self,parent,**kw):
        name = kw.pop('classname','test')
        self.tmp = ''
        super().__init__(parent,**kw)
        self['font'] = 'fixed'
        self.set(name)
    
    def set(self,name = ''):
        self.name = name
        self['text']= f'Selected Class: "{self.name}"'
    
    def hide(self):
        self.tmp = self.name
        self['text'] = ''
    
    def show(self):
        self.set(self.tmp)

class Middle(ttk.Labelframe , MyGrid):
    def __init__(self,parent,**kw):
        super().__init__()
        self.groups = dict() # CORE
        self.current_groupname = None # CORE
    
    def add_new(self,groupname , class_ , r , c , **kw):
        t_args = kw.pop('t_args',tuple())
        kw_args = kw.pop('kw_args',dict())
        sti = kw.pop('sti' , 'nwse')
        show = kw.pop('show', True)
        obj = class_(self,*t_args,**kw_args)
        self.add_old(groupname, obj , r, c, sti , show)

    def add_old(self,groupname,payload,r,c , sti = 'nwsw' , show = True):
        if groupname not in self.groups:
            self.groups[groupname]= {'payloads': []}
        self.groups[groupname]['payloads'] += [payload]
        payload.my_grid(row = r , column = c , sti = sti)
        if not show:
            payload.grid_remove()
    
    def hide(self,groupname):
        for i in self.groups[groupname]['payloads']:
            i.grid_remove()
    
    def show(self,groupname):
        for i in self.groups[groupname]['payloads']:
            i.grid()
    
    def switchto(self,groupname):
        if self.current_groupname:
            self.hide(self.current_groupname)
        self.show(groupname)
        self.current_groupname = groupname

class Tabs(ttk.Labelframe , MyGrid):
    def __init__(self,parent,**kw):
        self.switcher = kw.pop('switcher')
        super().__init__(parent,**kw)
        tmp_label = Label(parent)
        self.cursors = ('hand2',self['cursor'])
        self.colors = ('black','gray',tmp_label['bg'])
        tmp_label.destroy()
        self.tabs = dict() # CORE
        self.IMG = ImageTk.PhotoImage( image=Image.new('RGBA',(1,1),(0,0,0,0)) ) # CORE
        self.entered_text = None
        self.selected_text = None
        self.max_width_label = 1
        self.grid_count = 0 # CORE
    
    def activate(self,e,text,B):
        if self.selected_text:
            self.deactivate(text)
        self.selected_text = text
        B['bg']=self.colors[0]
        self.switcher.switchto(text) # CORE
        
    def deactivate(self,text):
        self.tabs[self.selected_text][1]['bg']=self.colors[2]
        self.selected_text = None
    
    def add(self,text):
        A = Label(self,text=text,anchor='center' , cursor = self.cursors[0])
        if (tmp_width := font.Font(font = A['font']).measure(text)) > self.max_width_label:
            self.max_width_label = tmp_width
        B = Label(self,text='',  cursor = self.cursors[0] ,width = self.max_width_label, height = 1,anchor='center' , image = self.IMG )
        self.tabs[text] = [ A , B ]
        A.bind('<Enter>',lambda e,arg1=text,arg2=B : self.event_enter(e,arg1,arg2) )
        B.bind('<Enter>',lambda e,arg1=text,arg2=B : self.event_enter(e,arg1,arg2) )
        A.bind('<Leave>',lambda e,arg1=text,arg2=B : self.event_leave(e,arg1,arg2) )
        B.bind('<Leave>',lambda e,arg1=text,arg2=B : self.event_leave(e,arg1,arg2) )
        A.bind('<Button>',lambda e,arg1=text,arg2=B : self.activate(e,arg1,arg2) )
        B.bind('<Button>',lambda e,arg1=text,arg2=B : self.activate(e,arg1,arg2) )
        self.grid_count += 1
        A.my_grid(row=(1,),column=(self.grid_count,),sti='we')
        B.my_grid(row=(2,),column=(self.grid_count,),sti='we')
        A.config_column(self.grid_count, id = f'{self.grid_count}',weight = 1)
    def event_enter(self,e,text,B):
        if text == self.selected_text:
            return
        B['bg']=self.colors[1]
    def event_leave(self,e,text,B):
        if text == self.selected_text:
            return
        B['bg']=self.colors[2]

if __name__ == '__main__':
    root = MyTk(400,300)
    m = Middle(root) # CORE
    t = Tabs(root , switcher = m)
    tabnames = ['Prepare Dataset','Create Model','Results']
    t.add(tabnames[0])
    t.add(tabnames[1])
    t.add(tabnames[2])
    t.my_grid(row=(2,),column=(1,2),sti='we')
    t.config_column(1,2,id='1,2',weight=1) # CORE
    t.config_row(2,3,4,id = '2,3,4', weight = (0,1,0) ) # CORE
    m.my_grid(row=(3,),column=(1,2),sti = 'nswe')
    m.add_new(tabnames[0] , Label , (1,) , (1,) , kw_args = {'text':'lab1'} , show = False )
    m.add_new(tabnames[1] , Label , (1,) , (2,) , kw_args = {'text':'lab2'} , show = False )
    root.sizegrip((1,),(1,100))
    root.sizegrip((4,),(1,100))
    root.mainloop()