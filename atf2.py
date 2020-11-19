import tkinter as tk
import tkinter.ttk as ttk
import tkinter.font as font
import tkinter.filedialog as filedialog
import threading
import os
from PIL import Image,ImageTk
import math

class MyGrid:
    full_pad = 10
    half_pad = full_pad // 2
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
        row = [r-1 for r in row if type(r) == int]
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

class Toplevel(tk.Toplevel):
    def __init__(self,parent,visible,destroy_or_hide_on_x,**kw):
        self.visible=visible
        super().__init__(parent, **kw)
        self.set_hidden(visible)
        self.set_on_x(destroy_or_hide_on_x.lower())
    
    def set_on_x(self,destroy_or_hide):
        if destroy_or_hide == 'hide':
            self.wm_protocol("WM_DELETE_WINDOW" , func = self.hide)
    
    def set_hidden(self,x=None):
        x = x if x is not None else self.visible
        (self.hide,self.show)[self.visible]()
        
    def hide(self):
        self.withdraw()
        self.visible=False
        
    def show(self):
        self.deiconify()
        self.visible=True
        
class ImageLoading(Toplevel):
    def __init__(self,parent,**kw):
        self.parent2 = kw.pop('parent2')
        super().__init__(parent, False, 'destroy') # visivle = False
        self.title('Loading Images')
        self.internal_canvas=Canvas(self,provide_frame={'borderwidth':1},grid_data={'row':(2,),'column':(1,),'sti':'nswe'},
            provide_scrolls={'orient':'both','v_grid_data':{'row':(2,),'column':(2,),'sti':'ens'},'h_grid_data':{'row':(3,),'column':(1,2),'sti':'swe'}})
        self.internal_canvas.config_column(1,2,id='1,2',weight=(1,0))
        self.internal_canvas.config_row(1,2,id='1,2',weight=(0,1))
        self.next_row=1
        self.the_dict = dict()
        
    def setup(self):
        max_len = self.parent2.Categories['max_category_string_length']
        for name,sub_dict in self.parent2.D.items():
            collapse = Collapsible(self.internal_canvas.internal_frame,
                              count_string_template = 'Class {:4}',
                              title = name,
                              use_count = True,
                              count = self.next_row)
            collapse.my_grid(row=(self.next_row,),column=(1,),sti='nswe',padx=MyGrid.full_pad,pady=MyGrid.full_pad)
            progress = MyProgressBar(collapse.star_frame)
            loading_label1 = MyLabel(collapse.star_frame,template = '{:%d}'%max_len ,anchor='center')
            loading_label2 = MyLabel(collapse.star_frame,text = 'x.png',anchor='center')
            # grid
            self.the_dict[name] = collapse #CORE
            collapse.The_label1 = loading_label1
            collapse.The_label2 = loading_label2
            collapse.The_progress = progress
            progress.my_grid(row=(1,),column=(1,3),sti='we')
            loading_label1.my_grid(row=(2,),column=(1,3),sti='we')
            loading_label2.my_grid(row=(3,),column=(1,3),sti='we')
            if self.next_row == 1:
                # config row & columns
                pass
                collapse.config_column(1,2,id='1,2',weight=(1,0))
                collapse.config_row('all',id='all',weight=1)
            # fix later
            progress.config_column(1,2,3,id='1,2,3',weight=1)
            progress.config_row('all',id='all',weight=1)
            
            self.next_row += 1
            #collapse = MyLabel(self.internal_canvas.internal_frame,text='Loading : ')
            #tmp2 = MyLabel(self.internal_canvas.internal_frame,text=name)
            #collapse.my_grid(row=(1,),column=(1,),sti='we')
            #collapse.my_grid(row=(2,),column=(1,),sti='we')
        
    def show_summary(self):
        pass
    
    def set_label1(self,key,**kw):
        self.the_dict[key].The_label1.config(**kw)
    
    def set_label2_progress(self,key,**kw):
        self.the_dict[key].The_label2.config(**kw)
        self.the_dict[key].The_progress.step()
        
    def set_progress(self,key,**kw):
        self.the_dict[key].The_progress.config(**kw)

    def minimize(self,key):
        self.the_dict[key].event_button_minimize(None) # e=None
            
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
    
    def __init__(self, w = None , h = None , title = 'MyTk' , center:bool = True,**kw):
        provide_menu = kw.pop('provide_menu',False)
        super().__init__()
        self.title(title)
        self.resize(w, h) # to set self.w & self.h
        if center:
            self.center()
        if provide_menu:
            self.root_menu=tk.Menu(self)
            self['menu']=self.root_menu
        self.menus = {'root':self.root_menu} #CORE dict: menu_name -> tk.Menu
        self.menu_items = dict() #CORE various keys: checkbutton variables
        self.sizegrips = dict() #CORE key:row value:Sizegrip()
        

    def add_sizegrip(self,r,c):
        self.sizegrips[r[0]] = S = Sizegrip(self)
        S.my_grid(row=r,column=c,sti = 'we')
    
    def show_sizegrip(self,r):
        self.sizegrips[r].grid()
        
    def hide_sizegrip(self,r):
        self.sizegrips[r].grid_remove()
    
    def command_sizegrip(self,var,row):
        status=var.get()
        method = (self.hide_sizegrip,self.show_sizegrip)[status]
        method(row)
    
    def menu_add_command(self,on_name,**kw):
        on = self.menus[on_name]
        on.add_command(**kw)
    
    def menu_add_checkbutton(self,on_name,**kw):
        provide_variable = kw.pop('provide_variable',None)
        if provide_variable:
            tmp1 , tmp2 ,tmp3= provide_variable.pop('type') , kw.get('label') , provide_variable.pop('hide_sizegrip')
            self.menu_items.setdefault(on_name, dict())
            self.menu_items[on_name].setdefault(tmp2, dict())
            self.menu_items[on_name][tmp2]['variable'] = {'bool':tk.BooleanVar,'int':tk.IntVar}[tmp1](**provide_variable)
            kw['variable']=self.menu_items[on_name][tmp2]['variable']
            if tmp3:
                self.menu_items[on_name][tmp2]['hide_sizegrip']=tmp3
                kw['command']=lambda arg1=kw['variable'],arg2=tmp3:self.command_sizegrip(arg1, arg2)
        on = self.menus[on_name]
        on.add_checkbutton(**kw)
        
    
    def add_sub_menu(self,name,on_name,**kw):
        on = self.menus[on_name]
        new = tk.Menu(on)
        self.menus[name]=new
        on.add_cascade(menu=new,**kw)

    def menu_add_separator(self,on_name):
        on = self.menus[on_name]
        on.add_separator()

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
            self.root_menu = tk.Menu(parent,provided_menu_args)
            self['menu']=self.root_menu
            self.checkbutton_vars = dict()
    
    def add_command(self,**kw):
        self.root_menu.add_command(kw)
    
    def add_separator(self):
        self.root_menu.add_separator()
    
    def add_checkbutton(self,**kw):
        provide_variable = kw.pop('provide_variable',False)
        if provide_variable:
            varname = f'checkbutton_var_{kw["label"]}'
            setattr(self, varname , tk.BooleanVar(value=False))
            kw['variable'] = getattr(self, varname)

        #print(f'{kw = }')
        self.root_menu.add_checkbutton(**kw)
    
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

