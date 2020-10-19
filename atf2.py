import tkinter as tk
import tkinter.ttk as ttk
import tkinter.font as font
import tkinter.filedialog as filedialog
import math
import os
from PIL import Image
from PIL import ImageTk

class MyGrid:
    def my_grid(self,**kw):
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
            self.master.grid_rowconfigure(r,kw)
    
    def config_column(self,*column,**kw):
        new_kw = self.config_row_or_column(column, kw)
        for c,kw in new_kw.items():
            self.master.grid_columnconfigure(c,kw)

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

class MyMenuButton(ttk.Menubutton , MyGrid):
    def __init__(self,parent,**kw):
        super().__init__(parent,**kw)

class MySeparator(ttk.Separator , MyGrid):
    def __init__(self,parent,orient,**kw):
        # supply orient as None if orient=... keyword argument is to be used
        if not orient:
            orient = kw.pop('orient','H').lower()
        if orient == 'h':
            orient = 'horizontal'
        elif orient == 'v':
            orient = 'vertical'
        super().__init__(parent,orient=orient,**kw)

class Label(tk.Label , MyGrid):
    def __init__(self,parent,**kw):
        super().__init__(parent,**kw)

class MyLabel(ttk.Label , MyGrid):
    def __init__(self,parent,**kw):
        super().__init__(parent,**kw)

