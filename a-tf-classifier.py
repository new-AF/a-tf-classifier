#-------------------------------------------------------------------------------
# Name:     a-tf-classifier.py
# Purpose:  a gui fontend for tensorflow
# Author:   abdullah fatota
#-------------------------------------------------------------------------------
import tkinter as tk
import tkinter.ttk as ttk

from tkinter import filedialog

from PIL import Image as PIL_Image
from PIL import ImageTk as PIL_Image_tk

# for getcwd
import os

def _geomTranslator(string, keywords):
    newString = []
    for i in string.split(';'):
        a,b = [str.strip(j) for j in i.split('=')]
        if a in keywords:
            b = '"{0}"'.format(b)
        newString.append('{} = {}'.format(a,b))
    newString = ' , '.join(newString)
    return newString
def _pack(string, _locals = None):
    name, _, string = string.partition('->')
    newString = _geomTranslator(string, ['fill','side'])
    newString = '{}.pack({})'.format(name,newString)
    #print(newString)
    exec(newString, None, _locals)

class ScrollableCanvas(tk.Frame):
    def __init__(self,master, **kwargs):
        geomKeywords = ['pack']
        geomArgs = []
        for i in geomKeywords:
            if i in kwargs:
                geomArgs.append('self.{}({})'.format(i,_geomTranslator(kwargs.pop(i),['fill','side'])))
        super().__init__(master, *kwargs)
        self.c = tk.Canvas(master,bg = 'blue')
        self.sbV = ttk.Scrollbar(master,orient = 'vertical', command = self.c.yview)
        self.sbH = ttk.Scrollbar(master,orient = 'horizontal', command = self.c.xview)
        self.c['xscrollcommand'] = self.sbH.set
        self.c['yscrollcommand'] = self.sbV.set
        _pack('self.sbV -> side = right ; fill = y', locals())
        _pack('self.sbH -> side = bottom ; fill = x', locals())
        _pack('self.c -> side = left ; expand = 1 ; fill = both', locals())
        self.c.bind('<Configure>',self.eventConfigure)
        self.c.bind('<Map>',self.eventMap)
        self.isMapped = 0
        #print('a scrollable canvas created',self.c.bbox('all'))
    def eventConfigure(self,e):
        self.c['scrollregion'] = self.c.bbox('all')
       # print('ScrollableCanvas->eventConfigure',self.c['scrollregion'])
    def eventMap(self,e):
        self.W, self.H = self.c.winfo_width() , self.c.winfo_height()
        #print('ScrollableCanvas->eventMap',e.width,e.height,e.x,e.y,self.c.winfo_ismapped(),self.c.winfo_viewable(),self.c.winfo_width())
class Gallery:

    def __init__(self,**kwargs):

        on = self.on = kwargs.pop('on',False)
        if  on == False:
            raise('Missing on= ... option')
            return
        if 'c' not in vars(on):
            raise('Missing "self.c" / "c" instance variable in "{}"'.format(on))
            return
        self.c = on.c
        self.imageCount = 0 ; self.rowCount = 0 ; self.colCount = 0 ; self.imageObject = dict() ; self.imageThumb = dict() ; self.imageTk = dict()
        self.lastWidth = 1 ; self.lastHeight = 1 ; self.padx = 20 ;
    def loadFromFilename(self,fname):
        pass

    def loadFromDir(self,path):
        print('loadFromDir ->',path)
        fileNames = os.listdir(path)
        fileNamesAndPaths = list(zip(fileNames, list(map(lambda i, path = path: os.path.join(path,i), fileNames ))))
        fileNamesLen = len(fileNames)


        x,y = list(range(0,self.on.W,100+self.padx )) , 0
        canFitCols = len(x)
        canFitRows = fileNamesLen / canFitCols
        print ('canFitCols->',canFitCols, 'math->',self.on.W / (100+self.padx),'x',x)

        startI, colCount = 0, 0

        while (canFitRows > 0):
            colCount = 0
            for fileName, filePath in fileNamesAndPaths[startI:startI+canFitCols]:
                #print(fileName,filePath)
                self.imageObject[fileName] = PIL_Image.open(filePath)
                self.imageThumb[fileName] = self.imageObject[fileName].thumbnail((50,50))
                self.imageTk[fileName] = PIL_Image_tk.PhotoImage( image = self.imageObject[fileName] )
                self.c.create_image(x[colCount],y, image = self.imageTk[fileName])
                colCount += 1
                self.imageCount += 1
            y += 120
            canFitRows -= 1
            startI += canFitCols
            #print()

# disable the widget if no path is set
class APathLabel(tk.Frame):
    def __init__(self,master, **kwargs):
        self.disabled = 1
        self.disabledText = 'Please select File -> "{}"'.format(fileMenu.entrycget(0,'label'))
        super().__init__(master, *kwargs)
        self.l1 = ttk.Label(self, text = 'Parent Directory :', anchor = 'center')
        self.l2 = ttk.Label(self, text = self.disabledText)
        self.l2['anchor'] = 'center'
        self._disable()
        _pack('self.l1 -> side = left  ; padx = 10',locals())
        _pack('self.l2 -> side = right ; expand = 1 ; fill = x',locals())

    # a pass-through config, to only remove a -text option
    def config(self, **kwargs):
        text = kwargs.pop('text',False)
        self._enable()
        call, text = [(self._disable,self.disabledText),(self._enable,'"{}"'.format(text))][bool(text)]
        #print('APathLabel -> config',call,text)
        call()
        self.l2['text'] = text

    def _enable(self):
        self.disabled = 0
        self.l2['state'] = 'normal'
    def _disable(self):
        self.disabled = 1
        self.l2['state'] = 'disabled'

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
    path = _browseToDir(os.getcwd(), fileMenu.entrycget(0,'label'))
    pathFrame.config(text = path)
    if pathFrame.disabled:
        return
    _all = os.listdir(path)
    a = _all[0]
    b = _all[1]
    # remove everything after "dataset"
    oneFrame['text'] = " ".join (str.split(oneFrame['text'])[:3] + ['"{}"'.format(a)])
    twoFrame['text'] = " ".join (str.split(oneFrame['text'])[:3] + ['"{}"'.format(b)])

    fullA, fullB = [os.path.join(path, i) for i in [a , b]]
    oneGallery.loadFromDir(fullA)



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
_pack('grip -> side = bottom ; fill = x')


# root window 'body' frame
zeroFrame = ttk.LabelFrame(main, text = 'Zero')
# pack it to fully occupy the root windo
_pack('zeroFrame -> expand = 1 ; fill = both')

# show parent path
pathFrame = APathLabel(zeroFrame)
_pack('pathFrame -> side = top ; fill = x')

# train data gallery
oneFrame = ttk.LabelFrame(zeroFrame,text = 'Training Images dataset')
oneScrollable = ScrollableCanvas(oneFrame, pack = 'expand = 1 ; fill = both')
_pack('oneFrame -> expand = 1 ; fill = both')

oneGallery = Gallery(on=oneScrollable)

# validation
twoFrame = ttk.LabelFrame(zeroFrame,text = 'Validation Images dataset')
twoScrollable = ScrollableCanvas(twoFrame, pack = 'expand = 1 ; fill = both')
_pack('twoFrame -> expand = 1 ; fill = both')

#_makeABanner(oneFrame, 'Training Data')
main.title('A TF Classifier')


_center(main)
main.mainloop()
