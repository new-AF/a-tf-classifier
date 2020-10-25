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
import random

from tkinter import filedialog
from tkinter import messagebox
import tkinter.font

from PIL import Image
from PIL import ImageTk
from PIL import ImageOps

import tensorflow as tf
import numpy as np
# up chevron icon
# Font Awesome by Dave Gandy - https://fortawesome.github.com/Font-Awesome
UP = Image.open('up.png').resize((20,20))

# down chevron icon
# Font Awesome by Dave Gandy - https://fortawesome.github.com/Font-Awesome
DO = Image.open('down.png').resize((20,20))

put = print
for i in 'x bottom left right top y both none'.split():
    globals()[i.upper()]=i

BLACK,BLUE,RED,YELLOW,GREEN = 'black blue red yellow green'.split()

SHIFT_ON = 0

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

        super().__init__(master, **kwargs)
        self.parent=master
        self.attr=dict()

        self.SBV = Packer(ttk.Scrollbar(self,orient = 'vertical'),'side = right ; fill = y',show=1)
        self.SBH = Packer(ttk.Scrollbar(self,orient = 'horizontal'),'side = bottom ; fill = x',show=1)
        self.C = Packer(tk.Canvas(self),'side = left ; expand = 1 ; fill = both',show=1)

        self.sbV=self.SBV.widget
        self.sbH=self.SBH.widget
        self.c=self.C.widget

        self.configscroll()
        self.localBind(self.c,configure=self.eConfigure,map=self.eMap)
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
    def localBind(self,target,**kw):
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
class Gallery(ttk.Labelframe):

    def __init__(self,parent,**kw):

        super().__init__(parent,**kw)

        self.run = 0
        self.Pvar = tk.IntVar()
        self.Progress=ttk.Progressbar(self,orient = 'horizontal',variable=self.Pvar)
        self.c = tk.Canvas(self)
        self.sbv , self.sbh = ttk.Scrollbar(self,orient = 'vertical',command = self.c.yview) , ttk.Scrollbar(self,orient = 'horizontal',command = self.c.xview)
        self.c.config(xscrollcommand=self.sbh.set, yscrollcommand=self.sbv.set)
        self.Svar = tk.IntVar(value=1)
        self.SLvar = tk.StringVar(value=1)
        self.Scale = ttk.Scale(self,variable=self.Svar)
        self.Scale.L = ttk.Label(self,textvariable=self.SLvar)
        self.Scale.R = ttk.Label(self,textvariable=self.SLvar)
        self.Scale.x = ttk.Label(self,text='x')

        self.init_menu()
        self.init_grid()
        self.scale_init()

        self.W = 1
        self.H = 1
        self.c.bind('<Configure>',self.xconfig)
        self.thumbW, self.thumbH = (50, 50)
        self.imgW , self.imgH = self.thumbW , self.thumbH

        self.lastwidth , self.lastheight , self.padx , self.pady = 1, 1, 20, 20
        self.labelW , self.labelH = self.thumbW + int(self.padx/2) , 2*main.Labelfont.metrics('linespace')

        self.initx = 0
        self.inity = 0
        self.lastx = self.initx
        self.lasty = self.inity
        #id s to be reused for multiple selections
        # due to Tk's memory leaking of canvas id s
        self.s_id = None
        self.s_free = []
        self.s_used = []
        self.s_u = dict()
        self.s_uu = dict()

        self.count=0
        self.count_selected = 0

        self.imgnames = dict()
        self.objpil=dict()
        self.objthumb=dict()
        self.objimgtk=dict()

        self.selected = None
        #self.c.bind('<Configure>',self.Threadmoving,add=1) ; # _ means add=1



        self.previewrunid=None

    def init_menu(self):
        self.M = m = tk.Menu(main,tearoff=0)
        self.MM = mm = tk.Menu(m,tearoff=0)
        self.Mb=ttk.Menubutton(self,text='Actions',menu=m)
        mm.add_checkbutton(label='Unselect', command=lambda : self.deselect())
        mm.add_separator()
        mm.add_command(label='Move to')
        m.add_checkbutton(label='Expand')
        m.add_separator()
        m.add_cascade(label='Selection',menu = mm)
        m.add_separator()
        m.add_command(label='Partition this set')


    def init_grid(self):
        self.Scale.grid(row=1,column=0,sticky='nswe')
        self.Scale.L.grid(row=1,column=1,sticky='w')
        self.Scale.x.grid(row=1,column=2,sticky='w')
        self.Scale.R.grid(row=1,column=3,sticky='w')
        self.Mb.grid(row=1,column=4,sticky='e')
        self.sbv.grid(row=1,column=5,sticky='ns',rowspan=3)
        self.sbh.grid(row=3,column=0,sticky='we',columnspan=6)
        self.c.grid(row=2,column=0,sticky='nswe',columnspan=5)
        self.Progress.grid(row=0,column=0,columnspan=6,sticky='we')

        for i in range(6):
            self.grid_columnconfigure(i,weight=0,uniform=i)
        self.grid_columnconfigure(4,weight=1,uniform='4i')
        self.grid_rowconfigure(0,weight=0,uniform='0')
        self.grid_rowconfigure(1,weight=0,uniform='00')
        self.grid_rowconfigure(2,weight=1,uniform=1)

        self.Scale.grid_remove()
        self.Scale.L.grid_remove()
        self.Scale.x.grid_remove()
        self.Scale.R.grid_remove()
        self.Progress.grid_remove()

    def ifshow(self,widget , s):
        #assumption: all managed by grid
        call = [tk.Grid.grid,tk.Grid.grid_remove][not s]
        call(widget)

    def xconfig(self,e):
        self.c.configure(scrollregion = self.c.bbox('all'))
        self.W = e.width
        self.H = e.height

    def dobbox(self):
        self.c.configure(scrollregion = self.c.bbox('all'))

    def scale_init(self):
        self.Scale.start = 0
        self.Scale.bind('<ButtonPress>',self.scale_start)
        self.Scale.bind('<ButtonRelease>',self.scale_end)
        self.Scale.config(command = self.scale_command)

    def scale_ifshow(self,s):
        self.ifshow(self.Scale , s)
        self.ifshow(self.Scale.L , s)
        self.ifshow(self.Scale.x , s)
        self.ifshow(self.Scale.R , s)


    def Threadmoving(self,e):
        return
        if 'W' not in vars(self.on) or self.count == 0:
            return
        #put(f'{(self.on.W , self.lastWidth)} {(self.thumbW + self.padX)} ; {(self.on.W - self.lastWidth)} < {(self.thumbW + self.padX)}')
        if self.on.W > self.lastwidth and (self.on.W - self.lastwidth) < (self.thumbW + self.padx):
            return
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
        #self.moving(e)


    def remove_selected(self,to = None, cs = None , add = []):
        #print('remove selected')

        cs =  cs if cs else self.get_selected_imgs(ids=1)
        new = dict(objpil=dict() , _f_id = dict() , _f_id2 = dict() )
        cc = to.count
        for c in cs:
            t= 'i%d'%c
            #print(f'{c=} {cc=}')
            new['objpil'][cc] = self.objpil.pop(c)
            new['_f_id'][cc] = self._dict['_f_id'].pop(c)
            new['_f_id2'][cc] = self._dict['_f_id2'].pop(c)
            self.c.delete(t)
            self.objimgtk.pop(c)
            self.objthumb.pop(c)
            cc += 1
            self.count -= 1

        if 'keep_select' not in add:
            self.deselect()
        self.update_labelframe_text()
        self.myfree = cs

        to._sent = new
        if 'ret' in add:
            return new


    def use(self):
        self.objpil.update(self._sent['objpil']) ;

        #put(f'{list(self._dict.keys())=}')

        self._dict['_f_id'].update(self._sent['_f_id'])
        self._dict['_f_id2'].update(self._sent['_f_id2'])
        count=len(self._sent['objpil'])
        #print(f'*************************{count=}')
        merge = zip( self.getcoords(count=count) ,self._sent['objpil'].items())
        for yx,d in merge:
            y,x = yx
            c, pil = d
            tag = 'i%d'%c
            #print(f'{y=} {x=} {tag=}')
            self.count += 1
            self.objthumb[c] = self.objpil[c].resize((self.thumbW,self.thumbH))
            self.objimgtk[c] = ImageTk.PhotoImage(self.objthumb[c])

            self.c.create_image(x, y, anchor ='nw', image = self.objimgtk[c],tag= tag)

            self.c.tag_bind(tag,'<ButtonPress>',self.select)
            self.c.tag_bind(tag, '<Double-ButtonPress>',self.view_show)

            self.c.tag_bind(tag,'<Enter>',self.preview_enter)
            self.c.tag_bind(tag,'<Leave>',self.preview_leave)
            self.c.tag_bind(tag,'<Motion>',self.preview_motion)
            #print(f'new {x=} {y=}')

        self._sent.clear()
        self.update_labelframe_text()

    def getcoords(self,start=(None,None),count=None):
        sx,sy = start

        if sx is None:
            sx=self.lastx
            sy=self.lasty

        if not count:
            count=self.count

        reqx = self.imgW+self.padx
        reqy = self.imgH+self.pady

        w = self.W

        #print(f'***{sx=} {sy=} {reqx=} {reqy=}')

        maxx = (w-sx) // reqx
        before = sx // reqx
        cap = w // reqx
        #print(f'***{count=} {maxx=} {before=} {cap=}')

        if cap == 0:
            cap = 1

        div = (before + count) // cap
        rem = (before + count) % cap

        yc = ( div+(1*(rem != 0)) )
        xc1 = cap - before

        #print(f'***{div=} {rem = } {yc =} {xc1=}')

        xlast = rem*reqx
        ylast = div*reqy

        #print(f'***{xlast=} {ylast = }')

        self.lastx = xlast
        self.lasty += ylast

        x1 = list(range(0 , cap*reqx , reqx))
        y1 = list(range(sy , sy+yc*reqy , reqy  ))

        a = [ (sy , x + sx) for x in x1[: (cap - before)] ]
        b = [ (y , x) for x in x1 for y in y1[1:] ]
        c = [ (y , x) for x in x1 for y in y1[-1:] ]

        #print(f'{y1= }\n{x1=}\n{a=}\n{b=}\n{c=}')

        yield from a
        yield from b
        yield from c


    def resize(self):
        #prog0.config(value=0)
        self._pil = dict()
        robj = map(lambda x: ImageTk.PhotoImage( x.resize((self.imgW,self.imgH)) ), self.objpil.values() )

        coords = self.getcoords(start = (self.initx, self.inity) , count = self.count)

        for yx,c,rimg in zip( coords , self.objpil.keys(), robj ):
            self._pil[c] = rimg
            y,x = yx
            tag = 'i%d'%c
            self.c.itemconfig(tag, image = rimg )
            self.c.moveto(tag , x , y)
            #print(f'{c=} {y=} {x=}')

        self.lastwidth=self.W
        self.dobbox()

    def Threadload(self):
        #print('Threadload, Current Thread',threading.currentThread())
        threading.Thread(target=self.load,args=tuple()).start()
        #self.load()


    #loadNamesFromList
    def load(self):

        if self.run:
            return

        self.count = self._dict['_f_count']
        self.Pvar.set(0)
        #print(f'{self.count=}')
        self.Progress.config(max=self.count)
        self.ifshow(self.Progress,1)

        coords = self.getcoords()
        merge = zip(coords,self._dict['_f_id2'].items(),self._dict['_f_id'].values() )



        for yx,cp,n in merge:
            y,x = yx
            c,p = cp
            #print(f'{y=} {x=} {c=} {n[:11]=}')
            tmp = self.objpil[c] = Image.open(p).convert('L').resize((1024//2,1024//2))
            #tmp2 = np.array(tmp,dtype='uint8')
            #print(n,tmp2.shape)
            self.objthumb[c] = self.objpil[c].resize((self.thumbW,self.thumbH))
            #self.objimgtk[c] = ImageTk.PhotoImage(self.objthumb[c])
            self.objimgtk[c] = ImageTk.PhotoImage(self.objthumb[c])

            tag = 'i%d'%c
            self.c.create_image(x, y, anchor ='nw', image = self.objimgtk[c],tag= tag)

            self.c.tag_bind(tag,'<ButtonPress>',self.select)
            self.c.tag_bind(tag, '<Double-ButtonPress>',self.view_show)

            self.c.tag_bind(tag,'<Enter>',self.preview_enter)
            self.c.tag_bind(tag,'<Leave>',self.preview_leave)
            self.c.tag_bind(tag,'<Motion>',self.preview_motion)

            self.Progress.step()

        self.run = 1
        self.ifshow(self.Progress,0)
        self.lastwidth=self.W
        self.lastheight=self.H
        #self.on.updatesregion()

        if self.objpil:
            self.image_w,self.image_h = self.objpil[0].size
            self.scale_ifshow(1)
        else:
            self.scale_ifshow(0)
            self.image_w,self.image_h = (1,1)

        self.preview_init()
        self.Svar.set(self.thumbW)
        self.scale_command(self.thumbW)
        self.Scale.config(to = self.image_w)

        self.update_labelframe_text()
        #print('\nEND\n')

    def update_labelframe_text(self, u=1):
        old = self.cget('text').split()
        if '|' in old:
            old.pop(0)

        old = ['%d'%self.count] + old[:2] + ['| %d selected item(s)'%self.count_selected]
        #print(f'{old = }')
        self.config(text = ' '.join(old))
        if u:
            self.dobbox()

    def get_labelframe_text(self):
        old = self.cget('text').split()
        if '|' in old:
            old.pop(0)

        old = old[:2]
        old = ' '.join(old)
        return old

    def select(self,e):
        main.update()
        #print(f'{SHIFT_ON=} {self.s_used=} {self.s_free=} {self.s_id=} {self.s_u=}')
        if not SHIFT_ON:
            self.deselect()
        #
        iall = e.widget.find_withtag("current")
        tall = [self.c.gettags(i) for i in iall]
        s = [i for i,t in zip(iall,tall) if 'select' in t]
        img = [t[0] for i,t in zip(iall,tall) if i not in s][0]


        #print(f'{iall=} {tall=} {s=} {img=}')
        if not self.s_free:
            self.s_id = self.c.create_rectangle(0, 0,self.imgW,self.imgH, fill = BLUE,outline='', stipple = 'gray50',tag='select',width = 0, state = 'normal')
            self.c.tag_bind(self.s_id,'<Double-ButtonPress>',self.view_show)
            self.s_free.append(self.s_id)

        self.s_id = self.s_free.pop(-1)
        self.s_used.append(self.s_id)
        self.s_u[self.s_id]=img
        self.s_uu[self.s_id]=int(img[1:])


        x , y = self.c.coords(img)
        self.c.coords(self.s_id , [ x , y , x+self.imgW , y+self.imgH ] )
        self.c.itemconfig(id,state='normal')

        self.count_selected = len(self.s_used)
        self.update_labelframe_text()

    def deselect(self):
        for s in self.s_used:
            self.c.itemconfig(s,state='hidden')
            self.s_u[s]=None
        self.s_used.clear()
        self.s_id = None
        self.count_selected = 0
        self.update_labelframe_text()

    def get_selected_imgs(self,**kw):
        cs = [self.s_uu[s] for s in self.s_used]

        nest=0
        ret = []
        for i in kw:
            if i == 'pils':
                ret += [[self.objpil[i] for i in cs]]
                nest+=1
            elif i == 'names':
                ret += [[ self._dict['_f_id'][c] for c in cs] ]
                nest+=1
            elif i == 'paths':
                ret += [[ self._dict['_f_id2'][c] for c in cs] ]
                nest+=1
            elif i == 'ids':
                ret += [cs]
                nest += 1

        if nest < 2:
            if nest:
                return ret[0]
            else:
                return []

        return ret



    def scale_start(self,e):
        self.Scale.start = 1

    def scale_end(self,e):
        if not self.Scale.start:
            return
        val = self.Svar.get()
        val = int(float(val))
        #print (f'{val = }')
        self.scale_resize(val)
        self.Scale.start = 0

    def scale_command(self,val):
        val = int(float(val))
        self.SLvar.set(value = val)

    def scale_resize(self,val):
        self.SLvar.set(value = val)

        self.imgW = val
        self.imgH = val
        self.resize()
        self.preview_small_resize()

    def scale_hide(do = 1):
        pass

    def preview_init(self):
        self.Preview = ScrollableCanvas(main)
        self.Preview.config(highlightbackground = GREEN , highlightthickness = 2)
        self.Preview.SBH.quotehide()
        self.Preview.SBV.quotehide()

        ratio = self.image_w / self.thumbW

        self.Preview_ratio = ratio
        self.Preview_ratioDiv2 = (ratioDiv2 := ratio/2)
        self.Preview_pad = int(ratioDiv2 * ratio)
        self.Preview_imgPadX , self.Preview_imgPadX = int(self.Preview_pad/2) , int(self.Preview_pad/2)

        self.c.create_line(0,0,ratio,0,ratio,ratio,0,ratio,0,0,fill='white',tag='small',state='hidden')
        # artificial padding
        self.Preview.c.create_rectangle(0,0, self.Preview_pad + self.image_w , self.Preview_pad + self.image_w , outline = "")

        self.Preview.c.update()
        cx , cy = self.Preview.c.canvasx(0) , self.Preview.c.canvasy(0)
        #print(f'INIT {self.Preview_pad = } {cx = } {cy = }')
        self.Preview.c.create_image(0,0 ,image='',tag='img')
        #self.Preview.c.moveto('img',cx+self.Preview_pad , cy+self.Preview_pad)

        self.Preview.updatesregion()

        self.Preview_yPlace = Tree.winfo_rooty() - main.winfo_rooty()
        self.Preview.place(x = 0 , y = self.Preview_yPlace , width = 0 , height = 0)

    def preview_small_resize(self):
        ratio = self.Preview_ratio = math.ceil(self.image_w / self.imgW)
        #put(f'{ratio}')
        self.Preview_ratioDiv2 = self.Preview_ratio / 2


        #x , y  , _ , _ = self.c.coords()
        self.c.coords('small',[0,0,ratio,0,ratio,ratio,0,ratio,0,0])
    def preview_enter(self,e):

        i = self.c.find_withtag('current')[0]
        self.Current_tag = self.c.gettags(i)[0]

        tagN = int(self.Current_tag[1:])

        #self.c.itemconfig('small',state='normal') # moved to preview_motion
        #print(f'ENTER {self.Current_tag = }')

        w = min(main.winfo_height() - self.Preview_yPlace , get_left_pane_width())
        self.Preview.place(width=w , height=w)

        #self.Preview_size = self.objpil[tagN].size
        self.Preview_pil = self.objpil[tagN]

        #print(f'ENTER {self.Preview_pil = } {self.Preview_size =} {self.Preview_pad = }')
        #self.Preview_expanded = ImageOps.expand(self.Preview_pil, border = self.Preview_pad, fill = (255,255,255))
        #print(f'ENTER {self.Preview_expanded = }')
        self.Preview_img = ImageTk.PhotoImage(self.Preview_pil)

        self.Preview.c.itemconfig('img',image = self.Preview_img )
        self.Preview.c.moveto('img',self.Preview_imgPadX , self.Preview_imgPadX)

        self.Preview.updatesregion(1)

    def preview_leave(self,e):
        pass
        self.Preview.place(width=0 , height=0)

        main.after(50,self.preview_leave_2) # hack to prevent interpreter hang

        main.update()

        self.c.itemconfig('small',state='hidden')

    def preview_leave_2(self):
        self.c.itemconfig('small',state='hidden')

    def preview_motion(self,e):

        w = self.Preview_ratioDiv2

        cx,cy = self.c.canvasx(0), self.c.canvasy(0)
        tx,ty = self.c.coords(self.Current_tag)

        x = e.x - (tx - cx)
        y = e.y - (ty - cy)
        fx,fy = x/self.imgW, y/self.imgH

        #fx , fy = (e.x - self.Preview_ix) / self.imgW , (iy - e.y) / self.imgH
        #fx , fy = (e.x + (e.x < self.r1x)*(-w) + (e.x > self.r2x)*(w) ) / self.imgW , (e.y-w) / self.thumbH

        self.c.itemconfig('small',state='normal')
        self.c.moveto('small', (cx + e.x) - w , (cy + e.y) - w )

        #self.c.moveto()
        #print(f'M {e.x = } {e.y = } {x = } {y = } {e.x-w = } {e.y-w = }')
        #print(f'M {ty-cy = } {e.x = } {e.y = } {tx = } {ty = } {x = } {y = }')

        self.Preview.c.xview_moveto(fx)
        self.Preview.c.yview_moveto(fy)

    def view_show(self, e):
        #print(f'+++{self.s_list=}')
        p,n = self.get_selected_imgs(pils=1,names=1)
        view = View(img0_list =  p, names = n)

class GalleryManager:

    def __init__(self,parent):

        self.parent = globals()['right']
        self.pack_args = dict(side=TOP,expand=1,fill=BOTH)
        self.active_id = []
        self.galleries = dict()
        self.cat_frames = dict()
        self._all = dict()
        self.h = 0.9
        self.categories_dict = {'uncategorized':'Uncategorized Images','training':'Training Images','validation':'Validation Images','testing':'Testing Images'}
        self.categories_count = len(self.categories_dict)
        self.class_id = dict()
        self.id_class = dict()
        self.counter = 0
        self.start = 1-self.h
        self.dy = self.h / self.categories_count
        self.y = [self.start+(i*self.dy) for i in range(self.categories_count)]
        self.expanded = dict()
        self.allocated = dict()
        self.alloc_win = None
        self.send_win = None
        self.init()
    def init(self):
        for cat,y  in zip(self.categories_dict.items(),self.y):
            word,label = cat
            self.cat_frames[word] = (f:= ttk.Frame(self.parent))
            f.place(x=0,rely=y,relwidth=1,relheight=self.dy)
            self.expanded[f] = tk.IntVar(value = 0)

    def init_allocated(self):
        aw = self.alloc_win = tk.Toplevel(main)
        self.alloc_win.cbvar=dict()
        self.alloc_win.cbvar2=dict()
        self.alloc_win.cbvar3=dict()

        aw.cl = []
        aw.cl2 = []
        _hideToplevel(self.alloc_win)
        _alterToplevelClose(aw)

        c=0
        aw.L = ttk.Label(self.alloc_win,text='Select percentage of images to allocate randomly from "{}" to:')
        self.alloc_win.L.grid(row=0,column=0,columnspan=2)
        m = tk.Menu(aw,tearoff = 0)
        mb = ttk.Menubutton(aw, text = 'Options', menu = m)
        m.add_command(label = '60 20 20 Split', command = lambda : self.fill_alloc((60,20,20)))
        m.add_command(label = '50 25 25 Split', command = lambda : self.fill_alloc((50,25,25)))
        mb.grid(row=1,column=1,columnspan=1,sticky='we')
        c+=2
        for str,long in self.categories_dict.items():
            cb = ttk.Checkbutton(self.alloc_win,text=f'"{long}"')
            e = ttk.Entry(self.alloc_win , state = 'disabled')
            self.alloc_win.cbvar[str] = (tmp:=tk.IntVar(value=0))
            self.alloc_win.cbvar2[str] = cb
            self.alloc_win.cbvar3[str] = e

            cb.config(variable=tmp,command = lambda a=e,b=tmp: a.config(state = ['normal','disabled'][not b.get()]))
            tk.Grid.grid(cb,row=c,column=0,sticky='nswe')
            tk.Grid.grid(e,row=c,column=1,sticky='nswe')
            c+=1

        ttk.Button(self.alloc_win,text='Partition',command = self.do_allocated).grid(row=c,column=0,sticky='we')
        ttk.Button(self.alloc_win,text='Cancel',command = lambda: _hideToplevel(self.alloc_win)).grid(row=c,column=1,sticky='we')
        self.alloc_win.grid_columnconfigure('all',weight=1,uniform=1,pad=10)
        self.alloc_win.grid_rowconfigure(c,pad=10)
        self.alloc_win.grid_rowconfigure(0,pad=10)

        for i,d in self.galleries.items():
            for _str,g in d.items():
                g.M.entryconfigure(g.M.index('Partition this set'),command = lambda a = _str,b=g,c=i : self.show_allocated(c,a,b))

    def show_allocated(self,id,str,g):
        (aw := self.alloc_win).L.config(text = self.alloc_win.L.cget('text').format(g.get_labelframe_text()) )
        t = self._all[g]
        aw.cg = g #current gallery
        aw.cl0 = [ i for i in self.categories_dict if i != str ] #current str s list excluding current str
        aw.cl = [ (i,j) for i,j in aw.cbvar2.items() if i != str ]
        aw.cl2 = [ (i,j) for i,j in aw.cbvar3.items() if i != str ]
        aw.cl3 = [ (i,j) for i,j in self.galleries[id].items() if i != str ]
        for d1,d2 in zip(self.alloc_win.cbvar2.items(),self.alloc_win.cbvar3.items()):
            a,b = d1
            c,d = d2
            try:
                b.grid_remove()
                d.grid_remove()
            except:
                pass
        for d1,d2 in zip(self.alloc_win.cbvar2.items(),self.alloc_win.cbvar3.items()):
            a,b = d1
            c,d = d2
            if a==str:
                continue
            b.grid()
            d.grid()
        _showToplevel(self.alloc_win)

    def do_allocated(self,*e):
        aw = self.alloc_win
        g = [j for i,j in aw.cl3]
        e = [j for i,j in aw.cl2]
        eg = zip(e,g)
        count = aw.cg.count
        for e,g in eg:
            put(f'{g.get_labelframe_text() =}')

            try:
                txt = int( e.get().strip(' %') )
                txt /= 100
                txt = int(txt*count)
                #put(f'{txt = } {txt*count=}')
            except:
                pass
            else:
                cs = list(aw.cg.objpil.keys())
                #put (f'{cs=} {g.get_labelframe_text() =} {txt=}')
                cs = random.sample(cs, txt)
                aw.cg.remove_selected(g,cs)
                g.use()

    def fill_alloc(self,tup):
        aw = self.alloc_win
        e = [j for i,j in aw.cl2]
        for i,j in zip(e,tup):
            i.delete(0,'end')
            i.insert(0,f'{j} %')

    def init_send(self):
        self.send_win = tk.Toplevel(main)
        sw = self.send_win
        sw.string = 'Move {} selected item(s) to:'
        _hideToplevel(self.send_win)
        _alterToplevelClose(sw)
        self.send_win.rbvar=dict()
        self.send_win.L = ttk.Label(self.send_win,text= '',anchor='center')
        self.send_win.var = tk.StringVar()
        c=1
        self.send_win.L.grid(row=0,column=0,columnspan=2,sticky='nswe')
        for cat,long in self.categories_dict.items():
            rb=ttk.Radiobutton(self.send_win,value=cat,variable=self.send_win.var,text=f'"{long}"')
            self.send_win.rbvar[cat]=rb
            rb.grid(row=c,column=0,columnspan=1,sticky='nswe')
            c += 1
        sw = self.send_win
        sw.b1 = ttk.Button(self.send_win,text='Move')
        sw.b1.grid(row=c,column=0,sticky='nswe')
        sw.b2=ttk.Button(self.send_win,text='Cancel',command = lambda: _hideToplevel(self.send_win))
        sw.b2.grid(row=c,column=1,sticky='nswe')
        sw.grid_columnconfigure(0,weight=1,uniform=1)
        sw.grid_columnconfigure(1,weight=1,uniform=1)
        for i,d in self.galleries.items():
            for str,g in d.items():
                g.MM.entryconfigure(g.MM.index('Move to'),command = lambda a=str,b=g,c=i : self.show_send(c,a,b))
        #put(f'{sw.rbvar=}')

    def show_send(self,id,cat,g):
        sw = self.send_win
        #print(f'GOT {id=} {cat=} {g=} {sw.rbvar[cat]=}')

        sw.b1.config(command=lambda g=g: self.do_send(g))
        count = len(g.s_used)
        sw.L.config(text = sw.string.format(count) )
        for _cat,rb in self.send_win.rbvar.items():
            try:
                rb.grid_remove()
            except:
                pass
        for _cat,rb in sw.rbvar.items():
            if _cat==cat:
                print(f'{_cat=} {cat=}')
                continue
            rb.grid()

        if count:
            _showToplevel(self.send_win)

    def do_send(self,g):
        sw = self.send_win

        to=sw.var.get()
        to=self.galleries[self.active_id][to]
        g.remove_selected(to)
        to.use()
        _hideToplevel(sw)


    def hook_expand(self,m,f):
        i = m.index('Expand')
        m.entryconfigure(i,variable=self.expanded[f],command= lambda a=f : self.m_expand(a))

    def m_expand(self,f):
        v = self.expanded[f].get()
        b = self.expanded.keys()
        a = [i for i in b if i != f]
        #put(f'before {v=}')
        if v:
            for i in a:
                self.expanded[i].set(0)
                i.place_configure(relheight=0)

            f.place_configure(rely= 0.1 , relheight = self.h)
        else:
            #print('OFF')
            for i,y in zip(b,self.y):
                self.expanded[i].set(0)
                i.place_configure(rely=y,relheight=self.dy)
        #put(f'before {self.expanded[f].get()=}')
    def clear(self):
        if not self.active_id:
            return

        for k,v in self.galleries[self.active_id].items():
            v.pack_forget()

    def show(self,id):
        for k,v in self.galleries[id].items():
            v.pack(**self.pack_args)
        self.active_id = id

    def load(self,id,**kw):
        if id not in self.galleries:
            self.clear()
            self.galleries[id] = dict()
            self.class_id[id] = self.counter
            self.id_class[self.counter] = id
            self.counter += 1
            for cat,_dict in kw.items():
                label = self.categories_dict[cat]
                self.galleries[id][cat] = (g:= Gallery(f:=self.cat_frames[cat],text=label))
                g.pack(**self.pack_args)
                self.hook_expand(g.M,f)
                g._dict = _dict
                g.W = f.winfo_width()
                g.H = f.winfo_height()
                g.Threadload()
                self.active_id = id
                self._all[g]=cat
            self.init_allocated()
            self.init_send()
        else:
            self.clear()
            self.show(id)

    def exportnumpy(self):
        img = dict()
        lab = dict()

        for i,d in self.galleries.items():
            for cat,g in d.items():
                if cat not in img:
                    img[cat] = []
                    lab[cat] = []
                img[cat] += g.objpil.values()
                lab[cat] += [self.class_id[i]] * len(g.objpil)


        img2 = dict()
        lab2 = dict()
        for cat,imgs in img.items():
            tmp_ndarray = np.array( [np.array(x,dtype='uint8') for x in imgs] , dtype='uint8' )
            len_tuple = len(tmp_ndarray.shape)
            tmp_labels = np.array( lab[cat] )
            if len_tuple == 3:
                the_len , image_width , image_height = tmp_ndarray.shape
                tmp_ndarray = tmp_ndarray.reshape(the_len , image_width , image_height , 1)
                tmp_labels = tf.keras.utils.to_categorical(tmp_labels , num_classes = len(set(tmp_labels)) )
            img2[cat] = tmp_ndarray
            lab2[cat] = tmp_labels
        
   
        return [img2,lab2]

#asses path from the dialog
class Path:
    def __init__(self,tree=None,path=None):
        if tree is None:
            raise('tree=... is empty')
            return


        self.yes='\u2714'
        self.no='\u274c'

        self.tree=tree
        self.all=dict()
        self.init()

        if path:
            self.setpath(path)
        self.tree.bind('<<TreeviewSelect>>',self.rowselected)
    def init(self):
        self.cols=[0,1,2,3,4]
        self.templ=['']*len(self.cols)
        self.tree.config(columns=self.cols)
        self.tree.column('#0',width=40,stretch=1)
        test = tk.Label(main)
        font = tk.font.Font(font=test.cget('font'))
        for i,c,anchor in zip('Classes-Uncategorized-Validation-Training-Testing'.split('-'),self.cols,'w center center center center'.split()):
            self.tree.heading(c,anchor='center',text=i)
            self.tree.column(c,minwidth=1,width=font.measure(i),anchor=anchor,stretch=1)

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
            _dict[d]={'_p':_p2, #path of the class
                    '_f_id':dict(),
                    '_f_id2':dict(),
                    '_f_count':0,
                    '_v':'',
                    '_v_id':dict(),
                    '_v_id2':dict(),
                    '_v_count':0,
                    '_t':'',
                    '_t_id':dict(),
                    '_t_id2':dict(),
                    '_t_count':0,
                    '_test':'',
                    '_test_id':dict(),
                    '_test_id2':dict(),
                    '_test_count':0,
                    'value':[self.no,self.no,self.no,self.no]} #values count (4)

            _lam2 = lambda x,base = _p2: os.path.join(base,x)
            _len_generic = len(_f2)

            _dict[d]['_f_id'] = dict( zip(range(_len_generic), _f2 ) )
            _dict[d]['_f_count'] = _len_generic
            _dict[d]['_f_id2'] = dict( zip(range(_len_generic), list(map(_lam2,_f2)) ) )

            if _len_generic:
                tmp = _dict[d]['value']
                tmp[0] = _len_generic
                _dict[d]['value'] = tmp

            _v_n=(list(filter(lambda x: x.lower() == 'validation',_d2)))
            _t_n=(list(filter(lambda x: x.lower() == 'training',_d2)))
            _test_n = ( list(filter(lambda x: x.lower() == 'testing',_d2)) )[0:1]
            if _v_n:
                _v_n = _v_n[0] #incase of different spelling variations
                _dict[d]['_v']= ( _v:=os.path.join(_p2,_v_n) )
                _lam2 = lambda x,base = _v: os.path.join(base,x)
                _, _, _v_f = next(os.walk(_v))
                _len_generic = len(_v_f)
                _dict[d]['_v_id'] = dict( zip(range(_len_generic), _v_f:=list(filter(_lam,_v_f))) )
                _dict[d]['_v_id2'] = dict( zip(range(_len_generic), list(map(_lam2,_v_f))) )
                _dict[d]['_v_count'] = _len_generic
                tmp = _dict[d]['value']
                tmp[1] = _len_generic
                _dict[d]['value'] = tmp

            if _t_n:
                _t_n = _t_n[0]
                _dict[d]['_t']= ( _t:=os.path.join(_p2,_t_n) )
                _,_, _t_f = next(os.walk(_t))
                _len_generic = len(_t_f)
                _lam2 = lambda x,base = _t: os.path.join(base,x)
                _dict[d]['_t_id'] = dict( zip(range(_len_generic), _t_f:=list(filter(_lam,_t_f))) )
                _dict[d]['_t_id2'] = dict( zip(range(_len_generic), list(map(_lam2,_t_f))) )
                _dict[d]['_t_count'] = _len_generic
                tmp= _dict[d]['value']
                tmp[2] = _len_generic
                _dict[d]['value'] = tmp

            if _test_n:
                _dict[d]['_test']= ( long:=os.path.join(_p2,_test_n) )
                _,_, f = next(os.walk(long))
                f = list( filter(_lam,f) )
                longf = list( map(lambda x, base = long : os.path.join(base,x),f) )
                xlen = len(f)
                xrang = range(xlen)
                _dict[d]['_test_id'] = dict( zip(xrang,f) )
                _dict[d]['_test_id2'] = dict( zip(xrang,longf) )
                _dict[d]['_test_count'] = xlen
                tmp= _dict[d]['value']
                tmp[3] = xlen
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
            for category,title in zip('_f_id _v_id _t_id _test_id'.split(),['{Uncategorized Images}','{Validation Images}','{Training Images}','{Testing Images}']):
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



        Uncat = dict(_p = _dict['_p'], _f_id = _dict['_f_id'] , _f_id2 = _dict['_f_id2'] , _f_count = _dict['_f_count'] )
        Train = dict(_p = _dict['_t'], _f_id = _dict['_t_id'] , _f_id2 = _dict['_t_id2'] , _f_count = _dict['_t_count'] )
        Valid = dict(_p = _dict['_v'], _f_id = _dict['_v_id'] , _f_id2 = _dict['_v_id2'] , _f_count = _dict['_v_count'] )
        Test = dict(_p = _dict['_test'], _f_id = _dict['_test_id'] , _f_id2 = _dict['_test_id2'] , _f_count = _dict['_test_count'] )

        gm = globals()['GM']
        gm.load(id1, uncategorized = Uncat , training = Train , validation = Valid , testing = Test)



def _center(w,width=None,h=None):
    s1 = ['']*2
    if width:
        s1[0]=str(width)
    if h:
        s1[1]=str(h)
    #print(f'{s1=}')

    newx , newy = w.winfo_screenwidth()//2 - w.winfo_reqwidth()//2 , w.winfo_screenheight()//2 - w.winfo_reqheight()//2
    s = f'+{newx}+{newy}'
    if width and h:
        s = f'{s1[0]}x{s1[1]}{s}'
    w.geometry(s)

def _showToplevel(w):
    _center(w)
    w.deiconify()

def _hideToplevel(w):
    w.withdraw()
def _alterToplevelClose(w):
    w.wm_protocol("WM_DELETE_WINDOW", func = lambda i=w: _hideToplevel(i) )
def _exitMain(w):
    w.destroy()

# base func to select directory dialog
def _browseToDir(_dir,_title):
    path = filedialog.askdirectory(initialdir = _dir, title = _title)
    return path

# File -> (index 0) ; of validation and training dirs
def _getParentDir():
    path = _browseToDir(os.getcwd(), fileMenu.entrycget(0,'label'))

    Tpath.setpath(path)


# root window
main = tk.Tk()

# main frame
zero=ttk.Frame(main)

# main frame / up
zeroup = ttk.Labelframe(zero,text='',labelanchor='n')

# main frame / down
zerodo = ttk.Frame(zero)

zero.pack(side=TOP,expand=1,fill=BOTH)
zeroup.pack(side=TOP,fill=X,padx=5)
zerodo.pack(side=BOTTOM,expand=1,fill=BOTH,padx=5)

main.font = None

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
def show(w,geom,**kw):
    geom=geom.lower()
    if geom == 'grid':
        tmp = w.GRID_CONFIG
        All.grid_rowconfigure(tmp['row'], weight = tmp['weight'], uniform = tmp['uniform'])
        w.grid()
    elif geom == 'pack':
        w.pack_configure(**w.PACK_CONFIG)
    elif geom == 'place':
        w.place_config(**w.PLACE_CONFIG)

def ifcollapse(menu,chindex,parent,geom):
    v=menu.entrycget(0,"value")
    return
    geom = getattr(tk,"%s.%s_slaves"%(geom.capitalize(),geom))
    a = reversed(geom(parent))
    this = a.pop(chindex)

    call,label = [show,hide][menu.entrycget(0,'value')=='Collapse']
    #print(f'{call=}')
    menu.entryconfig(0,label=label)
    call(scroll,geom)

#--------------------------------------------------------------------------------------------#

# size grip
(grip := ttk.Sizegrip(main)).pack(side = BOTTOM, expand = 0 , fill = X)

#--------------------------------------------------------------------------------------------#

# dataset main frame
(frame0 := ttk.LabelFrame(zerodo, text = 'Zero')).pack(side=TOP,expand=1,fill=BOTH)
(frame1 := ttk.LabelFrame(zerodo, text = 'One')).pack(side=TOP,expand=1,fill=BOTH)
(frame2 := ttk.LabelFrame(zerodo, text = 'Two')).pack(side=TOP,expand=1,fill=BOTH)
#frame1.grid_remove()
#--------------------------------------------------------------------------------------------#
#           Emulating Tabs/Sections within the ui
class Slide(ttk.Frame):
    def __init__(self,parent,all=[],**kw):
        sel = kw.pop('sel',0)
        super().__init__(master=parent,**kw)


        self.defcur = main.cget('cursor')
        self.count=0
        self.jactive=None
        self.active=None
        self.px = Image.new('RGBA',(1,1),(255,255,255,255))

        self.bg0 = ''
        self.bg1 = 'black'
        self.mybg = [self.bg0,self.bg1]

        self.under = dict()
        self.ff = dict()
        self.id1 = dict()
        self.id2 = dict()


        for i in all:
            self.myadd(i)
        self.sel(j=sel)

    def mygrid(self,*cs):

        for j in cs:

            l,ll = self.id1[j] , self.under[j]
            l.grid(row=0,column=j,sticky='we')
            ll.grid(row=1,column=j,sticky='we')
            self.grid_columnconfigure('all',weight=1,uniform=1)

    def myadd(self,tup,append=1):

        count = self.count

        ff , text = tup
        l = tk.Label(self,text=text,anchor='center')

        if count == 0:
            self.bg0 = self.mybg[0] = l.cget('bg')

        self.under[self.count] = ll = tk.Label(self,text=' ',bg = self.bg0, height = 1,anchor='center' )
        self.under[self.count].img = ImageTk.PhotoImage(image=self.px)
        ll['image'] = ll.img

        self.ff[count] = ff
        self.id1[count] = l
        self.id2[l] = count
        self.under[count] = ll

        self.mygrid(count)
        self.count+= 1

        self.grid_rowconfigure(0,weight = 0, uniform = 0)
        self.grid_rowconfigure(1,weight = 0, uniform = 1)

        self.other_state(count)

        return l

    def other_state(self,j):
        l,ll,ff =self.id1[j] , self.under[j], self.ff[j]
        st,bn,cu = [('disabled','',self.defcur),('normal',self.sel,'hand2')][getattr(ff,'Slide_state',0)]
        l.config(state = st , cursor = cu)
        ll.config(state = st)
        l.bind('<Button>',bn)

    def sel(self,e=None, j=None):
        
        j = self.id2[e.widget] if e is not None else j
        ll = self.under[j]
        #if j == 1:
        #    GM.exportnumpy()
        self.active = self.id1[j]
        self.jactive = j
        for l,ff in zip(self.under.values(),self.ff.values()):
            l['bg']=self.bg0
            #ff.grid_remove()
            ff.pack_forget()

        ll['bg']=self.bg1
        #self.ff[j].grid()
        self.ff[j].pack(side=TOP,expand=1,fill=BOTH)
        #call = [tk.Grid.grid_remove, tk.Grid.grid][state]
        #call(self.ff[j])


class Updown(ttk.Labelframe):
    def __init__(self,parent,**kw):
        self.bannertext = kw.pop('banner_text','Banner')
        super().__init__(master=parent,**kw)
        self.main = dict()
        self.main_count = 0
        self.last_row = 5
        self.mystate = 1
        self.init_banner()
        self.lhead.bind('<ButtonPress>',self.collpase)
        self.add_main()

    def init_banner(self):

        self.banner = ttk.Labelframe(self,tex='banner')


        self.line1 = ttk.Separator(self,orient = 'horizontal')
        self.line2 = ttk.Separator(self,orient = 'horizontal')
        self.line3 = ttk.Separator(self,orient = 'horizontal')
        self.line4 = ttk.Separator(self,orient = 'horizontal')
        self.line5 = ttk.Separator(self,orient = 'vertical')
        self.line6 = ttk.Separator(self,orient = 'vertical')
        self.lhead = tk.Frame(self)
        self.lhead.L = tk.Label(self.lhead,text = self.bannertext, anchor = 'center', cursor='hand2')#,bg='red'
        self.lhead.I = tk.Label(self.lhead, cursor='hand2')
        self.lhead.L.bind('<ButtonPress>',self.collpase)
        self.lhead.I.bind('<ButtonPress>',self.collpase)
        self.lhead.L.pack(side=LEFT,expand=1,fill=X)
        self.lhead.I.pack(side=RIGHT,expand=0)
        self.lhead.I.up = ImageTk.PhotoImage(image = UP)
        self.lhead.I.do = ImageTk.PhotoImage(image = DO)
        self.lhead.I.config(image  = self.lhead.I.do)

        self.line1.grid(row=0,column=1,columnspan=2,sticky='nswe')
        self.lhead.grid(row=1,column=1,columnspan=2,sticky='we')
        self.line2.grid(row=2,column=1,columnspan=2,sticky='we')
        self.line3.grid(row=3,column=1,columnspan=2,sticky='we')
        self.line4.grid(row=self.last_row,column=1,columnspan=2,sticky='swe')

        self.line5.grid(row=0,column=0,rowspan=5,sticky='ns')
        self.line6.grid(row=0,column=3,rowspan=5,sticky='ns')

        self.grid_rowconfigure(0,weight=1,uniform=1)
        self.grid_rowconfigure(1,weight=0,uniform='00')
        self.grid_rowconfigure(2,weight=0,uniform='000')
        self.grid_columnconfigure(1,weight=1,uniform=0)
        self.grid_columnconfigure([0,3],weight=0,uniform='03')

    def set_mainframe(self):
        return tk.LabelFrame(self,text=f'main {self.main_count}',width=40,height=50)
    def add_main(self):

        f = self.set_mainframe()
        f.grid(row = self.last_row - 1,column=1,columnspan=2,sticky='swe')
        self.line4.grid(row=self.last_row)
        self.main[self.main_count] = f
        self.main_count += 1
        self.last_row += 1

    def collpase(self,e):
        self.mystate = not self.mystate
        call=[tk.Grid.grid_remove,tk.Grid.grid][self.mystate]

        self.lhead.I.config(image  = [self.lhead.I.up,self.lhead.I.do][self.mystate])
        for f in self.main.values():
            call(f)

class XUpdown(Updown):
    width = 0
    def __init__(self,parent,**kw):

        self.count = kw.pop('count',1)
        self._self = kw.pop('K')
        #self.lwidth = kw.pop('lwidth')
        super().__init__(parent,**kw)
        self.x = '\u274c'
        self.lhead.bind('<ButtonPress>','')
        self.lhead.L.config(cursor=main.cget('cursor'),anchor='w')
        if XUpdown.width == 0:
            f = tk.font.Font(font = self.lhead.L.cget('font'))
            XUpdown.width = f.measure('1'*4)//2
            #print(f'{XUpdown.width=}')
            #self.lhead.L.config(width = XUpdown.width)
        self.lhead.I.config(image = '', text = self.x)
        self.lhead.I.bind('<ButtonPress>',self.delete)
        self.lhead.Count = ttk.Label(self.lhead,text = self.count)
        self.lhead.V1 = ttk.Separator(self.lhead, orient = 'vertical')
        self.lhead.V2 = ttk.Separator(self.lhead, orient = 'vertical')

        self.lhead.Count.pack(side=LEFT , before = self.lhead.L , padx = XUpdown.width)
        self.lhead.V1.pack(side=LEFT,fill=Y , before = self.lhead.L)
        self.lhead.V2.pack(side=RIGHT,fill=Y , after = self.lhead.L)

        self.line3.grid_remove()

    def delete(self,e):
        self._self.delete(self.count)
        self.destroy()

class Slot(tk.Frame):
    def __init__(self,parent,type,**kw):
        super().__init__(parent,**kw)
        self.config(bg=RED , relief = 'raised' , bd = 10)
        self.var_col = tk.IntVar(value=0)
        self.mytype = type

        #PACK AUTOMATICALLY ON PARENT
        self.pack(side=TOP,fill=X,pady=[0,10])

        self.init_banner()
        self.init_main()


    def once_config(self,e):
        c = self.master.master
        self.scrolldown_and_bbox(c)
        e.widget.bind('<Configure>','')

    def scrolldown_and_bbox(self,c):
        self.dobbox(c)
        self.scrolldown(c)

    def dobbox(self,c):
        c.config(scrollregion = c.bbox('all'))

    def scrolldown(self,c):
        c.yview_moveto(1)

    def init_banner(self):

        self.mact = tk.Menu(self,tearoff=0)
        self.mact.add_checkbutton(label='Collapsed', command = self.collapse , variable=self.var_col)
        self.mact.add_command(label='Rename', command = self.banner_txt_show)
        self.mact.add_command(label='Delete', command = self.mydelete)
        self.mb = ttk.Menubutton(self,text = 'Action' ,menu = self.mact)
        pad = 10
        self.before_txt = ttk.Label(self, text = 'Model Name:',anchor = 'w')
        self.before_ltype = ttk.Label(self, text = 'Model Type:',anchor = 'w')
        self.txt = tk.Entry(self,relief='solid')
        self.ltype = ttk.Label(self, text = self.mytype)
        self.ltxt = ttk.Label(self, text = '')

        self.mb.grid(row=0,rowspan = 2, column = 2, sticky='nswe')
        self.before_txt.grid(row=0,rowspan = 1, column = 0, sticky='nswe')
        self.txt.grid(row=0,rowspan = 1, column = 1, sticky='nswe')
        self.before_ltype.grid(row=1,rowspan = 1, column = 0, sticky='nswe')
        self.ltype.grid(row=1,rowspan = 1, column = 1, sticky='nswe')

        self.grid_columnconfigure([0,2],weight = 1 ,uniform = 1)
        self.grid_columnconfigure(1,weight = 2 ,uniform = 1)
        self.grid_columnconfigure(3,weight = 0 ,uniform = '000')

        self.grid_rowconfigure(0,weight = 0 ,uniform = '0')
        self.grid_rowconfigure(1,weight = 0 ,uniform = '00')
        self.grid_rowconfigure(2,weight = 0 ,uniform = '000')
        self.grid_rowconfigure(2,weight = 0 ,uniform = 1)

        self.txt.bind('<KeyPress-Return>',self.banner_txt_ret)
        self.txt.focus()
    def xconfig(self,e=None):
        return
    def xmap(self):
        return
        com = self.sbv.cget('command')
        self.sbv.config(command='')
        self.c.config(scrollregion=self.c.bbox('cf'))
        self.sbv.config(command=self.c.yview)

    def banner_txt_ret(self,e):
        self.ltxt['text'] = e.widget.get()
        c = e.widget.grid_info()
        e.widget.grid_remove()
        self.ltxt.grid(**c)
        self.ltxt.myset = 1

    def banner_txt_show(self):
        if 'myset' not in vars(self.ltxt):
            return
        self.ltxt.grid_remove()
        self.txt.grid()

    def init_main(self):


        self.init_main_details()
        self.init_main_summary()


    def init_main_details(self):

        self.details = Updown(self,banner_text='Model Details',text = 'init_main_details')
        self.details.main[0].config(text = 'Layers')
        #TY
        #self.details.pack(side=TOP,expand=1,fill=BOTH , pady = [0, 10])
        self.details.grid(row=2,rowspan = 1, column = 0, columnspan = 3, sticky='nswe')

    def init_main_summary(self):

        self.summary = Updown(self,banner_text='Model Summary',text = 'init_main_summary')
        #self.summary.pack(side=TOP,expand=1,fill=BOTH , pady = 10)
        self.summary.grid(row=3,rowspan = 1, column = 0, columnspan =3, sticky='nswe')
        self.summary.bind('<Configure>',self.once_config)
    def collapse(self):
        s = self.var_col.get()

        call = [tk.Grid.grid,tk.Grid.grid_remove][s]
        call(self.details)
        call(self.summary)


    def mydelete(self):
        self.destroy()


class K(Slot):
    def __init__(self,parent,**kw):
        super().__init__(parent,'Keras Sequential',**kw)
        self.parent = parent
        self.lcount = 0
        self.dense , self.conv , self.flat , self.pool = dict() , dict() , dict() , dict()

        self.summary.add_main()
        self.summary.main[0].config(text = '')
        self.summary.main[1].config(text = 'Report')
        self.genreport = ttk.Button(self.summary.main[0],text='Generate Summary', command = self.gen)
        self.report = ttk.Label(self.summary.main[1],text='')
        self.genreport.pack(side=TOP,fill=X)
        self.report.pack(side=TOP,fill=BOTH,expand=1)


        self.train_model = Updown(self,banner_text='Training Output')
        self.train_model.main[0].config(text='')
        self.train_model.grid(row=4,rowspan = 1, column = 0, columnspan =3, sticky='nswe')
        self.run_b = ttk.Button(self.train_model.main[0],text = 'Run Model',command = self.run)
        self.run_b.pack(side=TOP,fill=X,expand=1)

        self.c = self.master.master
        self.first_conv = 1
        self.update_actions()

    def update_count(self,plus=1,minus=None):
        if plus:
            x = plus
        elif minus:
            x = minus
        self.lcount += x
        return self.lcount
    def get_label(self,parent,text,color='purple',enclose=0,font='consolas'):
        if 'myfont' not in vars(self):
            self.myfont = self.before_txt.cget('font')
            self.myfont = tk.font.Font(font=self.myfont)
        if enclose:
            text = f'"{text}"'
        f = self.myfont
        f['family'] = font
        l = tk.Label(parent,text = text , font = f , activeforeground=color)
        return l

    def update_actions(self):
        i = self.mact.index('Collapsed')
        self.mact.insert_separator(i)
        for j,c in zip(['Add a Pooling Layer','Add a Convolutional Layer','Add a Dense Neuron Layer','Add a Flattening Layer'],
        ['addPool','addConvolutional','addNeuron','addFlatten']):
            self.mact.insert_command(i,label=j,command = lambda this=c: getattr(self,this)() )
    def addLayer(self, ftext = 'Some Layer', mtext = ''):
        c = self.update_count()
        f = XUpdown(self.details.main[0] , count = c, banner_text  = ftext , K = self )
        ff = f.main[0]
        ff.config(text = mtext)
        self.pack_layer(f)
        #self.xconfigsend()

        self.scrolldown_and_bbox(self.c)

        return (c,f,ff)
    def pack_layer(self, f):
        f.pack(side=TOP,expand=1,fill=BOTH,padx=5, pady=5)
        self.xmap()
    def add_row(self,m,count,id2,type,**ops):
        try:
            getattr(self,type)[count][id2]
        except:
            try:
                getattr(self,type)[count]
            except:
                getattr(self,type)[count] = {id2 : dict()}
            else:
                getattr(self,type)[count][id2] = dict()

        for i,j in ops.items():
            if i == 'left':
                xcall = j['call']
                args = j['call_args']
                left = xcall(m,**args)
                getattr(self,type)[count][id2]['left'] = left
            elif i == 'righ':
                xcall = j['call']
                args = j['call_args']
                righ = xcall(m,**args)
                getattr(self,type)[count][id2]['righ'] = righ
            elif i == 'menu':
                args = j.pop('call_args',dict(tearoff = 0))
                mm = tk.Menu(m,**args)
                for k,v in j.items():
                    if k in 'command checkbutton radiobutton'.split():
                        func = v.pop('func',self.hass)
                        fa = v.pop('func_args',[])
                        if fa:
                            func = lambda get = func , c=count: get(c,id2,*fa)
                        else:
                            func = lambda get = func , c=count: get(c,id2)
                        getattr(tk.Menu,f'add_{k}')(mm,command = func,**v)
                mb = ttk.Menubutton(m,text = 'Options',menu = mm)
                getattr(self,type)[count][id2]['menu'] = mm
                getattr(self,type)[count][id2]['mb'] = mb

        left,righ = locals()['left'] , locals()['righ']
        row = id2 -1
        #print(f'{type=} {count=} {id2=} {row=}')
        left.grid(row=row,column=0)
        righ.grid(row=row,column=1)
        try:
            mb.grid(row=row,column=2)
        except:
            pass
        m.grid_columnconfigure('all',weight=1,uniform=1)

        self.scrolldown_and_bbox(self.c)

        return [left,righ,mm,mb]

    def addFlatten(self):
        c,_,m = self.addLayer('Flattening Layer')
        print('addFlatten called')

        id2 = 1
        self.flat[c] = {id2 : { 'flat_auto' : tk.IntVar(value=0) } }


        self.add_row(m,c,id2,'flat',left={
        'call':ttk.Label,
        'call_args':dict(text='Data Input Shape')
        },
        righ = {
        'call':tk.Entry,
        'call_args':dict(relief='solid')
        },
        menu = { 'checkbutton' : dict(label='Default: Let Keras figure it out',
        func=self.flat_auto , variable = self.flat[c][id2]['flat_auto'] ) })

    def flat_auto(self,c,cc):
        w = self.flat[c][cc]['righ']
        v = self.flat[c][cc]['flat_auto'].get()
        s = ['normal','disabled'][v]
        w.config(disabledbackground='gray',state=s)
    def addNeuron(self):
        c,_,m = self.addLayer('Neuron Layer')
        #print('addNeuron called')

        id2 = 1
        self.add_row(m,c,id2,'dense',left={
        'call':ttk.Label,
        'call_args':dict(text='Neurons Count')
        },
        righ = {
        'call':tk.Entry,
        'call_args':dict(relief='solid')
        },
        menu = { 'command' : dict(label='Default: 8',
        func=self.neuron_count , func_args = [8]) })

        id2 = 2
        self.add_row(m,c,id2,'dense',left={
        'call':ttk.Label,
        'call_args':dict(text='Activation Function')
        },
        righ = {
        'call':tk.Entry,
        'call_args':dict(relief='solid')
        },
        menu = { 'command' : dict(label='Default: "relu"',
        func=self.neuron_af , func_args = ['"relu"']) })

    def neuron_af(self,c,cc,func):
        w = self.dense[c][cc]['righ']
        w.delete(0,'end')
        w.insert(0,func)
    def neuron_count(self,c,cc,count):
        e = self.dense[c][cc]['righ']
        e.delete(0,'end')
        e.insert(0,count)
    def addConvolutional(self):
        c,_,m = self.addLayer('2D Convolutional Layer')

        dname = 'conv'
        id2 = 1
        if c == 1:
            hard_coded_width , hard_coded_height = (1024//2,1024//2)
            self.add_row(m,c,id2,dname,left={
            'call':ttk.Label,
            'call_args':dict(text='Data Shape')
            },
            righ = {
            'call':tk.Entry,
            'call_args':dict(relief='solid')
            },
            menu = { 'command' : dict(label=f'Default: ({hard_coded_width},{hard_coded_width},1)',
            func=self.conv_1st , func_args = [f'({hard_coded_width},{hard_coded_width},1)'])  })

            id2 += 1


        self.add_row(m,c,id2,dname,left={
        'call':ttk.Label,
        'call_args':dict(text='Convolution Iteration(s)')
        },
        righ = {
        'call':tk.Entry,
        'call_args':dict(relief='solid')
        },
        menu = { 'command' : dict(label='Default: 32',
        func=self.conv_count , func_args = [32])  })

        id2 += 1
        self.add_row(m,c,id2,dname,left={
        'call':ttk.Label,
        'call_args':dict(text='Filter Size')
        },
        righ = {
        'call':tk.Entry,
        'call_args':dict(relief='solid')
        },
        menu = { 'command' : dict(label='Default: (3,3)',
        func=self.conv_filter_size , func_args = ['(3,3)'])  })

        id2 += 1
        self.add_row(m,c,id2,dname,left={
        'call':ttk.Label,
        'call_args':dict(text='Activation Function')
        },
        righ = {
        'call':tk.Entry,
        'call_args':dict(relief='solid')
        },
        menu = { 'command' : dict(label='Default: "relu"',
        func=self.conv_af , func_args = ['"relu"'])  })

        #print(f'{self.conv=}')
    def conv_1st(self,c,cc,size):
        e = self.conv[c][cc]['righ']
        e.delete(0,'end')
        e.insert(0,size)

    def conv_count(self,c,cc,count):
        e = self.conv[c][cc]['righ']
        e.delete(0,'end')
        e.insert(0,count)
    def conv_filter_size(self,c,cc,size):
        e = self.conv[c][cc]['righ']
        e.delete(0,'end')
        e.insert(0,size)
    def conv_af(self,c,cc,func):
        e = self.conv[c][cc]['righ']
        e.delete(0,'end')
        e.insert(0,func)
    def addPool(self):
        c,_,m = self.addLayer('Pooling Layer')
        #print('addPool called')

        id2 = 1
        self.add_row(m,c,id2,'pool',left={
        'call':ttk.Label,
        'call_args':dict(text='Pooling Filter Type')
        },
        righ = {
        'call':tk.Entry,
        'call_args':dict(relief='solid')
        },
        menu = { 'command' : dict(label='Default: "MaxPooling2D"',
        func=self.pool_type , func_args = ['"MaxPooling2D"']) })

        id2 = 2
        self.add_row(m,c,id2,'pool',left={
        'call':ttk.Label,
        'call_args':dict(text='Pooling Filter Size')
        },
        righ = {
        'call':tk.Entry,
        'call_args':dict(relief='solid')
        },
        menu = { 'command' : dict(label='Default: (2,2)',
        func=self.pool_fs , func_args = ['(2,2)']) })

    def pool_type(self,c,cc,type):
        e = self.pool[c][cc]['righ']
        e.delete(0,'end')
        e.insert(0,type)

    def pool_fs(self,c,cc,size):
        e = self.pool[c][cc]['righ']
        e.delete(0,'end')
        e.insert(0,size)

    def hass(self,c):
        print(f'self.pass {c=}')


    def decipher_conv(self):
        new = dict()

        for count, d in self.conv.items():
            row = 1
            new[count] = dict(required = [], kw = dict() , func = 'tf.keras.layers.Conv2D')
            if count == 1:
                new[count]['kw']['input_shape'] = eval( d[row]['righ'].get() )
                row += 1

            new[count]['required'] = [ int( d[row]['righ'].get() ) ] ; row+=1
            new[count]['required'] += [ eval( d[row]['righ'].get() ) ] ; row += 1
            new[count]['kw']['activation'] = eval( d[row]['righ'].get() )

        return new
    def decipher_dense(self):
        new = dict()
        for count, d in self.dense.items():
            new[count] = dict(required = [], kw = dict() , func = 'tf.keras.layers.Dense')
            new[count]['required'] = [ int( d[1]['righ'].get() ) ]
            new[count]['kw']['activation'] = eval( d[2]['righ'].get() )

        return new
    def decipher_flat(self):
        new = dict()
        for count, d in self.flat.items():
            new[count] = dict(required = [], kw = dict() , func = 'tf.keras.layers.Flatten')

        return new
    def decipher_pool(self):
        new = dict()
        for count, d in self.pool.items():
            new[count] = dict(required = [], kw = dict() , func = 'tf.keras.layers')
            string = eval( d[1]['righ'].get() )
            new[count]['func'] = "{}.{}".format(new[count]['func'],string)
            tup = eval( d[2]['righ'].get() )
            new[count]['required'] = list(tup)

        return new

    def translate(self,prin = 1):
        new = dict()
        for i in 'pool dense flat conv'.split():
            tmp = getattr(self,"decipher_%s"%i)()
            new.update(tmp)
        if prin:
            for i in sorted(new):
                print(new[i],'\n')
        return new
    def delete(self,c):
        for i in 'pool dense flat conv'.split():
            tmp = getattr(self,i)
            if c in tmp:
                tmp.pop(c)
                break
        self.lcount -= 1

    def gen(self):
        self.model = m = tf.keras.models.Sequential()
        tf.keras.backend.clear_session()
        self.label_summary = []

        def print2(i ):
            self.label_summary += [i]
            self.report.config(text ='\n'.join(self.label_summary))

        methods = self.translate(0)
        for i in sorted(methods):
            d = methods[i]
            tmp = eval(d['func'])
            tmp = tmp(*d['required'],**d['kw'])
            m.add(tmp)
            #print(tmp)

        m.summary(print_fn=print2)
        self.scrolldown_and_bbox(self.c)
    def run(self):
        imgs , labels = globals()['GM'].exportnumpy()

        self.traini,self.trail = imgs['training'],labels['training']
        self.test_images,self.trst_labels = imgs['validation'],labels['validation']
        
        self.model.compile(optimizer='adam', loss = 'categorical_crossentropy',metrics = ['acc'])

        threading.Thread(target=self.Threadrun).start()

    def Threadrun(self):
        history = self.model.fit(self.traini,self.trail,batch_size=1,epochs = 10)
        print('Evaluating the model on the test data')
        self.model.evaluate(self.test_images,self.trst_labels,batch_size=1)
        #print('history complete!',history)

#--------------------------------------------------------------------------------------------#
class Run:
    def __init__(self,parent = frame2):
        self.sbv = tk.Scrollbar(parent)
        self.c = tk.Canvas(parent,bg=BLUE)
        self.cf = tk.Frame(self.c)
        #self.cf.bind('<Visibility>',self.once_bbox)
        self.c.bind('<Configure>',self.onconfig)
        self.sbv.config(command = self.c.yview)
        self.c.config(yscrollcommand=self.sbv.set)
        self.sbv.grid(row = 0, column = 2, rowspan = 2, sticky = 'ns')
        self.c.grid(row = 1, column = 0, columnspan = 2, sticky = 'nswe')
        self.c.create_window(0,0,window=self.cf,tag='cf',anchor='nw') # <Configure> event fired. after this
        #self.c.config(scrollregion=self.c.bbox('all'))
        parent.grid_columnconfigure(2,weight=0,uniform='0')
        parent.grid_columnconfigure(1,weight=0,uniform='00')
        parent.grid_columnconfigure(0,weight=1,uniform=1)
        parent.grid_rowconfigure(1,weight=1,uniform=1)
        self.tri = '\u25b6'

    def add(self,textvar1='',textvar2=''):
        pad = 10
        newf = ttk.Labelframe(self.cf,text='testt')
        name0 = ttk.Label(newf, text = 'Model Name:',anchor = 'w')
        type0 = ttk.Label(newf, text = 'Model Type:',anchor = 'w')
        name = ttk.Label(newf,text='Name',textvariable=textvar1)
        typee = ttk.Label(newf,text='type', textvariable = textvar2)

        b = ttk.Button(newf,text = f'{self.tri} Run')
        b.grid(row=0,rowspan = 2, column = 2, sticky='nswe')
        name0.grid(row=0,rowspan = 1, column = 0, sticky='nswe')
        name.grid(row=0,rowspan = 1, column = 1, sticky='nswe')
        typee.grid(row=1,rowspan = 1, column = 1, sticky='nswe')
        type0.grid(row=1,rowspan = 1, column = 0, sticky='nswe')
        cf=self.cf
        newf.grid_columnconfigure([0,2],weight = 1 ,uniform = 1)
        newf.grid_columnconfigure(1,weight = 2 ,uniform = 1)
        #cf.grid_columnconfigure(3,weight = 0 ,uniform = '000')

        newf2 = Updown(newf,banner_text = 'Model Statistics')
        newf2.grid(row=2,rowspan = 1, column = 0, columnspan = 3, sticky='nswe')

        newf.pack(side=TOP,fill=X,pady=[0,10])

    def onconfig(self,e):
        print('onconfig called')
        self.c.config(scrollregion=self.c.bbox('all'))
        self.c.itemconfig('cf', width = e.width)

    def once_config(self,e):
        c = self.c
        self.c.itemconfig('cf',width=e.width,hieght=e.height)
        self.scrolldown_and_bbox(c)
        e.widget.bind('<Configure>','')


    def scrolldown_and_bbox(self,c):
        self.dobbox(c)
        self.scrolldown(c)

    def dobbox(self,c):
        c.config(scrollregion = c.bbox('all'))

    def scrolldown(self,c):
        c.yview_moveto(1)

# models main frame

class Frame1Model:
    def __init__(self,parent = frame1):
        self.parent = parent
        self.prepareModel()
        self.hook = 1
    def prepareModel(self):
        parent = self.parent
        self.new_menu = tk.Menu                   (parent,tearoff=0)
        self.new_menu.add_command                 (label='Keras Sequential',command = lambda : self.startModel(K))
        self.new_mb = ttk.Menubutton              (parent,text='New Model',menu=self.new_menu)
        self.new_mb.grid(row=0,column=3,sticky='nswe')
        self.sbv = tk.Scrollbar(parent)
        self.c = tk.Canvas(parent)
        self.cf = tk.Frame(self.c)


        #self.cf.bind('<Visibility>',self.once_bbox)
        self.c.bind('<Configure>',self.onconfig)
        self.sbv.config(command = self.c.yview)
        self.c.config(yscrollcommand=self.sbv.set)

        self.sbv.grid(row = 0, column = 2, rowspan = 2, sticky = 'ns')
        self.new_mb.grid(row = 0, column = 1, sticky = 'nswe')
        self.c.grid(row = 1, column = 0, columnspan = 2, sticky = 'nswe')

        parent.grid_columnconfigure(2,weight=0,uniform='0')
        parent.grid_columnconfigure(1,weight=0,uniform='00')
        parent.grid_columnconfigure(0,weight=1,uniform=1)
        parent.grid_rowconfigure(1,weight=1,uniform=1)
        self.sbv.grid_remove()

        self.run = Run()
    def startModel(self, _class):
        parent = self.parent
        self.sbv.grid()

        if self.hook:
            self.hook = 0
            c,cf=self.c , self.cf
            x,y = c.canvasx(0),c.canvasy(0)
            self.c.create_window(0,0,window=self.cf,tag='cf',anchor='nw') # <Configure> event fired. after this
            self.c.config(scrollregion=self.c.bbox('all'))

        self.model = _class(self.cf)
        #self.c.yview_moveto(1)
        self.run.add()
    def onconfig(self,e):
        print('onconfig called')
        self.c.config(scrollregion=self.c.bbox('all'))
        self.c.itemconfig('cf', width = e.width)

#--------------------------------------------------------------------------------------------#
this = Frame1Model(frame1)
#--------------------------------------------------------------------------------------------#


#/frame0/exe entry
#/frame0/exe button
(debugbutton := ttk.Button(frame0,command=debug,text='Execute'))#.pack(expand = 0,side = TOP, fill = X)
(entryfor0 := ttk.Entry(frame0,textvariable=debugvar,font='courier 11'))#.pack(expand = 0,side = TOP, fill = X)

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

def set_left_pane_width(val , widget = paned):
    main.tk.eval(f'{str(widget)} sashpos 0 {val}')

def get_left_pane_width(widget = paned):
    #print( main.tk.eval(f'{str(paned)} pane {str(Tree)}') ) # -width {ww}
    x = main.tk.eval(f'{str(widget)} sashpos 0')
    x = float(x)
    return x

def centerPane(e):
    w = frame0.winfo_width()
    w_div_2 = int(w / 2)
    set_left_pane_width(w_div_2)
    e.widget.bind(f'<{str(e.type)}>','')

# paned/right frame/
paned.add(right:=ttk.Frame(paned),weight=1)

right.bind('<Map>',centerPane)

#--------------------------------------------------------------------------------------------#
# a mini-image view toplevel window


#                                 Toolbar
class View(tk.Toplevel):
    def __init__(self,**kw):
        self.img0_list = kw.pop('img0_list')
        self.names = kw.pop('names')
        super().__init__(**kw)
        self.count = len(self.img0_list)
        self.at = self.count - 1
        self.title(self.names[self.at])
        self.tbar = ttk.Frame(self)
        self.tbar.pack(side = TOP, fill = X)

        self.tbar_first = ttk.Frame(self.tbar)
        self.tbar_first.pack(side = TOP, expand = 1, fill = X)

        self.tbar_first_count = ttk.Label(self.tbar_first , text = '' , anchor = 'w')
        self.tbar_first_count.pack(side = LEFT, fill = X)

        self.tbar_first_sbv = ttk.Separator(self.tbar_first , orient = 'vertical')
        self.tbar_first_sbv.pack(side = LEFT, fill = Y)

        self.tbar_first_banner = ttk.Label(self.tbar_first , text = '' , anchor = 'center')
        self.tbar_first_banner.pack(side = TOP, expand = 0, fill = NONE)


        self.tbar_sbh  = ttk.Separator(self.tbar , orient = 'horizontal')
        self.tbar_sbh.pack(side = TOP, fill = X)

        self.scroll = ScrollableCanvas(self)
        self.scroll.pack(side = TOP , expand = 1 , fill = BOTH)

        self.scroll.config(highlightbackground = GREEN , highlightthickness = 2)

        s = ['disabled','normal'][self.count > 1]

        self.tbar_back = ttk.Button(self.tbar, text = 'Previous' , command = self.back , state = s )
        self.tbar_back.pack(side = LEFT)

        self.tbar_next = ttk.Button(self.tbar, text = 'Next', command = self.next , state = s)
        self.tbar_next.pack(side = LEFT, padx = [0 , 20])

        self.tbar_full = ttk.Button(self.tbar, text = 'Reset Size')
        self.tbar_full.pack(side = LEFT)

        self.tbar_fit = tk.Checkbutton(self.tbar, text = 'Fit to window' , indicatoron = 0)
        self.tbar_fit.pack(side = LEFT, padx = [0 , 20])

        self.tbar_zoomin = ttk.Button(self.tbar, text = 'Zoom In' , command = lambda: self.zoomOnClick(1))
        self.tbar_zoomin.pack(side = LEFT)

        self.tbar_zoomout = ttk.Button(self.tbar, text = 'Zoom Out' , command = lambda: self.zoomOnClick(-1))
        self.tbar_zoomout.pack(side = LEFT)

        self.scroll.c.create_image(0,0 , tag = 'img')

        self.doMapBinded = 1

        self.tbar_fit['command'] = self.fitOnClick
        self.tbar_full['command'] = self.fullOnClick

        self.lo = 0
        self.hi = self.at
        self.img = self.img0_list[self.at]

        self.scroll.bind('<Map>', self.onMap)

        self.W , self.H = self.img.size
        self.iW , self.iH = self.W , self.H #current user-set width and height

        self.setimg()

    def setimg(self,resize=1):

        self.title(self.names[self.at])
        #
        if resize:
            self.img = self.img0_list[self.at].resize((self.iW,self.iH))

        self.imgtk = ImageTk.PhotoImage(image = self.img)
        self.scroll.c.itemconfig('img' , image = self.imgtk)
        w , h = self.img.size
        self.tbar_first_banner['text'] = f'({w/self.W*100:.2f}%) {w} x {h} Pixels'
        self.tbar_first_count['text'] = '{} / {}'.format(self.at+1 , self.hi+1)
        self.scroll.updatesregion()

    def next(self):
        #print(f'next {self.at=}')
        if self.at < self.hi :
            self.at += 1
            self.setimg()

    def back(self):
        #print(f'back {self.at=}')
        if self.at > self.lo :
            self.at += -1
            self.setimg()


    def onMap(self,e,*r):
        #print(f'{ r = } { e.widget = }')
        return
        e.widget.c.xview_moveto(0.0)
        e.widget.c.yview_moveto(0.0)


    def fitOnClick(self):

        if 'fitVar' not in vars(self.tbar_fit):
            self.tbar_fit.fitVar = tk.IntVar(value = 1)
            self.tbar_fit.config(variable = self.tbar_fit.fitVar)

        v = self.tbar_fit.fitVar.get()
        if v:
            self.scroll.c.bind('<Configure>', self.fitResize)
            self.scroll.c.event_generate('<Configure>')
        else:
            self.scroll.c.bind('<Configure>',"" )
            #View_fullOnClick()

        #print(f'View_fitOnClick {View_tbar_fit.fitVar.get() = }')

    def fitResize(self,e):
        cw , ch = e.widget.winfo_width() , e.widget.winfo_height()

        w , h = self.img.size
        r = w/h

        ch = r*cw
        iw = int( ch/r )
        ih = int( iw*r )

        #print(f'{w = } {h =} {r = } {cw =} {ch =} {iw =} {ih =} ')
        #self.img= self.img0_list[self.at].resize((iw,ih))
        self.iW , self.iH = iw , ih

        self.setimg()

        e.widget.moveto('img',0,0)
        e.widget.xview_moveto(0.0)
        e.widget.yview_moveto(0.0)
        self.scroll.updatesregion()

    def fullOnClick(self):

        #self.img= self.img0_list[self.at] #.resize((self.W,self.H)) # assumes imgs are of same size &
        self.iW , self.iH = self.W , self.H

        self.setimg()

    def zoomOnClick(self,sign):

        r = sign*0.1
        w , h = self.img.size
        w += r*w
        h += r*h

        w = int(w)
        h = int(h)

        #self.img= self.img0_list[self.at].resize((w,h))
        self.iW , self.iH = w , h

        self.setimg()

def Shift_start(e):
    if not e.keysym.lower().startswith('shift'):
        return
    global SHIFT_ON
    SHIFT_ON = 1
    #print(f'+++{e.keysym=} {SHIFT_ON=}')

def Shift_end(e):
    if not e.keysym.lower().startswith('shift'):
        return
    global SHIFT_ON
    SHIFT_ON = 0



#--------------------------------------------------------------------------------------------#
# bind Shift key
main.bind('<KeyPress>',Shift_start)
main.bind('<KeyRelease>',Shift_end)
#--------------------------------------------------------------------------------------------#

# paned/right frame/class banner frame/
(bannerframe:=ttk.Labelframe(right,text=_textcenter('Class'))).place(x=0 , y = 0, relwidth=1, relheight=0.1)


#--------------------------------------------------------------------------------------------#

# paned/right frame/class banner frame/class banner label
(banner:=ttk.Label(bannerframe,text='')).pack(side=TOP )


main.Labelfont = tkinter.font.Font(font=banner.cget('font'))

##print(main.Labelfont.config(weight='bold'))
#--------------------------------------------------------------------------------------------#



#paned/right frame/second paned window/"uncategorized" frame/
#(All:=Gallery(right,text='Uncategorized Images')).place(rely=0.1 , x = 0, relwidth=1, relheight=0.225)


#paned/right frame/top frame
#(Train:=Gallery(right,text='Training Images')).place(rely=0.325 , x = 0, relwidth=1, relheight=0.225)


#paned/right frame/top frame/frame00/parent path LabelAB
#(frame00 := LabelAB(Train)).pack(expand = 1,side = TOP, fill = X)


#--------------------------------------------------------------------------------------------#


#paned/right frame/bottom frame
#(Valid:=Gallery(right,text='Validation Images')).place(rely=0.55 , x = 0, relwidth=1, relheight=0.225)

#paned/right frame/top frame
#(Test:=Gallery(right,text='Testing Images')).place(rely=0.775 , x = 0, relwidth=1, relheight=0.225)


#chosen path assesor
Tpath=Path(tree=tree)


main.title('A TF Classifier')
#Moveto = To([All,Train,Valid,Test])

#zerodo.grid_columnconfigure('all',weight=1,uniform='default')
#zerodo.grid_rowconfigure('all',weight=1,uniform='default')

frame0.Slide_state=1
frame1.Slide_state=1
frame2.Slide_state=1

switch = Slide(zeroup,[(frame0,'Configure Dataset'),(frame1,'Build Model'),(frame2,'Predict')],sel=0)
switch.pack(side=TOP,expand=0,fill=NONE)


#main.wm_attributes('-top',1)



_center(main,500,500)

GM = GalleryManager(right)

main.mainloop()
