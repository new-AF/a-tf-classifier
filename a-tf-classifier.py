#-------------------------------------------------------------------------------
# Name:     a-tf-classifier.py
# Purpose:  a gui fontend for tensorflow
# Author:   abdullah fatota
#-------------------------------------------------------------------------------
import tkinter as tk
import tkinter.ttk as ttk
import math

import time
import threading

from tkinter import filedialog
from tkinter import messagebox
from PIL import Image as PIL_Image
from PIL import ImageTk as PIL_Image_tk

put = print
for i in 'x bottom left right top y both none'.split():
    globals()[i.upper()]=i

BLUE,RED,YELLOW,GREEN = 'blue red yellow green'.split()

# for getcwd
import os
import time

#supersedes _pack and _geomTranslator
class Packer:
    def __init__(self,target,*tupl,**kw):
        self.args = dict()
        self.widget=target
        self.on=kw.pop('show',0)
        for i in tupl:
            if type(i) == str:
                self.args.update(self.decipher(i))
        self.args.update(kw)
        if self.on:
            self.show()
    def decipher(self,string):
        news = dict()
        for i in string.split(';'):
            a,b = [str.strip(j) for j in i.split('=')]
            if a in 'fill side'.split():
                pass
            news[a]=b
        return news
    def quotehide(self):
        if not self.on:
            return
        self.widget.pack_forget()
        self.on=0
        return self.widget
    def show(self):

        self.widget.pack_configure(self.args)
        self.on=1
        return self.widget
class ScrollableCanvas(tk.Frame):
    def __init__(self,master, **kwargs):

        super().__init__(master, *kwargs)
        #tk.Frame.__init__(self,master,kwargs)
        self.parent=master
        self.attr=dict()

        self.SBV = Packer(ttk.Scrollbar(self,orient = 'vertical'),'side = right ; fill = y',show=1)
        self.SBH = Packer(ttk.Scrollbar(self,orient = 'horizontal'),'side = bottom ; fill = x',show=1)
        self.C = Packer(tk.Canvas(self),'side = left ; expand = 1 ; fill = both',show=1)

        self.sbV=self.SBV.widget
        self.sbH=self.SBH.widget
        self.c=self.C.widget

        self.configscroll()
        self._bind(self.c,configure=self.eConfigure,map=self.eMap)
        #print('a scrollable canvas created',self.c.bbox('all'))
    def addpropsfor(self,_for,**kw):
        if _for not in self.attr:
            self.attr[_for] = dict()
        self.attr[_for].update(kw)
    def getpropsfor(self,_for,string):
        if _for not in self.attr:
            return None
        return [self.attr[_for].get(i,None) for i in string.split()]
    def configscroll(self):
        self.sbV.config(command = self.c.yview)
        self.sbH.config(command = self.c.xview)
        self.c.config(xscrollcommand=self.sbH.set)
        self.c.config(yscrollcommand = self.sbV.set)
    def _bind(self,target,**kw):
        for k,v in kw.items():
            add=None
            if k[-1]=='_':
                k=k[:-1]
                add=1
            if k[0]=='_':
                k='<{}>'.format(k[1:])
            k = '<{}>'.format(k.capitalize())
            target.bind(k,v,add=add)
    def eConfigure(self,e):
        self.W = self.c.winfo_width()
        self.H = self.c.winfo_height()
        self.c.config(scrollregion = self.c.bbox('all'))
        #print('ScrollableCanvas->eventConfigure',self.c['scrollregion'],e.width,e.height,e.x,e.y,self.c.winfo_ismapped(),self.c.winfo_viewable(),self.c.winfo_width())
    def eMap(self,e):
        pass
        #print('ScrollableCanvas->eventMap',e.width,e.height,e.x,e.y,self.c.winfo_ismapped(),self.c.winfo_viewable(),self.c.winfo_width())
    def disable(self,msg='disabled'):
        if 'D' not in vars(self):
            self.D=Packer(ttk.Label(self.parent,text=msg),self.C.args)
        self.D.show()
    def enable(self):
        if 'D' not in vars(self):
            return
        self.D.widget.configure(state='normal')
        self.D.quotehide()
    def updatesregion(self,lsttag=None,bbox=1):
        self.c.config(scrollregion=(self.c.bbox(lsttag if lsttag else 'all')) if bbox else (lsttag))