class MyScrollbar(ttk.Scrollbar , MyGrid):
        def __init__(self,parent,**kw):
            super().__init__(parent,**kw)

class Canvas(tk.Canvas , MyGrid):
    def __init__(self,parent,**kw):
        self.provide_frame = kw.pop('provide_frame',False)
        self.use_frame = kw.pop('use_frame',False)
        self.provide_scrolls = kw.pop('provide_scrolls',False)
        self.grid_data = kw.pop('grid_data',False)
        self.v_scroll = None
        self.h_scroll = None
        super().__init__(parent,**kw)
        if self.provide_frame:
            self.internal_frame = Frame(self,**self.provide_frame) #provide_frame dict() kw
            self.internal_frameid = self.create_window(0,0,window=self.internal_frame,anchor='nw')
            self.bind('<Configure>',self.event_configure)
        if self.provide_scrolls:
            # provide_scrolls : dict and has location in parent to grid scrollbars to
            orient = self.provide_scrolls.pop('orient',False)
            parent = self.provide_scrolls.pop('parent',parent)
            if orient:
                orient = ((orient,),('v','h'))[orient=='both']
                if 'v' in orient:
                    self['yscrollcommand']=self.v_scroll
                    self.v_scroll = MyScrollbar(parent,orient='vertical',command = self.yview)
                    if self.provide_scrolls.get('v_grid_data',None):
                        self.v_scroll.my_grid(**self.provide_scrolls['v_grid_data'])
                if 'h' in orient:
                    self['xscrollcommand']=self.h_scroll
                    self.h_scroll = MyScrollbar(parent,orient='horizontal',command = self.xview)
                    if self.provide_scrolls.get('v_grid_data',None):
                        self.h_scroll.my_grid(**self.provide_scrolls['h_grid_data'])
                
        if self.grid_data:
            self.my_grid(**self.grid_data)
    
    def event_configure(self,e):
        self.itemconfig(self.internal_frameid, width=e.width,height=e.height)
        self['scrollregion']=self.bbox('all')
        
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
        self.template = kw.pop('template',None)
        self.provide_variable = kw.pop('provide_variable',False)
        super().__init__(parent,**kw)
        if self.provide_variable:
            self.internal_variable = tk.StringVar(value = kw.get('text',''))
            self['textvariable'] = self.internal_variable
        self.backup_text = None
    
    def set_text(self,text):
        if self.template is not None:
            text = self.template.format(text)
        if self.provide_variable:
            self.internal_variable.set(text)
        else:
            self['text'] = text
        self.backup_text = text
    
    def get_text(self):
        return self.backup_text

