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
        self.all=dict()
        self.init()

        if path:
            self.setpath(path)

    def setpath(self,path):
        _l=os.walk(path)
        _p, _d, _f = next(_l)
        _lam=lambda x:x[x.rfind('.'):] in ('.png','.jpg','.jpeg','.tiff','.tiff')

        _dict=dict()
        for d in _d:
            _p2,_d2,_f2=next(os.walk(os.path.join(_p,d)))
            _dict[d]={'_p':_p2,'_f':_f2,'_v':'','_v_f':[],'_t':'','_t_f':[],'value':[self.no,self.no,self.no]}

            if (tmpp:=len(_f2)):
                tmp = _dict[d]['value']
                tmp[0] = tmpp
                _dict[d]['value'] = tmp

            _v_n=(list(filter(lambda x: x.lower() == 'validation',_d2))[0:1]) #incase of different spelling variations
            _t_n=(list(filter(lambda x: x.lower() == 'training',_d2))[0:1])
            if _v_n:
                _v=os.path.join(_p2,_v_n)
                _dict[d]['_v']= _v
                _, _, _v_f = next(os.walk(_v))
                _v_f=filter(_lam,_v_f)
                _dict[d]['_v_f'] = _v_f
                tmp = _dict[d]['value']
                tmp[1]=len(_v_f)
                _dict[d]['value'] = tmp

            if _t_n:
                _t=os.path.join(_p2,_t_n)
                _dict[d]['_t']= _t
                _,_, _t_f = next(os.walk(_t_f))
                _t_f=filter(_lam,_t_f)
                _dict[d]['_t_f'] = _t_f
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
            self.tree.insert('','end',iid=k, values = [k]+v['value'])

    def init(self):
        self.cols=[0,1,2,3]
        self.tree.config(columns=self.cols)
        self.tree.column('#0',width=20,stretch=0)
        for i,c in zip('Classes Has*NonCategorized*Images Has*Validation Has*Training'.split(),self.cols):
            i = i.replace('*',' ')
            self.tree.heading(c,anchor='center',text=i)
            self.tree.column(c,minwidth=10,width=70,anchor='center')
            print(c)
        #print(f'Status {self.missingboth=} \n {self.havet=} \n {self.havev=}')

        #configure tags
        self.tree.tag_configure('nonempty',background='green')
        self.tree.tag_configure('empty',background='red')

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