class Gallery:

    def __init__(self,**kw):

        self.on = kw.pop('on',0)

        if  not self.on:
            raise('Missing on= ... option')
            return
        if 'c' not in vars(self.on):
            raise(f'Missing "self.c" / "c" instance variable in "{self.on}"')
            return

        self.run = 0
        self.progress=kw.pop('progress')

        self.thumbW, self.thumbH = (50, 50)
        self.lastwidth , self.lastheight , self.padx , self.pady = 1, 1, 20, 20

        self.count=0
        self.imgnames = dict()
        self.objpil=dict()
        self.objthumb=dict()
        self.objimgtk=dict()
        self.idpath=dict()
        self.idname=dict()

        self.on._bind(self.on.c,configure_=self.Threadmoving) ; # _ means add=1
        self.varProg = 0

    def Threadmoving(self,e):
        if 'W' not in vars(self.on) or self.count == 0:
            return
        #put(f'{(self.on.W , self.lastWidth)} {(self.thumbW + self.padX)} ; {(self.on.W - self.lastWidth)} < {(self.thumbW + self.padX)}')
        if self.on.W > self.lastwidth and (self.on.W - self.lastwidth) < (self.thumbW + self.padx):
            return
        self.Tmovestop=0
        self.moving(e)
        if 'T1movelock' not in vars(self):
            pass
            #self.Tmovelock = threading.Lock()
            #self.Tmove = threading.Thread(target=self.moved,args=(e,))
            #print(f'started thread {self.Tmove}')
            #self.Tmove.start()

        else:
            #print(f'*************************** exists maiking {self.Tmovestop = }')
            self.Tmovestop=1
        #print(f'Started {self.Tmove.getName()}')
        self.moving(e)

    def moved0(self,e):
        #self.Tmovelock.acquire()


        #put('moved->grid')
        X,Y,LenX,LenY,count = self.getGrid(self.imageCount)
        #put(Y)
        startI=0
        myc=0
        prog0.config()
        self.lastWidth, self.lastHeight = self.on.W, self.on.H
        #gen = (img for img )
        #print(f'X {X} * Y {Y} = {len(X)*len(Y)} ;')
        for _y in Y:
            #
            for _x,icount  in zip(X,count[startI:startI+LenX]):
                #print(f'no of alive threads {threading.active_count():>10}')
                print(f'{self.Tmovestop = } Active thread {threading.currentThread().getName()}')
                if self.Tmovestop == 7:
                    print('stopped')

                    prog0.config(value=0)
                    self.Tmovelock.release()
                    self.Tmove = threading.Thread(target=self.moved,args=(e,))
                    self.Tmovestop=0
                    self.Tmove.start()
                    return
                #time.sleep(1)
                prog0.step()
                tag='i%d'%icount


                #put(f'count {icount}; --> x {_x}; y {_y}; ')
                self.on.c.moveto('i%d'%icount,_x, _y)
                #put(f'moving  {tag} == i{self.on.c.find_withtag(tag)} to {_x},{_y}')
            #put()
            #print(f'MYC = {myc} {X},{count[startI:startI+LenX]}')
            startI += LenX

            myc+=1
        self.icountrange=count
        self.on.updatesregion()
        #print(f'Thread {threading.currentThread()} Finished')

    def moving(self,e):
        #prog0.config(value=0)

        for y,rest in self.getcoords():
            for x,c in rest:
                self.on.c.moveto('i%d'%c,x, y)
                print(f'{c=} {y=} {x=}')
        self.lastwidth=self.on.W
        self.on.updatesregion()

    def getcoords(self,**kw):
        reqx = self.thumbW+self.padx
        reqy = self.thumbH+self.pady

        xcount = math.floor(self.on.W/reqx)
        if not xcount:
            xcount=1
        ycount = math.ceil(self.count/xcount)

        #print(f'-------- {xcount=} {ycount=}')

        range1=[i*reqx for i in range(xcount)]
        range2=range(self.count)

        count = 0
        start=0
        if kw.pop('use_names',0):

            while count < ycount:
                yield((count*reqy),zip( range1,list(range2[start:start+xcount]),list(self.imgnames[start:start+xcount]) ))
                start+= xcount
                count+=1
        elif kw.pop('use_dict',0):
            while count < ycount:
                yield( count*reqy, zip(range1,list(range2[start:start+xcount]),list(self.cnames.values())[start:start+xcount]) )
                start+= xcount
                count += 1


    def Threadload(self,path,**kw):
        #print('Threadload, Current Thread',threading.currentThread())
        threading.Thread(target=self.load,args=(path,kw)).start()


    #loadNamesFromList
    def load(self,path,kw=dict()):
        #print(f'Gallet->load {path=} {kw=}')

        if self.run:
            return

        if (got:=kw.pop('names',0)):
            self.imgnames=got
            coords=self.getcoords(use_names=1)

        elif (got:=kw.pop('cnames',0)):
            self.cnames=got
            coords=self.getcoords(use_dict=1)
        else:
            #load from this dir
            got=os.listdir(path)
            coords=self.getcoords(use_names=1)

        self.count=len(got)
        self.progress.Variable.set(0)
        self.progress.config(max=self.count)
        show(self.progress,'pack')

        #print(f'~~~ {self.count} \n')
        for y,rest in coords:
            for x,c,name in rest:
                #print(f'{y=} {x=} {c=} {name=}')
                p=os.path.join(path,name)
                #print(f'{path=} {p=}')
                self.idpath[c]=p
                self.idname[c]=name
                self.objpil[c]=(tmp:=PIL_Image.open(p))
                self.objthumb[c]=tmp.thumbnail((self.thumbW,self.thumbH))
                self.objimgtk[c]=(tmp2:=PIL_Image_tk.PhotoImage(tmp))
                self.on.c.create_image(x, y, anchor ='nw', image = tmp2,tag='i%d'%c)

                #print(f'{c=} {y=} {x=}')

                self.progress.step()

        self.run = 1
        hide(self.progress,'pack')
        self.lastwidth=self.on.W
        self.lastheight=self.on.H
        self.on.updatesregion()