class Tree(ttk.Treeview , MyGrid):
    def __init__(self,parent,**kw):
        self.L = kw.pop('label')
        super().__init__(parent,**kw)
        self.tmp_label = Label(parent)
        self.tmp_font = font.Font(font=self.tmp_label['font'])
        self.yes='\u2714'
        self.no='\u274c'
        self.D = dict() # CORE
        self.column_names = {'class':'Class','uncat':'Uncategorized','train':'Training','valid':'Validation'}
        self.column_width = max(list([self.tmp_font.measure(i) for i in self.column_names.values()])) # CORE uniform column width +11 is a hack b.c. .measure give ~90% of actual width
        self.column_width = math.ceil(1.3*self.column_width) # 30% more width
        self['columns']=list(self.column_names.keys())
        self.filter_images = lambda x: x[x.rfind('.'):] in ('.png','.jpg','.jpeg','.tiff','.tif')
        self.filter_dir_validation = lambda x: x.lower() == 'validation'
        self.filter_dir_training = lambda x: x.lower() == 'training'
        for i,j in self.column_names.items():
            anchor = 'center'
            self.heading(i, text=j , anchor = anchor)
            self.column(i , anchor = anchor,stretch=0,width=self.column_width)
        self.column('#0',width = self.column_width // 2 , anchor = 'w')
        # class name label
        self.bind('<<TreeviewSelect>>',self.event_treeview_select)
        
    def event_treeview_select(self,e):
        #print (self,e,e.widget.focus())
        name = e.widget.focus().split('/')[0]
        self.set_class_name(name)
    def set_class_name(self,text):
        self.L['text']=f'Selected Class: "{text}"'
    def reset_class_name(self):
        self.L['text']=''
    def add_self_to_switcher(self, *args):
        self.switcher , groupname , r , c = args
        self.L.my_grid(row = r, column = c)
        r = (r[0]+1,*r[1:])
        self.button.my_grid(row = r , column = c) # CORE
        r = (r[0]+1,*r[1:])
        self.my_grid(row = r , column = c , sti = 'nswe') # CORE
        self.switcher.add_old(groupname , self.button , None , None)
        self.switcher.add_old(groupname , self , None , None)
        self.config_row(r[0],id='000',weight=0)
    def open_file_dialog(self):
        path = filedialog.askdirectory(initialdir = '.', title = '')
        #path = 'C:/Users/abdullah/Documents/a-tf-classifier/576013_1042828_bundle_archive/COVID-19 Radiography Database'
        self.resolve(path)
    
    def update_tree(self):
        c = 0
        for i,sub_dict in self.D.items():
            self.insert('', c, iid = i , values = (i,
                                                   sub_dict['uncat_count'] if sub_dict['uncat_count'] > 0 else self.no,
                                                   sub_dict['train_count'] if sub_dict['train_count'] > 0 else self.no,
                                                   sub_dict['valid_count'] if sub_dict['valid_count'] > 0 else self.no,
                                                    ) ) # CORE
            for jj,ii in enumerate(('uncat','train','valid')):
                iid = '%s/%s'%(i,ii)
                values_template = ['',]*4
                self.insert(i, jj, iid = iid , values=self.column_names[ii] )
                #self.insert(i, 1, iid = '%s/train'%i , values=self.column_names['train'] )
                for jjj,iii in enumerate(sub_dict[ii]):
                    #jjj is count
                    #iii is the FILE NAME
                    values_template[jj+1] = iii
                    self.insert(iid, jjj, values = values_template)
            
            c+=1
    
    def resolve(self,path):
        obj = os.walk(os.path.abspath(path))
        path , d , _ = next(obj)
        d = [(i,os.path.join(path,i)) for i in d]
        D = {i : {'class':i,'path':fulld , **self.subresolve(fulld)} for i,fulld in d}
#         for i,fulld in d:
#             tmp = self.subresolve(fulld)
#             D.update(tmp)
#         print(D)
        self.D = D
        self.update_tree()
        
    def subresolve(self,path , recursive_call = False):
        obj = os.walk(path)
        path , d , f = next(obj)
        
        f = list(filter(self.filter_images , f))
        if not recursive_call:
            # dtrain & dvalid are each list of of potential respective dir names.
            # ONLY 1 / 1ST DIR NAME IS CHOSEN
            dtrain = list(filter(self.filter_dir_training,d))[:1]
            dvalid = list(filter(self.filter_dir_validation,d))[:1]
        else:
            return {recursive_call : f , f'{recursive_call}_path':path , f'{recursive_call}_count': len(f)}
        
        # uncat is a LIST of image file names.
        D = dict(uncat = f , uncat_path = path , uncat_count = len(f) ) # CORE
        
        #explore files in dtrain & dvalid dirs.
        if dtrain:
            dtrain = os.path.join(path,dtrain)
            D.update( self.resolve(dtrain, 'train') )
        else:
            # train is a LIST of image file names.
            D.update( {'train' : [] , 'train_path' : None , 'train_count' : 0} )
        
        if dvalid:
            dvalid = os.path.join(path , dvalid)
            D.update( self.resolve(dvalid , 'valid') )
        else:
            D.update( {'valid' : [] , 'valid_path' : None , 'valid_count' : 0} )
        
        return D

class Middle:
    def __init__(self,parent,**kw):
        self.parent=parent
        self.groups = dict() # CORE
        self.current_groupname = None # CORE
    
    def add_new(self,groupname , class_ , **kw):
        t_args = kw.pop('t_args',tuple())
        kw_args = kw.pop('kw_args',dict())
        # t_args is tuple args
        obj = class_(self.parent,**kw_args) # CORE
        self.add_old(groupname, obj , **kw)
        return obj
    
    def add_old(self,groupname,payload, **kw):
        grid_data = kw.pop('grid_data' , None)
        show = kw.pop('show',False)
        
        if groupname not in self.groups:
            self.groups[groupname]= {'payloads': []}
        self.groups[groupname]['payloads'] += [payload]
        
        if grid_data:
            payload.my_grid(**grid_data)
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
        self.grid_data = kw.pop('grid_self',None)
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
        if self.grid_data:
            self.my_grid(**self.grid_data)
    
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

class MyPanedwindow(ttk.Panedwindow, MyGrid):
    def __init__(self,parent,**kw):
        self.grid_data = kw.pop('grid_self',None)
        super().__init__(parent,orient='horizontal',**kw)
        if self.grid_data:
            self.my_grid(**self.grid_data)

class Left(ttk.Labelframe , MyGrid):
    def __init__(self,parent,**kw):
        self.button_text = kw.pop('button_text','Button')
        self.grid_data = kw.pop('grid_data',dict())
        self.tree_args = kw.pop('Tree_args',dict())
        super().__init__(parent,text='Left',**kw)
        # button , label , tree  
        self.label = MyLabel(parent,text = '')
        self.tree = Tree(self , label = self.label , **self.tree_args)
        self.button = MyButton(self, text = self.button_text , command = self.tree.open_file_dialog)  
        if self.grid_data:
            self.my_grid(**self.grid_data)
        self.button.my_grid(row = (1,) , column = (1,) , sti = 'nswe')
        self.label.my_grid(row = (2,) , column = (1,) , sti = 'nswe')
        self.tree.my_grid(row = (3,) , column = (1,) , sti = 'nswe')
        self.button.config_row(1,2,3 , id = '1,2,3' , weight = (0,0,1))
        self.button.config_column(1,id = '1', weight = 1)
        if type(parent)==MyPanedwindow:
            parent.add(self)
            parent.add(MyButton(parent,text='1'))

class Collpasible(ttk.Labelframe , MyGrid):
    def __init__(self,parent,**kw):
        self.title = kw.pop('title','Default Title')
        self.count = kw.pop('count',1)
        super().__init__(parent,**kw)
        self['text']='Collapsible'
        self.label_title = MyLabel(self,text = self.title , anchor = 'center')
        self.label_count = MyLabel(self,text = self.count)
        self.up = '\u2b9d'
        self.label_up = MyLabel(self,text = self.up)
        # separators
        self.vsep_1 = MySeparator(self,'v')
        self.vsep_2 = MySeparator(self,'v')
        self.hsep_1 = MySeparator(self,'h')
        # do gridding
        self.label_count.my_grid(row = (1,) , column = (1,) , sti = 'w')
        self.label_title.my_grid(row = (1,) , column = (3,) , sti = 'we')
        self.label_up.my_grid(row = (1,) , column = (5,) , sti = 'e')
        self.vsep_1.my_grid(row = (1,) , column = (2,) , sti = 'nswe')
        self.vsep_2.my_grid(row = (1,) , column = (4,) , sti = 'nswe')
        self.hsep_1.my_grid(row = (2,) , column = (1,5) , sti = 'we')
        self.label_count.config_row(1,2,3 , id = '1,2,3' , weight = (0,0,1))
        self.label_count.config_column(1,2,3,4,5 , id = '1,2,3,4,5' , weight = (0,0,1,0,0))
        
        
    def set_count(self,count):
        self.count = count
        self.label_count['text']=self.count
    def set_title(self,text):
        self.title = text
        self.label_title['text']=self.title

class Models(ttk.Labelframe, MyGrid):
    def __init__(self,parent,**kw):
        super().__init__(parent,**kw)
        self.menu_addmodel = tk.Menu(self)
        self.button_addmodel = MyMenuButton(self,text='Add Model',menu=self.menu_addmodel)
        # drid
        self.button_addmodel.my_grid(row = (1,) , column = (3,) , sti = 'e')
        self.button_addmodel.config_row(1,id='1',weight = 0)
        self.button_addmodel.config_column(1,2,3,id='1,2,3',weight = (1,1,0))
        self.free_row = 2
        self.menu_addmodel.add_command(label = 'Keras Sequential' , command = self.addmodel)
    def addmodel(self):
        tmp = Collpasible(self)
        tmp.my_grid(row = (self.free_row,) , column = (1,3) , sti = 'nswe')
        
        
if __name__ == '__main__':
    root = MyTk(400,300)
    m = Middle(root) # CORE
    #PANED = MyPanedwindow(root , grid_self = {'row':(3,),'column':(1,2),'sti':'nswe'})

    t = Tabs(root , switcher = m , grid_self = {'row':(2,),'column':(1,2),'sti':'we'})
    tabnames = ['Prepare Dataset','Create Model','Results']
    t.add(tabnames[0])
    t.add(tabnames[1])
    t.add(tabnames[2])
    PANED = m.add_new(tabnames[0] , MyPanedwindow , kw_args = {'grid_self' : {'row':(3,),'column':(1,2),'sti':'nswe'} } )
    #test_label = m.add_new(tabnames[1] , Label , grid_data = {'row':(3,),'column':(1,2),'sti':'nswe'} , kw_args = {'text' : tabnames[1] , 'anchor':'center'})
    MODELS = m.add_new(tabnames[1] , Models , grid_data = {'row':(3,),'column':(1,2),'sti':'nswe'} , kw_args = {'text' : tabnames[1]} )
    t.config_column(1,2,id='1,2',weight=1) # CORE
    t.config_row(2,3,4,id = '2,3,4', weight = (0,1,0) ) # CORE
    LEFT = Left(PANED,button_text = 'Open File Dialog') # CORE
    root.sizegrip((1,),(1,100))
    root.sizegrip((4,),(1,100))
    root.mainloop()