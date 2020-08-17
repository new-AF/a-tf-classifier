#-------------------------------------------------------------------------------
# Name:     a-tf-classifier.py
# Purpose:  a gui fontend for tensorflow
# Author:   abdullah fatota
#-------------------------------------------------------------------------------
import tkinter as tk
import tkinter.ttk as ttk
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
        #print('a scrollable canvas created')
    def eventConfigure(self,e):
        self.c['scrollregion'] = self.c.bbox('all')
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
fileMenu.add_separator()
fileMenu.add_command(label = 'Exit', command = lambda : _exitMain(main))
helpMenu = tk.Menu(rootMenu, tearoff = 0)
#helpMenu.add_separator()
helpMenu.add_command(label='About', command = lambda : _showToplevel(aboutWindow))
rootMenu.add_cascade(menu = fileMenu, label = 'File')
rootMenu.add_cascade(menu = helpMenu, label = 'Help')
main['menu']=rootMenu

# root window 'body' frame
zeroFrame = ttk.LabelFrame(main, text = 'Zero')
# pack it to fully occupy the root windo
_pack('zeroFrame -> expand = 1 ; fill = both')

# train data
oneFrame = ttk.LabelFrame(zeroFrame,text = 'Training Images dataset')
oneScrollable = ScrollableCanvas(oneFrame, pack = 'expand = 1 ; fill = both')
_pack('oneFrame -> expand = 1 ; fill = both')


#_makeABanner(oneFrame, 'Training Data')
main.title('A TF Classifier')
_center(main)
main.mainloop()