# disable the right label widget if no path is set
class LabelAB(tk.Frame):
    def __init__(self,master, **kwargs):
        self.disabled = 1
        self.disabledText = 'Please select File -> "{}"'.format(fileMenu.entrycget(0,'label'))
        super().__init__(master, *kwargs)
        self.L1 = Packer(ttk.Label(self, text = 'Parent Directory :', anchor = 'center'),'side = left  ; padx = 10')
        self.L2 = Packer(ttk.Label(self, text = self.disabledText), 'side = right ; expand = 1 ; fill = x')
        self.l1=self.L1.widget
        self.l2=self.L2.widget
        self.disable()

    def settext(self, text):
        self.enable()
        call, text = [(self._disable,self.disabledText),(self._enable,'"{}"'.format(text))][bool(text)]
        #print('APathLabel -> config',call,text)
        call()
        self.l2.config(text = text)

    def enable(self):
        self.disabled = 0
        self.l2['state'] = 'normal'
    def disable(self):
        self.disabled = 1
        self.l2['state'] = 'disabled'

#asses path from the dialog
class Path:
    def __init__(self,tree=None,gallery=[],path=None):
        if tree is None:
            raise('tree=... is empty')
            return
        if not gallery:
            raise('gallery=... is empty')
            return
        #uncategorized, validation,training galleries
        self.ug, self.vg, self.tg  = gallery

        self.yes='\u2714'
        self.no='\u274c'

        self.tree=tree
        self.all=dict()
        self.init()

        if path:
            self.setpath(path)
        self.tree.bind('<<TreeviewSelect>>',self.rowselected)
    def init(self):
        self.cols=[0,1,2,3]
        self.templ=['']*len(self.cols)
        self.tree.config(columns=self.cols)
        self.tree.column('#0',width=40,stretch=0)
        for i,c in zip('Classes-Has Uncategorized Images-Has Validation-Has Training'.split('-'),self.cols):
            self.tree.heading(c,anchor='center',text=i)
            self.tree.column(c,minwidth=10,width=70,anchor='center')
            print(c)
        #self.tree.column(1,anchor='w')
        self.tree.column(0,anchor='w')
        self.tree.heading(0,anchor='w')
        #print(f'Status {self.missingboth=} \n {self.havet=} \n {self.havev=}')

        #configure tags
        self.tree.tag_configure('nonempty',background='green')
        self.tree.tag_configure('empty',background='red')

    def setpath(self,path):
        _l=os.walk(path)
        _p, _d, _f = next(_l)
        _lam=lambda x:x[x.rfind('.'):] in ('.png','.jpg','.jpeg','.tiff','.tiff')

        _dict=dict()
        for d in _d:
            _p2,_d2,_f2=next(os.walk(os.path.join(_p,d)))
            _dict[d]={'_p':_p2,
                    '_f_id':dict(),
                    '_v':'',
                    '_v_id':dict(),
                    '_t':'',
                    '_t_id':dict(),
                    'value':[self.no,self.no,self.no]} #values count (4)

            _dict[d]['_f_id'] = dict( zip(range(len(_f2)), _f2 ) )

            if (tmpp:=len(_f2)):
                tmp = _dict[d]['value']
                tmp[0] = tmpp
                _dict[d]['value'] = tmp

            _v_n=(list(filter(lambda x: x.lower() == 'validation',_d2)))
            _t_n=(list(filter(lambda x: x.lower() == 'training',_d2)))
            if _v_n:
                _v_n = _v_n[0] #incase of different spelling variations
                _dict[d]['_v']= ( _v:=os.path.join(_p2,_v_n) )
                _, _, _v_f = next(os.walk(_v))
                _dict[d]['_v_id'] = dict( zip(range(len(_v_f)), _v_f:=list(filter(_lam,_v_f))) )
                tmp = _dict[d]['value']
                tmp[1]=len(_v_f)
                _dict[d]['value'] = tmp

            if _t_n:
                _t_n = _t_n[0]
                _dict[d]['_t']= ( _t:=os.path.join(_p2,_t_n) )
                _,_, _t_f = next(os.walk(_t))
                _dict[d]['_t_id'] = dict( zip(range(len(_t_f)), _v_f:=list(filter(_lam,_t_f))) )
                tmp= _dict[d]['value']
                tmp[2] = len(_t_f)
                _dict[d]['value'] = tmp

        self.all = _dict
        #print(f'{self.all =}')
        self.updatetree()

    def updatetree(self):
        keys=sorted(self.all)

        for k in keys:
            v = self.all[k]
            templ=['']
            self.tree.insert('','end',iid=k, values = [k]+v['value'])
            for category,title in zip('_f_id _v_id _t_id'.split(),['{Uncategorized Images}','{Validation Images}','{Training Images}']):
                _dict = v[category]

                if _dict:
                    id1='{%s} {%s}'%(k,category)
                    self.tree.insert(k,'end',iid= id1 ,values=title)
                    for c,img in _dict.items():
                        id2 = '%s {%s}'%(id1,c)
                        self.tree.insert(id1,'end',iid=id2,values = templ+[img])
                templ.append('')
        #start updating gelleries

    def rowselected(self,e):
        pass
        row=self.tree.focus()
        if '}' in row:
            row = row.split('}')[:-1]
            row = [i+'}' for i in row]
        else:
            row = [row]
        #print(f'{row=}')
        row = [i.lstrip().lstrip('{').rstrip().rstrip('}') for i in row]
        row = row + ['']*(3-len(row))
        id1, id2, id3 = row
        print (f'{id1=} {id2=} {id3=}')

        banner.config(text=id1)
        _dict = self.all[id1]
        for widget,a,b in zip('ug vg tg'.split(), '_p _v _t'.split(),'_f_id _v_id _t_id'.split()):
            c_names = _dict[b]
            #print(f'{a=} path={_dict[a]} {c_names=}')
            if c_names:
                getattr(self,widget).Threadload(_dict[a],cnames = c_names)
                #getattr(self,widget).load(_dict[a],dict(cnames=c_names))

