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
            else:
                self.grid_configure({i:t})
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

class LabelFrame(tk.LabelFrame , MyGrid):
    def __init__(self,parent,**kw):
        super().__init__(parent,**kw)

class MyLabelFrame(ttk.Labelframe , MyGrid):
    def __init__(self,parent,**kw):
        super().__init__(parent,**kw)
  
class Frame(tk.Frame , MyGrid):
    def __init__(self,parent,**kw):
        super().__init__(parent,**kw)

class MyFrame(ttk.Frame , MyGrid):
    def __init__(self,parent,**kw):
        super().__init__(parent,**kw)
  



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
        provide_menu = kw.pop('provide_menu',False)
        kw.setdefault('direction','left')
        super().__init__(parent,**kw)
        if provide_menu:
            provided_menu_args = kw.pop('provide_menu_args',dict())
            provided_menu_args.setdefault('tearoff',False)
            self.the_menu = tk.Menu(parent,provided_menu_args)
            self['menu']=self.the_menu
            self.checkbutton_vars = dict()
    
    def add_command(self,**kw):
        self.the_menu.add_command(kw)
    
    def add_separator(self):
        self.the_menu.add_separator()
    
    def add_checkbutton(self,**kw):
        provide_variable = kw.pop('provide_variable',False)
        if provide_variable:
            varname = f'checkbutton_var_{kw["label"]}'
            setattr(self, varname , tk.BooleanVar(value=False))
            kw['variable'] = getattr(self, varname)

        #print(f'{kw = }')
        self.the_menu.add_checkbutton(**kw)
    
    def set_checkbutton_variable(self,name,value):
        varname = f'checkbutton_var_{name}'
        getattr(self, varname).set(value)
    
    def get_checkbutton_variable(self,name):
        varname = f'checkbutton_var_{name}'
        return getattr(self, varname).get()
    
    # implicity for BooleanVar(s) only
    def flip_checkbutton_variable(self,name):
        value = not self.get_checkbutton_variable(name)
        self.set_checkbutton_variable(name, value)
        return value

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

class MyEntry(ttk.Entry , MyGrid):
    def __init__(self,parent,**kw):
        initial_text = kw.pop('text','')
        super().__init__(parent,**kw)
        self.variable = tk.StringVar(value=initial_text)
        self['textvariable']=self.variable
    
    def set_text(self,text):
        self.variable.set(text)
    
    def get_text(self):
        return self.variable.get()

class Entry(tk.Entry , MyGrid):
    def __init__(self,parent,**kw):
        initial_text = kw.pop('text','')
        super().__init__(parent,**kw)
        self.variable = tk.StringVar(value=initial_text)
        self['textvariable']=self.variable
    
    def set_text(self,text):
        self.variable.set(text)
    
    def get_text(self):
        return self.variable.get()

    
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

class Collapsible(LabelFrame):
    full_padx = 10
    full_pady = 10
    half_pady = 5
    icon_up = '\u2b9d'
    icon_down = '\u2b9f'
    icon_x = '\u274c'
    icon_reload = '\u27f3'
    def __init__(self,parent,**kw):
        self.title = kw.pop('title','Default Title')
        self.count = kw.pop('count',None)
        self.use_count = kw.pop('use_count',False)
        self.use_x = kw.pop('use_x',False)
        self.label_last_icon = kw.pop('label_last_icon','icon_up')
        self.minimized = False
        self.count_string_template = kw.pop('count_string_template','{:4}')
        super().__init__(parent,**kw)
        self.star_frame = LabelFrame(self) #CORE main frame for "Data Shape" , etc
        self.next_row = 1
        #self['labelanchor']='n'
        #self['text']='Collapsible'
        self.label_title = MyLabel(self,text = self.title , anchor = 'center' , cursor = 'hand2')
        self.label_count = MyLabel(self , text='')
        self.label_last = Label(self,text = Collapsible.icon_x if self.use_x else getattr(Collapsible, self.label_last_icon )  , cursor = 'hand2' , anchor = 'center')
        # separators
        self.vsep_1 = MySeparator(self,'v')
        self.vsep_2 = MySeparator(self,'v')
        self.hsep_1 = MySeparator(self,'h')
        self.hsep_2 = MySeparator(self,'h')
        # do gridding
        self.hsep_1.my_grid(row = (1,) , column = (1,5) , sti = 'we')
        self.label_count.my_grid(row = (2,) , column = (1,) , sti = 'we')
        self.vsep_1.my_grid(row = (2,) , column = (2,) , sti = 'nswe')
        self.label_title.my_grid(row = (2,) , column = (3,) , sti = 'we')
        self.vsep_2.my_grid(row = (2,) , column = (4,) , sti = 'nswe')
        self.label_last.my_grid(row = (2,) , column = (5,) , sti = 'we')
        self.hsep_2.my_grid(row = (3,) , column = (1,5) , sti = 'we')
        self.star_frame.my_grid(row = (4,) , column = (1,5) , sti = 'nswe')
        self.label_count.config_row(1,2,3 , id = '1,2,3,4' , weight = (0,0,0,1))
        self.label_count.config_column(1,2,3,4,5 , id = '1,2,3,4,1' , weight = (0,0,1,0,0))
        
        self.label_title.bind('<ButtonRelease>',self.event_button_minimize)
        if self.use_count:
            self.set_count(True)
        else:
            self.vsep_1.grid_remove()
        
        if self.use_x:
            pass # IMPLEMENT DESTROY ON CLICKING "X" in SUBCLASSES
        elif self.label_last_icon == 'icon_up':
            self.label_last.bind('<ButtonRelease>',self.event_button_minimize)
        self.next_row = 5

    def set_count(self,count = None):
        # True means set count text 'automatically'
        # None -> clear count text and self.count variable
        if count is True:
            count = self.count
        elif count is None:
            count = ''
            self.count = None
        self.label_count['text']= self.count_string_template.format( count )
    
    def set_title(self,text):
        self.title = text
        self.label_title['text']=self.title

    def event_button_minimize(self,e):
        self.minimized = not self.minimized
        if self.label_last_icon == 'icon_up':
            text = (Collapsible.icon_up,Collapsible.icon_down)[self.minimized]
            self.label_last['text']=text
        method = (tk.Grid.grid,tk.Grid.grid_remove)[self.minimized]
        method(self.star_frame)

