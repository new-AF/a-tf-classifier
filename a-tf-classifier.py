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
for i in 'x bottom left right top y both'.split():
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
        self.parent=master
        self.attr=dict()

        self.SBV = Packer(ttk.Scrollbar(master,orient = 'vertical'),'side = right ; fill = y',show=1)
        self.SBH = Packer(ttk.Scrollbar(master,orient = 'horizontal'),'side = bottom ; fill = x',show=1)
        self.C = Packer(tk.Canvas(master),'side = left ; expand = 1 ; fill = both',show=1)

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

        self.on = kw.pop('on',False)

        if  self.on == False:
            raise('Missing on= ... option')
            return
        if 'c' not in vars(self.on):
            raise('Missing "self.c" / "c" instance variable in "{}"'.format(self.on))
            return
        #if 'progress' in kw and kw.pop('progress',0):
        #    self.pval=0
        #    self.Progress=Packer(ttk.Progressbar(self.on.parent.winfo_parent(),orient = 'horizontal',variable = self.pval, value=30), 'side = top;  fill = x')
        #    self.progress=self.Progress.show()


        self.thumbW, self.thumbH = (50, 50)
        self.imageCount , self.rowCount , self.colCount = 0 , 0 , 0
        self.imageObject , self.imageThumb , self.imageTk = dict() , dict() , dict()
        self.lastWidth , self.lastHeight , self.padX , self.padY = 1, 1, 20, 20
        self.counttofname=dict()
        self.icountrange=[]
        # _ means add=1
        self.on._bind(self.on.c,configure_=self.startmoved)
        self.varProg = 0

    def startmoved(self,e):
        if 'W' not in vars(self.on) or self.imageCount == 0:
            return
        #put(f'{(self.on.W , self.lastWidth)} {(self.thumbW + self.padX)} ; {(self.on.W - self.lastWidth)} < {(self.thumbW + self.padX)}')
        if self.on.W > self.lastWidth and (self.on.W - self.lastWidth) < (self.thumbW + self.padX):
            return
        self.Tmovestop=0
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
        self.moved(e)

    def moved(self,e):
        #self.Tmovelock.acquire()
        prog0.config(value=0)

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
    def getGrid(self,_len):
        #put('->grid')
        x = list(range(0, self.on.W, self.thumbW + self.padX ))
        lenX = len(x)

        if len(x) == 0:
            x = 1
            print('grid-> len(x) == 0; Automatically set to 1')
        #put(f'ROWs {(_len/lenX)}')
        y = list(range(0, (int(math.ceil(_len/lenX)))*(self.thumbH + self.padY),self.thumbH + self.padY))
        lenY = len(y)
        count = list(range(_len))
        #put(f'total = {_len} ; {lenX} x {lenY} ; ')
        #put(f'X---{x}----Y----{y}')
        return [x,y,lenX,lenY,count]
    def loadFromFilename(self,fname):
        pass
    def loadFromDir(self,path):
        print('Parent',threading.currentThread())
        threading.Thread(target=self.loadFromDir_,args=(path,)).start()
    def loadFromDir_(self,path):
        #print('loadFromDir ->',path)
        fileNames = os.listdir(path)
        filePaths = list(map(lambda i, path = path: os.path.join(path,i), fileNames ))

        _len = len(fileNames)

        X,Y,LenX,LenY,self.icountrange = self.getGrid(_len)

        #put(f'{X}----{Y}----{LenX}----{LenY}-----')
        #put ('canFitCols->',LenX, 'math->',self.on.W / (self.thumbW+self.padX),'x ranges',X)
        prog0.config(maximum=_len)
        startI, colCount = 0, 0

        self.lastWidth, self.lastHeight = self.on.W, self.on.H
        for _y in Y:

            for fileName, _x, filePath,icount  in zip(fileNames[startI:startI+LenX],X,filePaths[startI:startI+LenX],self.icountrange[startI:startI+LenX] ):

                #print(f'fileName ---{filePath}---{_y}---{_x}---{self.imageCount}---')
                self.counttofname[icount]=fileName
                self.imageObject[icount] = PIL_Image.open(filePath)
                self.imageThumb[icount] = self.imageObject[icount].thumbnail((self.thumbW,self.thumbH))
                self.imageTk[icount] = PIL_Image_tk.PhotoImage( image = self.imageObject[icount] )
                self.on.c.create_image(_x, _y, anchor ='nw', image = self.imageTk[icount],tag='i%d'%icount)
                prog0.step()
                #print(threading.currentThread())
                #self.on.c.create_text(_x, _y, text = f'{_x,_y}')

            startI += LenX
        self.lastY = Y[-1]
        self.imageCount = _len
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
    def __init__(self,control=None,path=None):
        if control is None:
            raise('control=... is empty')
            return
        self.yes='\u2714'
        self.no='\u274c'

        self.tree=control

        self.havet = dict()
        self.havev = dict()
        self.missingboth = dict()
        self.empty=dict()

        self.where=dict()
        self.tags=dict()
        if path:
            self.setpath(path)
    def setpath(self,path):
        _fnames = os.listdir(path)
        _files = [i for i in _fnames if os.path.isdir( os.path.join(path,i) )]
        #print(f'{_files =}')
        #print()
        _class_info = {_class : {'path' : _path} for _class,_path in zip(_files,[os.path.join(path,i) for i in _files ])}

        ##
        experiment = 0
        if experiment:
            _names = os.listdir(path)
            _namepaths = list(map(lambda x: os.path.join(path,x),_names))
            _zip = list(filter(lambda x: os.path.isdir(x[1]), zip(_names,_namepaths)  ))

            _d1 = {n : {
                    'path':p,
                    'all':os.listdir(p),
                    'v_listing':None,
                    't_listing':None,
                    'v':None,
                    't':None,
                    'all_len':None,
                    'v_len':None,
                    't_len':None,
                    'tag':None,
                    'values':None
                    } for n,p in _zip}

            def hasValidation(n,dirname):
                _d1[n]['v'] = dirname
                #print('hasVVV')
                #print ('->>>',_d1[n])
                return 1

            def hasTraining(n,dirname):
                #print('hasTTT')
                _d1[n]['t'] = dirname
                print ('->>>',_d1[n])
                return 1
            #print(f'{_d1 =}')
            for n,_d in _d1.items():
                p = _d['path']
                if [ i for  i in _d['all'] if i.lower() == 'validation' and os.path.isdir(os.path.join(p,i) ) and hasValidation(n,i)]: #unix shenanigs if multiple variations of 'validation' exist, last dir (set via hasValidation) will be use
                    tmp=list( filter(lambda x:x[x.rfind('.'):] in ('.png','.jpg','.jpeg','.tiff','.tiff'), os.listdir(os.path.join(p,_d1[n]['v'])) ) )
                    _d[n]['v_listing']=tmp
                    _d[n]['v_len']=len(tmp)
                if [ i for i in _d['all'] if i.lower() == 'training' and os.path.isdir( os.path.join(p,i) ) and hasTraining(n,i) ]:
                    tmp=list( filter(lambda x:x[x.rfind('.'):] in ('.png','.jpg','.jpeg','.tiff','.tiff'), os.listdir(os.path.join(p,_d1[n]['t'])) ) )
                    _d[n]["t_listing"]=tmp
                    _d[n]['t_len']=len(tmp)

                if _d[n]['t'] and _d[n]['t']:
                    _d[n]['all']=[]
        #for k,v in _d1.items():
        #    print(f'{k=} {v=}\\n\n')
        #print(f'{_dnames =} {_dpaths =}')
        ##

        for k in dict(_class_info):
            _path=_class_info[k]['path']
            _class_info[k]['filenames']= list( filter(lambda x:x[x.rfind('.'):] in ('.png','.jpg','.jpeg','.tiff','.tiff'), os.listdir(_path) ) )
            _class_info[k]['nonempty'] = ( tmp:= len(_class_info[k]['filenames']) )
            if not tmp:
                self.empty[k] = _class_info[k]
                del _class_info[k]
        todel=[]

        def markandcopy(item,to,key):
            if key not in getattr(self):
                getattr(self,key)[key]=dict(path=_class_info['path'])
            #key -> _class/folder that contains the  folders named "training" or "validation"
            getattr(self,to)[key]=item
            todel.append(key)
            return None
        for _class, _dict in _class_info.items():
            _class_listdir = os.listdir(_dict['path'])
            t = [markandcopy(i,to='havet') for i in _class_listdir if i.lower() == 'training' and os.path.isdir( os.path.join(_dict['path'],i) ) ]
            v = [markandcopy(i,to='havev') for i in _class_listdir if i.lower() == 'validation' and os.path.isdir( os.path.join(_dict['path'],i) )]

        for k in todel:
            del _class_info[k]
        self.missingboth=_class_info
        self.updatetree()
    def updatetree(self):
        if not self.tree.get_children():
            self.init()
        keys=[]

        for key in self.havet.keys():
            keys.append((key,self.yes,self.no,self.yes))
            self.where[key]='havet'
        for key in self.havev.keys():
            keys.append((key,self.yes,self.yes,self.no))
            self.where[key]='havev'
        for key in self.missingboth.keys():
            keys.append((key,self.yes,self.no,self.no))
            self.where[key]='missingboth'
        for key in self.empty.keys():
            keys.append((key,self.no,self.no,self.no))
            self.where[key]='empty'


        keys.sort(key=lambda x:x[0])

        self.keys=keys


        print(f'{keys=}')
        for k in keys:
            _id=k[0]
            self.tree.insert('','end',iid=_id,values=k)
            #for fname in getattr(self,self.where[_id])['filenames']:
            #    self.tree.insert(_id,'end',iid=fname,values=fname)

        for k in keys:
            self.tree.item(k[0],tags=self.tags[self.where[k[0]]])

        #print(f'{self.tags=} f{self.where=} f{keys=}')



    def init(self):
        t=self.tree
        self.cols=[0,1,2,3]
        t.config(columns=self.cols)
        t.column('#0',width=0,stretch=0)
        for i,c in zip('Classes Non*Empty Has*Validation Has*Training'.split(),self.cols):
            i = i.replace('*',' ')
            t.heading(c,anchor='center',text=i)
            t.column(c,minwidth=10,width=70,anchor='center')
            print(c)
        #print(f'Status {self.missingboth=} \n {self.havet=} \n {self.havev=}')

        #configure tags
        t.tag_configure('nonempty',background='green')
        t.tag_configure('empty',background='red')

        self.tags['havet']='nonempty'
        self.tags['havev']='nonempty'
        self.tags['missingboth']='nonempty'
        self.tags['empty']='empty'