def _center(w,width=None,h=None):
    s1 = ['{}']*2
    if width:
        s1[0]=str(width)
    if h:
        s1[1]=str(h)
    #print(f'{s1=}')
    s1='x'.join(s1)
    s2='+{}+{}'.format(int(w.winfo_screenwidth()/2 - w.winfo_reqwidth()/2),int(w.winfo_screenheight()/2 - w.winfo_reqheight()/2))

    w.geometry('%s%s'%(s1,s2))

def _showToplevel(w):
    w.deiconify()
    _center(w)
def _hideToplevel(w):
    w.withdraw()
def _alterToplevelClose(w):
    w.wm_protocol("WM_DELETE_WINDOW", func = lambda i=w: _hideToplevel(i) )
def _exitMain(w):
    w.destroy()
def _makeABanner(p, title = 'Banner'):
    f = tk.Frame(p,bg = 'red')
    s = ttk.Separator(f, orient = 'horizontal')
    l = tk.Label(f, text = title)
    _pack('l -> fill = x', locals())
    _pack('s -> expand = 1 ; fill = x', locals())
    _pack('f -> side = top ; expand = 1 ; fill = x',locals())

# base func to select directory dialog
def _browseToDir(_dir,_title):
    path = filedialog.askdirectory(initialdir = _dir, title = _title)
    return path

