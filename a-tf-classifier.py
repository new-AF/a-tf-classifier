#-------------------------------------------------------------------------------
# Name:     a-tf-classifier.py
# Purpose:  a gui fontend for tensorflow
# Author:   abdullah fatota
#-------------------------------------------------------------------------------
import tkinter as tk
import tkinter.ttk as ttk

from tkinter import filedialog
from tkinter import messagebox
from PIL import Image as PIL_Image
from PIL import ImageTk as PIL_Image_tk

put = print
for i in 'x bottom left right top y both'.split():
    exec(f'{i.upper()}=i')
    #globals()[i.capitalize()]=eval(f'tk.{i}')
BLUE,RED,YELLOW,GREEN = 'blue red yellow green'.split()
put(X)
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
    def show(self):

        self.widget.pack_configure(self.args)
        self.on=1

class ScrollableCanvas(tk.Frame):
    def __init__(self,master, **kwargs):

        super().__init__(master, *kwargs)
        self.config(bg=GREEN)
        self.attr=dict(parent=master)

        self.SBV = Packer(ttk.Scrollbar(master,orient = 'vertical'),'side = right ; fill = y',show=1)
        self.SBH = Packer(ttk.Scrollbar(master,orient = 'horizontal'),'side = bottom ; fill = x',show=1)
        self.C = Packer(tk.Canvas(master,bg = 'blue'),'side = left ; expand = 1 ; fill = both',show=1)

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

    def __init__(self,**kwargs):

        self.on = kwargs.pop('on',False)
        if  self.on == False:
            raise('Missing on= ... option')
            return
        if 'c' not in vars(self.on):
            raise('Missing "self.c" / "c" instance variable in "{}"'.format(self.on))
            return

        self.thumbW, self.thumbH = (50, 50)
        self.imageCount , self.rowCount , self.colCount = 0 , 0 , 0
        self.imageObject , self.imageThumb , self.imageTk = dict() , dict() , dict()
        self.lastWidth , self.lastHeight , self.padX , self.padY = 1, 1, 20, 20
        self.counttofname=dict()
        self.icountrange=[]
        # _ means add=1
        self.on._bind(self.on.c,configure_=self.moved)
        self.varProg = 0
    def moved(self,e):
        if ('W') not in vars(self.on):
            put('NOT')
            return
        if self.imageCount == 0 or (self.on.W - self.lastWidth) < (self.thumbW + self.padX):
            put('NOT2')
            return

        X,Y,LenX,LenY = self.grid(self.imageCount)
        startI, colCount = 0, 0

        self.lastWidth, self.lastHeight = self.on.W, self.on.H
        #gen = (img for img )
        for _y in Y:
            for _x,icount  in zip(X[startI:startI+LenX],self.icountrange[startI:startI+LenX]):
                self.on.c.moveto('i%d'%icount,_x, _y)
                #put(f'moving f{icount} to {_x},{_y}')

            startI += LenX
        self.on.updatesregion()
    def grid(self,_len):
        #
        x, y = list(range(0, self.on.W, self.thumbW + self.padX )), 0
        lenX = len(x)
        if len(x) == 0:
            x = 1
            print('grid-> len(x) == 0; Automatically set to 1')
        y = list(range(0, _len*(self.thumbH+self.padY),self.thumbH + self.padY))
        return [x,y,lenX,len(y)]
    def loadFromFilename(self,fname):
        pass

    def loadFromDir(self,path):
        print('loadFromDir ->',path)
        fileNames = os.listdir(path)
        filePaths = list(map(lambda i, path = path: os.path.join(path,i), fileNames ))

        _len = len(fileNames)

        X,Y,LenX,LenY = self.grid(_len)
        self.icountrange = range(_len)
        #put(f'{X}----{Y}----{LenX}----{LenY}-----')
        #put ('canFitCols->',LenX, 'math->',self.on.W / (self.thumbW+self.padX),'x ranges',X)

        startI, colCount = 0, 0

        self.lastWidth, self.lastHeight = self.on.W, self.on.H
        for _y in Y:

            for fileName, _x, filePath,icount  in zip(fileNames[startI:startI+LenX],X,filePaths[startI:startI+LenX],self.icountrange[startI:startI+LenX] ):

                #print(f'fileName ---{filePath}---{_y}---{_x}---{self.imageCount}---')
                self.counttofname[icount]=fileName
                self.imageObject[icount] = PIL_Image.open(filePath)
                self.imageThumb[icount] = self.imageObject[icount].thumbnail((self.thumbW,self.thumbH))
                self.imageTk[icount] = PIL_Image_tk.PhotoImage( image = self.imageObject[icount] )
                self.on.c.create_image(_x, _y, anchor ='nw', image = self.imageTk[icount],tag='i%d'%self.imageCount)
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
    def __init__(self,path):
        self.havet = dict()
        self.havev = dict()
        self.missingBOTH = dict()
    def setpath(path):
        _classes = os.listdir(path)
        _class_info = {_class : {'path' : _path} for _class,_path in zip(_classes,[os.path.join(path,i) for i in _classes])}
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
        self.missingBOTH=_class_info

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

# size grip
grip = ttk.Sizegrip(main)
grip.pack(side = BOTTOM , fill = X)


# root window 'body' frame
frame0 = ttk.LabelFrame(main, text = 'Zero'); frame0.pack(expand = 1 , fill = BOTH)
# pack it to fully occupy the root wind

#what's equivalent to Tcl/Tk's console show
debugvar = tk.StringVar()
entryfor0 = ttk.Entry(frame0,textvariable=debugvar,font='courier 11') ; entryfor0.pack(expand = 1 , fill = X)
def debug(*tup):
    exec(debugvar.get())
debugbutton=ttk.Button(frame0,command=debug,text='Execute'); debugbutton.pack(expand = 1 , fill = X)
entryfor0.bind('<Key-Return>',debug)
# show parent path
frame00 = LabelAB(frame0); frame00.pack(side = TOP , fill = X)


# train data gallery
frame01 = ttk.LabelFrame(frame0,text='Training Images dataset') ; frame01.pack(expand = 1 , fill = BOTH)
scrollfor01 = ScrollableCanvas(frame01); scrollfor01.pack(expand = 1, fill = BOTH)
#oneProgressFrame = tk.Frame(frame01,bg='red',bd=10)
gfor01 = Gallery(on=scrollfor01)

#oneProgress = ttk.Progressbar(oneProgressFrame,orient = 'horizontal',variable = oneGallery.varProg)
#_pack('oneProgress -> side = top ; expand = 1 ; fill = x')
#_pack('oneProgressFrame -> side = top ; expand = 1 ; fill = x')
#_pack('frame01 -> expand = 1 ; fill = BOTH')



# validation gallery
frane02 = ttk.LabelFrame(frame0,text = 'Validation Images dataset') ; frane02.pack(expand = 1, fill = BOTH)
scrollfor02 = ScrollableCanvas(frane02); frane02.pack(expand = 1, fill = BOTH)


#_makeABanner(frame01, 'Training Data')
main.title('A TF Classifier')


_center(main)
main.mainloop()