def _center(w):
    w.geometry('+{}+{}'.format(int(w.winfo_screenwidth()/2 - w.winfo_reqwidth()/2),int(w.winfo_screenheight()/2 - w.winfo_reqheight()/2)))

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
    gfor01.loadFromDir(fullA)
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

# size grip
(grip := ttk.Sizegrip(main)).pack(side = BOTTOM, expand = 0 , fill = X)


# main frame
(frame0 := ttk.LabelFrame(main, text = 'Zero')).pack(expand = 1 , fill = BOTH)

# main paned window
(paned:=ttk.PanedWindow(frame0,orient='horizontal')).grid(row=0,column=0,rowspan=2,columnspan=2,sticky='nswe')

### Gridding Starts here ###
## Including Column and Row Configuration ##
frame0.grid_columnconfigure([0,1],weight=1,uniform=1)
###

#paned->classes Frame->
paned.add(Tree:=ttk.LabelFrame(paned,text=_textcenter('Classes')),weight=1)

#Grid(paned->classes Frame->)
Tree.grid_columnconfigure([0],weight=1,uniform=1)
Tree.grid_rowconfigure([0],weight=1,uniform=1)

# paned->classes Frame->classes treeview
(tree:=ttk.Treeview(Tree)).grid(row=0,column=0,sticky='nswe')