# File -> (index 0) ; of validation and training dirs
def _getParentDir():
    #path = _browseToDir(os.getcwd(), fileMenu.entrycget(0,'label'))
    path="F:/Downloads/576013_1042828_bundle_archive/COVID-19 Radiography Database"
    _all = os.listdir(path)
    a = _all[0]
    b = _all[1]
    # remove everything after "dataset"
    #frame01.setLabel(a,True)
    #twoFrame['text'] = " ".join (str.split(frame01['text'])[:3] + ['"{}"'.format(b)])

    fullA, fullB = [os.path.join(path, i) for i in [a , b]]
    #gfor01.loadFromDir(fullA)
    Tpath.setpath(path)


# root window
main = tk.Tk()

# popup
aboutWindow = tk.Toplevel(main)
aboutWindow.title('About A TF Classifier')
# configure it
_hideToplevel(aboutWindow)
_alterToplevelClose(aboutWindow)

# menus
rootMenu = tk.Menu(main)
fileMenu = tk.Menu(rootMenu,tearoff = 0)
fileMenu.add_command(label = 'Select the Directory containing Training and Validiation dirs', command = _getParentDir)
fileMenu.add_separator()
fileMenu.add_command(label = 'Exit', command = lambda : _exitMain(main))
helpMenu = tk.Menu(rootMenu, tearoff = 0)
#helpMenu.add_separator()
helpMenu.add_command(label='About', command = lambda : _showToplevel(aboutWindow))
rootMenu.add_cascade(menu = fileMenu, label = 'File')
rootMenu.add_cascade(menu = helpMenu, label = 'Help')
main['menu']=rootMenu


# Labelframe text padding
def _textcenter(i,by=20):
    l=len(i)
    d= math.ceil(l/by)*l
    return '{0:^{1}}'.format(i,d)

#entry and button for "live-debugging"
def debug(*tup):
    exec(debugvar.get())

debugvar = tk.StringVar()