class ModelsHome(ttk.Labelframe, MyGrid):
    def __init__(self,parent,**kw):
        self.supply_model_classes = kw.pop('supply_model_classes',tuple())
        super().__init__(parent,**kw)
        self.button_addmodel = MyMenuButton(self,provide_menu = True , text='Add Model')
        for class_ in self.supply_model_classes:
            name = class_.model_name
            self.button_addmodel.add_command(label = name , command = lambda arg1 = class_ : self.addmodel(arg1))
        # drid
        self.button_addmodel.my_grid(row = (1,) , column = (3,) , sti = 'ns' , pady = Collapsible.half_pady)
        self.button_addmodel.config_row(1,id='1',weight = 0)
        self.button_addmodel.config_column(1,2,3,id='1,2,3',weight = (1,1,0))
        self.free_row = 2
        
        self.models_count = 0
        self.models_refernces = []
        
    def addmodel(self , class_ ):#**kw_args
        tmp = class_(self)# CORE **kw_args
        self.models_count += 1
        self.models_refernces += [tmp]
        tmp.my_grid(row = (self.free_row,) , column = (1,3),sti = 'nswe')
        self.free_row += 1

class Model(LabelFrame):
    def __init__(self,parent,**kw):
        super().__init__(parent,**kw)
        self.nodes = []
        self.nodes_count = 0
        #self['text']='Model'
        #self['labelanchor']='n'
        self.label_name = MyLabel(self,text='Model Name:')
        self.label_name_value = Label(self,text='')
        self.entry_name = Entry(self,relief='solid') 
        self.label_type = MyLabel(self,text='Model Type:')
        self.label_type_value = Label(self,text='')
        self.label_name_value.bind('<ButtonRelease>',self.event_button_label_type_value)
        self.label_name_value.bind('<Enter>',self.event_enter_label_type_value)
        self.label_name_value.bind('<Leave>',self.event_leave_label_type_value)
        self.menubutton_action = MyMenuButton(self,provide_menu=True,text='Action')
        self.menubutton_action.add_checkbutton(label='Collapse All',provide_variable = True , command=self.command_menubutton_action_collapse_all)
        self.entry_name.bind('<KeyPress-Return>',self.event_entry_name_return)
        self.entry_name.focus()
        #grid
        self.label_name.config_row(1,id='1',weight = 0)
        self.label_name.config_column(1,2,3,id='1,2,3',weight = (0,1,0))
        self.menubutton_action.my_grid(row = (1,2) , column = (3,) , sti = 'nswe')
        self.label_name.my_grid(row = (1,) , column = (1,) , sti = 'w')
        self.entry_name.my_grid(row = (1,) , column = (2,) , sti = 'we')
        self.label_name_value.my_grid(row = (1,) , column = (2,) , sti = 'we')
        self.label_name_value.grid_remove()
        self.label_type.my_grid(row = (2,) , column = (1,) , sti = 'e')
        self.label_type_value.my_grid(row = (2,) , column = (2,) , sti = 'we')
        self.free_row = 3
    
    def event_button_label_type_value(self,e):
        e.widget.grid_remove()
        self.entry_name.delete(0,'end')
        self.entry_name.insert(0, e.widget['text'])
        self.entry_name.grid()
    
    def event_enter_label_type_value(self,e):
        e.widget['relief'] = 'solid'
    
    def event_leave_label_type_value(self,e):
        e.widget['relief'] = 'flat'
    
    def event_entry_name_return(self,e):
        name = e.widget.get()
        if name.strip() == '':
            # from the derived class
            name = f'{self.model_name} Model {self.static_count}'
        self.label_name_value['text']=name
        e.widget.grid_remove()
        self.label_name_value.grid()
    
    def command_menubutton_action_collapse_all(self):
        # exists only to be overriden
        pass