class Tree(ttk.Treeview , MyGrid):
    def __init__(self,parent,**kw):
        self.parent2 = kw.pop('parent2')
        super().__init__(parent,**kw)
        
        self.tmp_font = font.Font(font=self.master.class_label['font'])
        self.yes='\u2714'
        self.no='\u274c'
        #self.D = dict() # access from self.parent2.D
        self.column_names = ('Class',)+self.parent2.Categories['tuple_categories']
        self.column_width = max(list([self.tmp_font.measure(i) for i in self.column_names])) # CORE uniform column width +11 is a hack b.c. .measure give ~90% of actual width
        #self.column_width = math.ceil(1.3*self.column_width) # 30% more width
        self['columns']=self.column_names
        self.filter_images = lambda x: x[x.rfind('.'):] in ('.png','.jpg','.jpeg','.tiff','.tif','.gif')
        self.filter_dir_validation = lambda x: x.lower() == 'validation'
        self.filter_dir_training = lambda x: x.lower() == 'training'
        for i in self.column_names:
            anchor = 'center'
            self.heading(i, text=i , anchor = anchor)
            self.column(i , anchor = anchor,stretch=0,width=self.column_width)
        self.column('#0',width = self.column_width // 2 , anchor = 'w')
        # class name label
        self.bind('<<TreeviewSelect>>',self.event_treeview_select)

    def event_treeview_select(self,e):
        #print (self,e,e.widget.focus())
        name = e.widget.focus().split('/')[0]
        self.parent2.class_selected(name)
  
    def update_tree(self):
        c = 0
        for i,sub_dict in self.parent2.D.items():
            values = [cat['count'] if (cat['count'] is not None) else self.no for (cat_name,cat) in sub_dict.items() ]
            #print(values)
            self.insert('', c, iid = i , values = (i, *values )) # CORE
            for cat_count,cat in self.parent2.Categories['count_categories']:
                iid = '%s/%s'%(i,cat)
                values_template = ['',]*len(self.column_names)
                #print(values_template)
                self.insert(i, cat_count, iid = iid , values = cat )
                #self.insert(i, 1, iid = '%s/train'%i , values=self.column_names['train'] )
                for file_count,file_name in enumerate(sub_dict[cat]['images']):
                    values_template[cat_count] = file_name
                    self.insert(iid, file_count, values = values_template)
            
            c+=1
        
    def resolve(self,path):
        obj = os.walk(os.path.abspath(path))
        self.sub_resolve(path)
        self.update_tree()
        print(self.parent2.D)
        print('tree->resolved')
        self.parent2.tree_has_resolved()

    def sub_resolve(self,root_path):
        _ , d , f = next(os.walk(root_path)) #StopIteration if root_path DNE
        joined_paths = [(class_name,os.path.join(root_path,class_name)) for class_name in d]
        self.parent2.D = {class_name:dict() for class_name in d}
        # Uncat
        
        for class_name,class_path in joined_paths:
            _ , d , f = next(os.walk(class_path))
            f = list(filter(self.filter_images , f))
            first_category = self.parent2.Categories['tuple_categories'][0]
            self.parent2.D[class_name][first_category] = dict( images = f , count = len(f) , path = class_path )
            # REST of categories
            # ONCE to guard against UNIX cases-sensitive folder names
            for cat in self.parent2.Categories['tuple_categories'][1:]:
                if cat_lower := cat.lower() in d:
                    if cat not in self.parent2.D[class_name]:
                        new_path = os.path.join(class_path,cat_lower)
                        _ , _ , f = next(os.walk(new_path))
                        f = list(filter(self.filter_images , f))
                        self.parent2.D[class_name][cat] = dict(images = f , count = len(f) , path = new_path)
                else:
                    self.parent2.D[class_name][cat] = dict(images = [] , count = None , path = None)
        
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
        self.balance_fraction = kw.pop('self.balance_fraction',0.5)
        self.balance_active = kw.pop('self.balance_active',False)
        super().__init__(parent,orient='horizontal',**kw)
        self.user_moved = False
        if self.grid_data:
            self.my_grid(**self.grid_data)
        self.bind('<B1-Motion>',self.event_dragged)

    def balance_activate(self,fraction=None):
        if fraction:
            self.balance_fraction = fraction
        if not self.balance_active:
            self.bind('<Configure>',self.event_configure)
        self.balance_active = True
        
        
    def balance_deactivate(self,fraction=None):
        if fraction:
            self.balance_fraction = fraction
        self.balance_active = False
        self.bind('<Configure>',self.event_configure)
        
    def set_sash_balance(self,fraction):
        self.balance_fraction = fraction
        
    def event_configure(self,e):
        if self.balance_active:
            self.sashpos(0, round(e.width * self.balance_fraction))
        
    def event_dragged(self,e):
        self.user_moved = True
        width = self.winfo_width()
        self.balance_fraction = (self.sashpos(0) / width)
        
class MyProgressBar(ttk.Progressbar , MyGrid):
    def __init__(self,parent,**kw):
        provide_variable = kw.pop('provide_variable',False)
        super().__init__(parent,**kw)
        if provide_variable:
            self.internal_variable = tk.IntVar()

class MyScale(ttk.Scale , MyGrid):
    def __init__(self,parent,**kw):
        provide_variable = kw.pop('provide_variable',False)
        super().__init__(parent,**kw)
        if provide_variable:
            self.internal_variable = tk.IntVar()

class Left(MyFrame):
    def __init__(self,parent,**kw):
        self.Categories = kw.pop('Categories')
        self.button_text = kw.pop('button_text','Button')
        self.grid_data = kw.pop('grid_data',dict())
        self.tree_args = kw.pop('tree_args',dict())
        self.props = kw.pop('props',dict())
        self.right_instance = None
        self.D = dict()
        super().__init__(parent,**kw)
        self.img_loading=ImageLoading(root,parent2 = self)
        #self['text']='Left'
        #self['labelanchor']='s'
        
        # button , label , tree
        self.class_label_frame = MyLabelFrame(self,text='Selected Class',labelanchor='n')
        self.class_label = MyLabel(self.class_label_frame,text = '',anchor='center')
        self.tree = Tree(self, parent2 = self ,  **self.tree_args)
        self.button = MyButton(self, text = self.button_text , command = self.open_file_dialog)  
        if self.grid_data:
            self.my_grid(**self.grid_data)
        self.class_label.my_grid(row = (1,) , column = (1,) , sti = 'nswe')
        self.class_label.config_row(1,id='1',weight=0)
        self.class_label.config_column(1,id='1',weight=1)
        self.class_label_frame.my_grid(row = (1,) , column = (1,) , sti = 'nswe')
        self.button.my_grid(row = (2,) , column = (1,) , sti = 'nswe')
        self.tree.my_grid(row = (3,) , column = (1,) , sti = 'nswe')
        self.button.config_row(1,2,3 , id = '1,2,3' , weight = (0,0,1))
        self.button.config_column(1,id = '1', weight = 1)
        if type(parent)==MyPanedwindow:
            parent.add(self)
    
    def set_right_instance(self,r):
        self.right_instance = r
        self.right_instance.set_parent2(self)
    
    def tree_has_resolved(self):
        #print('Left->tree_has_resolved')
        self.right_instance.setup_galleries() # reads self.parent2.D 
    
    def open_file_dialog(self):
        #path = filedialog.askdirectory(initialdir = '.', title = '')
        #path = 'C:/Users/abdullah/Documents/a-tf-classifier/576013_1042828_bundle_archive/COVID-19 Radiography Database'
        path = '/home/abdullah/eclipse-workspace'
        self.tree.resolve(path) # Modifies self.D from Tree instance
        self.img_loading.setup() # CORE
        self.img_loading.show()
        self.start_loading(True) # close_after = True
    
    def thread_start_loading(self,close_after=False):
        for name,sub_dict in self.D.items():
            for cat_name,cat in sub_dict.items():
                self.D[name][cat_name]['image_objects'] = dict()
                self.D[name][cat_name]['image_tk_objects'] = dict()
                self.D[name][cat_name]['thumb_tk_objects'] = dict()
                if max_count := cat['count']: # B.C. naively join the path and file names list does not always work.
                    self.img_loading.set_label1(name,text=cat_name)
                    self.img_loading.set_progress(name,maximum=max_count)
                    parent_path = cat['path']
                    for NAME , PATH in  ((f,os.path.join(parent_path,f)) for f in cat['images']):
                        tmp = self.D[name][cat_name]['image_objects'][NAME] = Image.open(PATH)
                        self.D[name][cat_name]['image_tk_objects'][NAME] = ImageTk.PhotoImage(tmp)
                        self.D[name][cat_name]['thumb_tk_objects'][NAME] = ImageTk.PhotoImage(tmp.resize(self.props['thumbnail_size']))
                        self.img_loading.set_label2_progress(name,text=NAME)
            self.img_loading.minimize(name)
        #print(self.tree.D)
        if close_after:
            self.img_loading.hide()
    
    def start_loading(self,close_after = False):
        args=[close_after]
        threading.Thread(target=self.thread_start_loading,args=args).start()
        
    def class_selected(self,text):
        self.class_label['text']=f'"{text}"'
        # Should trigger right_instance
        self.right_instance.class_selected(text)
    def clear_class_name(self):
        self.class_label['text']=''
    
class Gallery(MyLabelFrame):
    def __init__(self,parent,**kw):
        for i in (('thumbnail_size',(50,50)),('provide_scrolls','v'),'provide_progress','provide_scale','max_class_name','class_name','cat_name'):
            j = ((i,),i)[type(i) == tuple]
            setattr(self, j[0], kw.pop(*j))
        super().__init__(parent,**kw)
        self.internal_canvas = Canvas(self ,provide_scrolls = {'orient':'v','parent':self,
                                                                'v_grid_data': {'row':(1,2),'column':(4,),'sti':'ens'} })
        self.D = None
        self.internal_canvas.config_column(1,2,3,4,id='1,2,3,4',weight=(1,1,1,0))
        self.internal_canvas.config_row(1,2,id='1,2',weight=(0,1))
        self.menubutton_actions = MyMenuButton(self , provide_menu = True , text = 'Actions')
        self.menubutton_actions.my_grid(row=(1,),column=(3,),sti = 'e')
        self.internal_canvas.my_grid(row=(2,),column=(1,3),sti = 'nswe')
        if self.provide_progress:
            self.progress = MyProgressBar(self,orient='horizontal',provide_variable=True)
            self.progress.my_grid(row=(1,),column=(1,4),sti = 'we')
            self.progress.grid_remove()
        if self.provide_scale:
            self.scale = MyScale(self)
            self.scale_label = MyLabel(self,text = '1 x 1')
            self.scale.my_grid(row=(1,),column=(1,),sti = 'we')
            self.scale_label.my_grid(row=(1,),column=(2,),sti = 'we')
        
        self.countofilename = dict() # CORE dict: key:filename value:count
        self.imgs = dict() #CORE dict:  key:count (from 1) value:PILLOW objects
        self.imgs_count=0
        self.selected_count=0
        self.set_title()
    
    def set_title(self):
        t = '{:4} {:{max_count}} images | {:4} selected'.format(self.imgs_count,self.cat_name,self.selected_count,max_count=self.max_class_name)
        
        self['text']=t
    
    def hide(self):
        self.grid_remove()
        
    def show(self):
        self.grid()
    
       
        
class Right(MyFrame):
    def __init__(self,parent,**kw):
        self.props = kw.pop('props',dict())
        self.props.setdefault('current class name',None)
        self.props.setdefault('gallery title template',None)
        self.props.setdefault('width stored',None)
        self.props.setdefault('next row',None)
        self.parent2 = None
        #self.thumbnail_size = (50,50)
        super().__init__(parent,**kw)
        if type(parent)==MyPanedwindow:
            parent.add(self)
        #self.gallery_title_template=None
        #self.count_max = len(self.supplied_categories)
        #self.tmp_button = MyButton(self)
        #self.tmp_button.config_column(1,2,id='1,2',weight=(1,0))
        #self.tmp_button.config_row(1,2,3,id='1',weight=1)
        #self.ginfo = dict() # CORE ; gallery_info 'MAPPED?';LAST X,Y
        self.classes = dict() # CORE dict key:name value:Gallery()
        self.bind('<Configure>',self.store_width,add='+') # + just in case
    
    def set_parent2(self, x ):
        self.parent2 = x
    
    def store_width(self,e):
        pass
        #print('store_width->method',e.widget.winfo_width())
        #self.props['width stored'] = e.widget.winfo_width()
        #print('ACTUAL store_width',self.width_stored)
        self.resize_canvas()

    def setup_galleries(self):
        # has self.D been inserted?
        try:
            self.parent2.D
        except:
            print('Right Instance says: "self.parent2.D" not found')
            return
        
        for class_name,the_dict in self.parent2.D.items():
            category_count = 1
            if class_name not in self.classes:
                self.classes[class_name] = {'mapped' : False  , 'filled':False , 'galleries': dict()}
            for category_name,the_dict2 in the_dict.items():
                self.classes[class_name]['galleries'][category_name] = tmp = Gallery(self,
                                                                    class_name = class_name ,
                                                                    cat_name = category_name , 
                                                                    max_class_name = self.parent2.Categories['max_category_string_length'] , 
                                                                    provide_progress = True , 
                                                                    provide_scale = True , 
                                                                    provide_scrolls = True)
                tmp.internal_canvas.create_rectangle((0,0,*self.parent2.props['thumbnail_size']),stipple='gray12',fill='blue',tag='box',state='hidden')
                tmp.internal_canvas.bind('<Button-1>',self.internal_clicked)
                #print(tmp,category_count)
                tmp.my_grid(row = (category_count,) , column = (1,) , sti = 'nswe')
                #self.grid_rowconfigure(category_count, uniform = 'one' , weight = 1 )
                tmp.config_row(category_count,id='one',weight=1)
                tmp.config_column(1,2,id='1,2',weight=(1,0))
                tmp.grid_remove()
            
                category_count += 1
    
    
    def class_selected(self,the_class_name):
        #if the_class_name is None:
        #    return
        #print('class_selected',the_class_name, self.classes[the_class_name])
        
        if self.props['current class name'] == the_class_name :
            return
        
        self.props['current class name'] = the_class_name
        # Hide All
        for class_name , the_dict in self.classes.items():
            for category_name , gallery in the_dict['galleries'].items():
                #print('removing:',class_name,category_name)
                gallery.grid_remove()
        # Show This Class
        for category_name , gallery in self.classes[the_class_name]['galleries'].items():
            #print(category_name,gallery)
            #print('showing:',the_class_name,category_name)
            gallery.grid()
        
        self.after(100, lambda : self.fill_canvas() )
        
    def fill_canvas(self , class_name = None):
        
        if class_name is None:
            class_name = self.props['current class name']
            #print('fill_canvas',class_name, self.classes[class_name])
            if class_name is None:
                return
        
        if self.classes[class_name]['filled'] is True:
            return
        
        threading.Thread(target = self.thread_fill_canvas , args = (class_name,) ).start()
    
    def thread_fill_canvas(self , the_class_name):# Places thumb_tk_objects image objects on 9 canvases
    
        sample_width = None # because when one class is selected, it mapped/width width is used, others are width=1 since they are unmapped 
        for class_name,sub_dict in self.parent2.D.items():
            for cat_name,the_dict in sub_dict.items():
                gallery = self.classes[class_name]['galleries'][cat_name]
                if the_class_name == class_name and sample_width is None:
                    sample_width = gallery.internal_canvas.winfo_width()
                obj = self.coords(self.parent2.props['thumbnail_size'] , sample_width )
                count=1
                self.parent2.D[class_name][cat_name]['canvas_id_to_filename'] = dict() # Modifies self.D from Tree instance
                for file_name,tkimg in the_dict['thumb_tk_objects'].items():
                    x,y = next(obj)
                    #print(class_name,cat_name,count,x,y)
                    canvas_id = gallery.internal_canvas.create_image(x,y,image=tkimg,anchor='nw')
                    #gallery.internal_canvas.tag_bind(canvas_id , '<Button-1>' , lambda e: print('Clicked',e))
                    self.parent2.D[class_name][cat_name]['canvas_id_to_filename'][canvas_id] = file_name # Modifies self.D from Tree instance
                    count += 1
        #print( self.parent2.D )
            self.classes[class_name]['filled'] = True
    def resize_canvas(self , class_name = None):
        print('*'*100)
        print('resize_canvas',class_name)
        print('*'*100)
        if class_name is None:
            class_name = self.props['current class name']
            if class_name is None:
                return
        if self.classes[class_name]['filled'] is False:
            return
        threading.Thread(target = self.thread_resize_canvas , args = (class_name,)).start()
    
    def thread_resize_canvas(self , class_name):
        for category_name , gallery in self.classes[class_name]['galleries'].items():
            obj = self.coords(None, gallery.internal_canvas.winfo_width() )
            for the_id , xy in zip ( self.parent2.D[class_name][category_name]['canvas_id_to_filename'].keys() , obj ):
                x , y = xy
                print('thread_resize_canvas, x,y:',x,y)
                gallery.internal_canvas.moveto(the_id, x = x , y= y)
        
    
    def coords(self , thumb_size , width = None , pad=(MyGrid.full_pad,MyGrid.full_pad) ):
        width = self.props['width stored'] if width is None else width
        thumb_size = thumb_size if thumb_size is not None else self.parent2.props['thumbnail_size']
        #print(thumb_size)
        thumb_x , thumb_y = thumb_size
        pad_x , pad_y = pad
        per_row = math.floor( width / (thumb_x + pad_x) )
        space_left = width - (per_row * (thumb_x + pad_x)) # should >=1 , Because per_row will be 0
        start_x = space_left // 2
        # Algorithm using space_left: whatever hasbeen left , divide it by 2 then make start_x
        # print('width:',width,'per_row:',per_row,'space_left',space_left,'start_x',start_x)

        y = pad_y
        while True:
            for x in range(start_x , start_x + ( per_row*(per_row > 0 ) + 1*(per_row <= 0) )*thumb_x , thumb_x + pad_x):
                yield(x,y)
            y += pad_y + thumb_y
        
    def coords0(self,width=None,t_size=None,count=None,start=(0,0,0),pad=(MyGrid.full_pad,MyGrid.full_pad)): #thumbnail_size
        tx , ty = t_size
        x1,x2,y = start
        px , py = pad
        i = True
        for x in range(x1 , width - tx - px , tx ):
            yield (x + (px,0)[i] ,y)
            count -= 1
            i = False
        i = True
        y += ty + py
        while count > 0:
            for x in range(x2 , width - tx - px , tx ):
                yield (x + (px,0)[i] ,y)
                count -= 1
                y += ty + py
        
    def internal_clicked(self,e):
        x,y = e.widget.canvasx(e.x),e.widget.canvasy(e.y)
        print('Clicked',e.x_root,e.y_root,x,y)
        
class Collapsible(LabelFrame):
    icon_up =   '\u2b9d'
    icon_down = '\u2b9f'
    icon_x = '\u274c'
    icon_reload = '\u27f3'
    def __init__(self,parent,**kw):
        self.title = kw.pop('title','Default Title')
        self.count = kw.pop('count',None)
        self.use_count = kw.pop('use_count',False)
        self.use_x = kw.pop('use_x',False)
        self.label_last_empty_bg = None
        self.label_last_icon = kw.pop('label_last_icon',('icon_up','icon_x')[self.use_x])
        self.minimized = False
        self.minimized_icon = Collapsible.icon_up
        self.count_string_template = kw.pop('count_string_template','{:4}')
        super().__init__(parent,**kw)
        self.star_frame = Frame(self,relief='flat',borderwidth=MyGrid.half_pad) #CORE main frame for "Data Shape" , etc
        self.next_row = 1
        #self['labelanchor']='n'
        #self['text']='Collapsible'
        self.label_title = MyLabel(self,text = self.title , anchor = 'center' , cursor = 'hand2' , borderwidth = MyGrid.half_pad)
        self.label_title_backup = self.label_title['text']
        self.label_count = MyLabel(self , text='')
        self.label_last = Label(self,text = Collapsible.icon_x if self.use_x else getattr(Collapsible, self.label_last_icon )  , cursor = 'hand2' , anchor = 'center')
        # separators
        self.vsep_1 = MySeparator(self,'v')
        self.vsep_2 = MySeparator(self,'v')
        self.hsep_1 = MySeparator(self,'h')
        self.hsep_2 = MySeparator(self,'h')
        # do gridding
        #self.hsep_1.my_grid(row = (1,) , column = (1,5) , sti = 'we')
        self.label_count.my_grid        (row = (2,) , column = (1,) , sti = 'we')
        self.vsep_1.my_grid             (row = (2,) , column = (2,) , sti = 'nswe')
        self.label_title.my_grid        (row = (2,) , column = (3,) , sti = 'we')
        self.vsep_2.my_grid             (row = (2,) , column = (4,) , sti = 'nswe')
        self.label_last.my_grid         (row = (2,) , column = (5,) , sti = 'we')
        self.hsep_2.my_grid             (row = (3,) , column = (1,5) , sti = 'we')
        self.star_frame.my_grid         (row = (4,) , column = (1,5) , sti = 'nswe')
        self.label_count.config_row(1,2,3 , id = '1,2,3,4' , weight = (0,0,0,1))
        self.label_count.config_column(1,2,3,4,5 , id = '1,2,3,4,1' , weight = (0,0,1,0,0))
        self.label_title.bind('<Enter>',self.event_entry_label_title)
        self.label_title.bind('<Leave>',self.event_leave_label_title)
        self.label_title.bind('<ButtonRelease>',self.event_button_minimize)
        if self.use_count:
            self.set_count(True)
        else:
            self.vsep_1.grid_remove()
        
        if self.use_x:
            pass # IMPLEMENT DESTROY ON CLICKING "X" in SUBCLASSES
            self.label_last.bind('<Enter>',self.event_entry_label_last_x)
            self.label_last.bind('<Leave>',self.event_leave_label_last_x)
            #self.label_last['borderwidth'] = MyGrid.half_pad
            self.label_last_empty_bg = self.label_last['bg']
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
        self.minimized_icon = (Collapsible.icon_up,Collapsible.icon_down)[self.minimized]
        if self.label_last_icon == 'icon_up':
            text = (Collapsible.icon_up,Collapsible.icon_down)[self.minimized]
            self.label_last['text']=text
        self.label_title.event_generate('<Enter>')
        self.label_title['borderwidth'] += ((+1,-1)[self.minimized])
        method = (tk.Grid.grid,tk.Grid.grid_remove)[self.minimized]
        method(self.star_frame)
        
    def event_entry_label_title(self,e):
        #print(e)
        e.widget['text'] = f"{self.minimized_icon}{self.minimized_icon}{self.minimized_icon} {self.label_title_backup} {self.minimized_icon}{self.minimized_icon}{self.minimized_icon}"
    
    def event_leave_label_title(self,e):
        e.widget['text']=self.label_title_backup
    
    
    def event_entry_label_last_x(self,e):
        self.label_last['relief'] = 'raised'
        self.label_last['background']='red'
    
    def event_leave_label_last_x(self,e):
        self.label_last['relief'] = 'flat'
        self.label_last['background']=self.label_last_empty_bg
        

class ModelsHome(ttk.Labelframe, MyGrid):
    def __init__(self,parent,**kw):
        self.supply_model_classes = kw.pop('supply_model_classes',tuple())
        super().__init__(parent,**kw)
        self.internal_canvas = Canvas(self,provide_frame={'relief':'ridge'},
                                      grid_data = {'row':(2,3),'column':(1,3),'sti':'nswe'},
                                      provide_scrolls={'orient':'both',
                                                       'v_grid_data':{'row':(2,),'column':(4,),'sti':'ens'},
                                                       'h_grid_data':{'row':(3,),'column':(1,4),'st':'swe'}})
        self.button_addmodel = MyMenuButton(self,provide_menu = True , text='Add Model')
        for class_ in self.supply_model_classes:
            name = class_.model_name
            self.button_addmodel.add_command(label = name , command = lambda arg1 = class_ : self.addmodel(arg1))
        # drid
        self.button_addmodel.my_grid(row = (1,) , column = (1,4) , sti = 'we' , pady = MyGrid.half_pad)
        self.button_addmodel.config_row(1,2,id='1,2',weight = (0,1))
        self.button_addmodel.config_column(1,2,3,id='1,2,3,4',weight = (1,1,0,0))
        # for internal_frame
        self.free_row = 1
        self.count_models = 0
        self.ref_models = dict()
    def addmodel(self , class_ ):#**kw_args
        tmp = class_(self.internal_canvas.internal_frame)# CORE **kw_args
        if self.count_models == 0:
            tmp.config_column(1,id='1',weight=1,pad=10)
            #tmp.config_row('all',pad=100)# NOT WORKING
        self.count_models += 1
        self.ref_models[self.count_models]=tmp
        tmp.my_grid(row = (self.free_row,) , column = (1,),sti = 'nswe', pady = MyGrid.half_pad , padx = MyGrid.full_pad)
        self.free_row += 1

class Model(MyFrame):
    def __init__(self,parent,**kw):
        super().__init__(parent,**kw)
        self.nodes = []
        self.nodes_count = 0
        self.count_columns = 4
        #self['text']='Model'
        #self['labelanchor']='n'
        self['borderwidth']=5
        self['relief']='raised'
        self.label_colon1 = MyLabel(self,text=' : ')
        self.label_colon2 = MyLabel(self,text=' : ')
        self.label_name = MyLabel(self,text='Model Name')
        self.label_name_value = MyLabel(self,text='',anchor='w')
        self.entry_name = Entry(self,relief='solid') 
        self.label_type = MyLabel(self,text='Model Type')
        self.label_type_value = MyLabel(self,text='',anchor='w')
        self.label_name_value.bind('<ButtonRelease>',self.event_button_label_type_value)
        self.label_name_value.bind('<Enter>',self.event_enter_label_type_value)
        self.label_name_value.bind('<Leave>',self.event_leave_label_type_value)
        self.menubutton_action = MyMenuButton(self,provide_menu=True,text='Action')
        self.menubutton_action.add_checkbutton(label='Collapse All',provide_variable = True , command=self.command_menubutton_action_collapse_all)
        self.entry_name.bind('<KeyPress-Return>',self.event_entry_name_return)
        self.entry_name.focus()
        #grid
        self.label_name.config_row(1,id='1',weight = 0)
        self.label_name.config_column(1,2,3,4,id='1,2,3,4',weight = (0,0,1,0))
        self.menubutton_action.my_grid      (row = (1,2) , column = (4,) , sti = 'nswe')
        self.label_name.my_grid             (row = (1,) , column = (1,) , sti = 'w')
        self.label_colon1.my_grid           (row = (1,) , column = (2,) , sti = 'w')
        self.entry_name.my_grid             (row = (1,) , column = (3,) , sti = 'we')
        self.label_name_value.my_grid       (row = (1,) , column = (3,) , sti = 'we')
        self.label_name_value.grid_remove()
        self.label_type.my_grid             (row = (2,) , column = (1,) , sti = 'w')
        self.label_colon2.my_grid           (row = (2,) , column = (2,) , sti = 'w')
        self.label_type_value.my_grid       (row = (2,) , column = (3,) , sti = 'we')
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
        for l in ('Flatten','2D Convolutional','Pooling','Dense'):
            l_method_name = '_'.join(l.lower().split())
            self.menubutton_action.add_command(label=f'Add a {l} Layer',command = getattr(self, f'add_{l_method_name}_layer'))
        self.layers = dict()
        #Collapsible(self,title = 'Layers')
        #self.layers.my_grid(row = (self.free_row,) , column = (1,3) , sti = 'nswe')
        self.summary = Collapsible(self,title = 'Model Summary' , label_last_icon = 'icon_reload')
        self.summary.my_grid(row = (self.free_row,) , column = (1,self.count_columns) , sti = 'nswe' , padx = MyGrid.full_pad , pady = MyGrid.full_pad)
        self.free_row += 1
    
    def add_layer(self,kw1=None,kw2=dict()):
        # starting from 1
        self.layers_count += 1
        tmp = self.layers[self.layers_count] = Collapsible(self, **kw1)
        tmp.label_last.bind('<ButtonRelease>',lambda e,arg2=tmp.count : self.delete_layer(e,arg2) ) #CORE
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
        tmp.my_grid(row = (self.free_row-1,) , column = (1,self.count_columns) , sti = 'nswe' , padx = MyGrid.full_pad , pady = MyGrid.full_pad )
        self.free_row += 1
        
    def delete_layer(self,e,count):
        del self.layers[count]
        e.widget.master.destroy()
        self.free_row -= 1
        self.layers_count -= 1
        
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
    
    def add_2d_convolutional_layer(self):
        kw1 = {'title':'2D Convolution' , 
               'use_count':True , 
               'count':self.layers_count+1 ,
               'use_x':True, 
               'count_string_template' : 'Layer {:4}'}
        kw2 = {
            (1,1):{'class':MyLabel,'text':'Data Shape'},
            (1,2):{'class':Entry, 'relief':'solid'},
            (1,3): {'class':MyMenuButton, 'provide_menu':True , 'text':'Options'},
            (2,1):{'class':MyLabel,'text':'Convolution Iteration(s)'},
            (2,2):{'class':Entry, 'relief':'solid'},
            (2,3): {'class':MyMenuButton, 'provide_menu':True , 'text':'Options'},
            (3,1):{'class':MyLabel,'text':'Filter Size'},
            (3,2):{'class':Entry, 'relief':'solid'},
            (3,3): {'class':MyMenuButton, 'provide_menu':True , 'text':'Options'},
            (4,1):{'class':MyLabel,'text':'Activation Function'},
            (4,2):{'class':Entry, 'relief':'solid'},
            (4,3): {'class':MyMenuButton, 'provide_menu':True , 'text':'Options'},
            }
        self.add_layer(kw1,kw2)
    
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
    root = MyTk(400,300,provide_menu=True)
    m = Middle(root) # CORE
    #PANED = MyPanedwindow(root , grid_self = {'row':(3,),'column':(1,2),'sti':'nswe'})

    t = Tabs(root , switcher = m , grid_self = {'row':(2,),'column':(1,2),'sti':'we'})
    tabnames = ['Prepare Dataset','Create Model','Results']
    t.add(tabnames[0])
    t.add(tabnames[1])
    t.add(tabnames[2])
    PANED = m.add_new(tabnames[0] , MyPanedwindow , kw_args = {'grid_self' : {'row':(3,),'column':(1,2),'sti':'nswe'} } )
    PANED.balance_activate()
    #test_label = m.add_new(tabnames[1] , Label , grid_data = {'row':(3,),'column':(1,2),'sti':'nswe'} , kw_args = {'text' : tabnames[1] , 'anchor':'center'})
    MODELS = m.add_new(tabnames[1] , ModelsHome , grid_data = {'row':(3,),'column':(1,2),'sti':'nswe'} , kw_args = {'text' : tabnames[1] , 'supply_model_classes': (KerasModel,) } )
    t.config_column(1,2,id='1,2',weight=1) # CORE
    t.config_row(2,3,4,id = '2,3,4', weight = (0,1,0) ) # CORE
    Categories_Tuple = ('Uncategorized','Training','Validation') # CORE
    Categories = {'count_categories':[(j+1,i) for j,i in enumerate(Categories_Tuple)],
                   'tuple_categories':Categories_Tuple[:],
                   'max_category_string_length':max([len(i) for i in Categories_Tuple])
                   }
    LEFT = Left(PANED,button_text = 'Open File Dialog' , Categories = Categories , props = {'thumbnail_size' : (50,50)}) # CORE
    RIGHT = Right(PANED) # CORE
    LEFT.set_right_instance(RIGHT)
    root.add_sizegrip((1,),(1,100))
    root.add_sizegrip((4,),(1,100))
    root.add_sub_menu('initial', 'root',label='Initial')
    root.add_sub_menu('ui settings', 'root',label='UI Settings')
    root.menu_add_command('initial',label='Select Classes Dir.',command=LEFT.open_file_dialog)
    root.menu_add_checkbutton('ui settings',label='Upper Sizegrip',provide_variable={'type':'bool','value':1,'hide_sizegrip':1})
    root.menu_add_checkbutton('ui settings',label='Lower Sizegrip',provide_variable={'type':'bool','value':1,'hide_sizegrip':4})
    root.menu_add_separator('ui settings')
    root.mainloop()