#hide windows
def hide(w,geom,**kw):
    geom=geom.lower()
    if geom == 'grid':
        if 'GRID_CONFIG' not in vars(w):
            info1 = w.grid_info()
            print(f'{w.winfo_parent()=}')
            info2 = All.grid_rowconfigure(row := info1['row'])

            w.GRID_CONFIG = dict(row = row, weight = info2['weight'], uniform = info2['uniform'])

            print(f'{info1 =} {info2 =}')
        #All.grid_rowconfigure(w.GRID_CONFIG['row'], weight = 0, uniform = 'HIDE')
        w.grid_remove()


    elif geom == 'pack':
        if 'PACK_CONFIG' not in vars(w):
            w.PACK_CONFIG = w.pack_info()
            w.PACK_CONFIG.update(kw)
        w.pack_forget()
    elif geom == 'place':
        if 'PLACE_CONFIG' not in vars(w):
            w.PLACE_CONFIG = w.place_info()
        w.place_forget()

#unhide
def show(w,geom):
    geom=geom.lower()
    if geom == 'grid':
        tmp = w.GRID_CONFIG
        All.grid_rowconfigure(tmp['row'], weight = tmp['weight'], uniform = tmp['uniform'])
        w.grid()
    elif geom == 'pack':
        w.pack_configure(**w.PACK_CONFIG)
    elif geom == 'place':
        w.place_config(**w.PLACE_CONFIG)

def ifcollapse(menu,cindex,scroll,geom):
    call,label = [(show,'Collapse'),(hide,'Expand')][menu.entrycget(0,'label')=='Collapse']
    #print(f'{call=}')
    menu.entryconfig(0,label=label)
    call(scroll,geom)

#--------------------------------------------------------------------------------------------#

# size grip
(grip := ttk.Sizegrip(main)).pack(side = BOTTOM, expand = 0 , fill = X)

#--------------------------------------------------------------------------------------------#

# main frame
(frame0 := ttk.LabelFrame(main, text = 'Zero')).pack(expand = 1 , fill = BOTH)

#--------------------------------------------------------------------------------------------#

#/frame0/exe entry
#/frame0/exe button
(debugbutton := ttk.Button(frame0,command=debug,text='Execute')).pack(expand = 0,side = TOP, fill = X)
(entryfor0 := ttk.Entry(frame0,textvariable=debugvar,font='courier 11')).pack(expand = 0,side = TOP, fill = X)

entryfor0.bind('<Key-Return>',debug)

#--------------------------------------------------------------------------------------------#

# main paned window
(paned:=ttk.PanedWindow(frame0,orient='horizontal')).pack(expand = 1 , fill = BOTH)

#--------------------------------------------------------------------------------------------#

#paned window/classes frame/
paned.add(Tree:=ttk.LabelFrame(paned,text=_textcenter('Classes')),weight=1)

#Grid config
Tree.grid_columnconfigure([0],weight=1,uniform=1)
Tree.grid_rowconfigure([0],weight=1,uniform=1)

#--------------------------------------------------------------------------------------------#

# paned/classes Frame/classes treeview/
(tree:=ttk.Treeview(Tree)).grid(row=0,column=0,sticky='nswe')

#--------------------------------------------------------------------------------------------#
#-----------------------------------Right Frame----------------------------------------------#
#--------------------------------------------------------------------------------------------#

# paned/right frame/
paned.add(right:=ttk.Frame(paned),weight=1)


#--------------------------------------------------------------------------------------------#

# paned/right frame/class banner frame/
(bannerframe:=ttk.Labelframe(right,text=_textcenter('Class'))).place(x=0 , y = 0, relwidth=1, relheight=0.1)

#--------------------------------------------------------------------------------------------#

# paned/right frame/class banner frame/class banner label
(banner:=ttk.Label(bannerframe,text='',font=dict(weight='bold'))).pack(side=TOP )

#--------------------------------------------------------------------------------------------#