class KerasModel(Model):
    model_name = 'Keras Sequential'
    static_count = 0
    def __init__(self,parent,**kw):
        super().__init__(parent,**kw)
        self.layers_count = 0
        KerasModel.static_count += 1
        self.label_type_value['text']=self.model_name # Model Type:Keras Sequential
        self.menubutton_action.add_separator()
        for l in ('Flatten','Convolutional','Pooling','Dense'):
            self.menubutton_action.add_command(label=f'Add a {l} Layer',command = getattr(self, f'add_{l.lower()}_layer'))
        self.layers = dict()
        #Collapsible(self,title = 'Layers')
        #self.layers.my_grid(row = (self.free_row,) , column = (1,3) , sti = 'nswe')
        self.summary = Collapsible(self,title = 'Model Summary' , label_last_icon = 'icon_reload')
        self.summary.my_grid(row = (self.free_row,) , column = (1,3) , sti = 'nswe' , padx = Collapsible.full_padx , pady = Collapsible.full_pady)
        self.free_row += 1
    
    def add_layer(self,kw1=None,kw2=dict()):
        # starting from 1
        self.layers_count += 1
        tmp = self.layers[self.layers_count] = Collapsible(self, **kw1)
        tmp.label_last.bind('<ButtonRelease>',lambda e,arg2=tmp.count : self.delete_layer(e,arg2) )
        for i,j in kw2.items():
            # row and column spans
            rs,cs = 1,1
            # row and column 
            r,c = i
            if (len_i := len(i)) == 3:
                r,rs,c = i
            if len(i) == 4:
                r,rs,c,cs = i
            widget = j.pop('class')(tmp.star_frame,**j) # CORE j is kw
            widget.config_column(1,2,3,id='1,1,1',weight=1) # once suffices
            widget.config_row(r, id = f'{r}' , weight = 1)
            widget.my_grid(row = (r,rs) , column = (c,cs) )
        self.summary.my_grid(row = (self.free_row,) ) # reorder summary as last
        tmp.my_grid(row = (self.free_row-1,) , column = (1,3) , sti = 'nswe' , padx = Collapsible.full_padx , pady = Collapsible.full_pady )
        self.free_row += 1
        
    def delete_layer(self,e,count):
        e.widget.master.destroy()
        self.free_row -= 1
    
    def add_flatten_layer(self):
        
        kw1 = {'title':'Flatten' , 
               'use_count':True , 
               'count':self.layers_count+1 ,
               'use_x':True, 
               'count_string_template' : 'Layer {:4}'}
        kw2 = {
            (1,1):{'class':MyLabel,'text':'Data Shape'},
            (1,2):{'class':Entry, 'relief':'solid'},
            (1,3): {'class':MyMenuButton, 'provide_menu':True , 'text':'Options'}
            }
        self.add_layer(kw1,kw2)
    
    def add_convolutional_layer(self):
        pass
    
    def add_pooling_layer(self):
        pass
    
    def add_dense_layer(self):
        pass
    
    def command_menubutton_action_collapse_all(self):
        value = self.menubutton_action.get_checkbutton_variable('Collapse All')
        # if True -> hide
        method = (tk.Grid.grid,tk.Grid.grid_remove)[value] # CORE
        for l in self.layers.values():
            method(l)
        method(self.summary)
    
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
    MODELS = m.add_new(tabnames[1] , ModelsHome , grid_data = {'row':(3,),'column':(1,2),'sti':'nswe'} , kw_args = {'text' : tabnames[1] , 'supply_model_classes': (KerasModel,) } )
    t.config_column(1,2,id='1,2',weight=1) # CORE
    t.config_row(2,3,4,id = '2,3,4', weight = (0,1,0) ) # CORE
    LEFT = Left(PANED,button_text = 'Open File Dialog') # CORE
    root.sizegrip((1,),(1,100))
    root.sizegrip((4,),(1,100))
    root.mainloop()