#paned->second paned
paned.add(Second:=ttk.PanedWindow(paned,orient='vertical'))

#paned->second paned->top frame
Second.add(Top:=ttk.LabelFrame(Second,text='top frame'),weight=1)

#Grid(paned->second paned->top frame)
Top.grid_columnconfigure([0,1],weight=1,uniform=1)
Top.grid_rowconfigure([2],weight=1,uniform=1)
Top.grid_rowconfigure([0,1,3],weight=0,uniform=0)

#paned->second paned->bottom frame
Second.add(Bottom:=ttk.LabelFrame(Second,text='bottom frame'),weight=1)

#Grid(paned->second paned->top frame)
Bottom.grid_columnconfigure([0,1],weight=1,uniform=1)
Bottom.grid_rowconfigure([0,1],weight=1,uniform=1)

#entry and button for "live-debugging"
def debug(*tup):
    exec(debugvar.get())

debugvar = tk.StringVar()

(debugbutton := ttk.Button(Top,command=debug,text='Execute')).grid(row=0,column=0,columnspan=2,sticky='nswe')
(entryfor0 := ttk.Entry(Top,textvariable=debugvar,font='courier 11')).grid(row=1,column=0,columnspan=2,sticky='nswe')

entryfor0.bind('<Key-Return>',debug)

# parent path
(frame00 := LabelAB(Top)).grid(row=2,column=0,columnspan=2,sticky='nswe')
Tpath=Path(control=tree)

#train frame
(frame01 := ttk.LabelFrame(Top,text=_textcenter('Training Images dataset'))).grid(row=2,column=0,columnspan=2,sticky='nswe')

#train gallery
(scrollfor01 := ScrollableCanvas(frame01)).pack(expand = 1, fill = BOTH)
gfor01 = Gallery(on=scrollfor01,progress=1)

#progress bar
prog0var = tk.IntVar()
(prog0 := ttk.Progressbar(Top,orient = 'horizontal',variable = prog0var, value=30)).grid(row=3,column=0,columnspan=2,sticky='nswe')

#validation frame
(frame02 := ttk.LabelFrame(Bottom,text = _textcenter('Validation Images dataset'))).grid(row=0,column=0,columnspan=2,sticky='nswe')

#validation gallery
(scrollfor02 := ScrollableCanvas(frame02)).pack(expand = 1, fill = BOTH)


main.title('A TF Classifier')


#main.wm_attributes('-top',1)

_center(main)

main.mainloop()