#paned/right frame/second paned window/"uncategorized" frame/
(All:=ttk.LabelFrame(right,text='Uncategorized Images')).place(rely=0.1 , x = 0, relwidth=1, relheight=0.3)


#--------------------------------------------------------------------------------------------#

# /"uncategized" actions menu
uncatmenu=tk.Menu(main,tearoff=0)

uncatmenu.add_command(label='Collapse',command=lambda : ifcollapse(uncatmenu,0,uncatscroll,'pack'))

#--------------------------------------------------------------------------------------------#

# paned/right frame/"uncategorized" frame/actions button
(uncatbutton:=ttk.Menubutton(All,text='Actions',menu=uncatmenu)).pack(side=TOP , expand = 0, fill=X)

#--------------------------------------------------------------------------------------------#



#paned/right frame/second paned window/"uncategorized" frame/scroll canvas
(uncatscroll:=ScrollableCanvas(All)).pack(side=TOP , expand = 1, fill=BOTH)



#--------------------------------------------------------------------------------------------#
# paned/right frame/"uncategorized" frame/progress bar
(uncatprog:=ttk.Progressbar(All,orient = 'horizontal')).pack(side=TOP , expand = 0, fill=X,before = uncatscroll)
uncatprog.Variable = tk.IntVar() #value =55
uncatprog.config(variable=uncatprog.Variable)
hide(uncatprog,'pack', before = uncatscroll)

#--------------------------------------------------------------------------------------------#
guncat = Gallery(on=uncatscroll,progress=uncatprog)
#--------------------------------------------------------------------------------------------#


#paned/right frame/top frame
(Top:=ttk.LabelFrame(right,text='Training Images')).place(rely=0.4 , x = 0, relwidth=1, relheight=0.3)


#--------------------------------------------------------------------------------------------#


#paned/right frame/top frame/frame01/train ScrollableCanvas
(scrollfor01 := ScrollableCanvas(Top)).pack(expand = 1, fill = BOTH)

#--------------------------------------------------------------------------------------------#

#paned/right frame/top frame/training progress bar

(trainprog := ttk.Progressbar(Top,orient = 'horizontal')).pack(expand = 1,side = TOP, fill = X, before = scrollfor01)
trainprog.Variable = tk.IntVar() #value =55
trainprog.config(variable=trainprog.Variable)
hide(trainprog,'pack', before = scrollfor01)

#--------------------------------------------------------------------------------------------#
g01 = Gallery(on=scrollfor01,progress=trainprog)
#--------------------------------------------------------------------------------------------#

#paned/right frame/top frame/frame00/parent path LabelAB
(frame00 := LabelAB(Top)).pack(expand = 1,side = TOP, fill = X)


#--------------------------------------------------------------------------------------------#

#paned/right frame/bottom frame
(Bottom:=ttk.LabelFrame(right,text='Validation Images')).place(rely=0.7 , x = 0, relwidth=1, relheight=0.3)

#--------------------------------------------------------------------------------------------#


#paned/right frame/bottom frame/validation ScrollableCanvas
(scrollfor02 := ScrollableCanvas(Bottom)).pack(expand = 1,side = TOP, fill = BOTH)

#--------------------------------------------------------------------------------------------#
validprogvar = tk.IntVar() #value =55
# paned/right frame/"validation" frame/progress bar
(validprog:=ttk.Progressbar(Bottom,orient = 'horizontal',variable = validprogvar)).pack(side=TOP , expand = 0, fill=X, before = scrollfor02)
validprog.Variable = tk.IntVar() #value =55
validprog.config(variable=validprog.Variable)
hide(validprog,'pack', before = scrollfor02)

#--------------------------------------------------------------------------------------------#
g02 = Gallery(on=scrollfor02,progress=validprog)
#--------------------------------------------------------------------------------------------#


#chosen path assesor
Tpath=Path(tree=tree,gallery=[guncat,g01,g02])

#--------------------------------------------------------------------------------------------#

main.title('A TF Classifier')

#main.wm_attributes('-top',1)

_center(main,500,500)

main.mainloop()
