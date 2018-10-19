#!/usr/bin/env python

import os, sys, getopt, signal, random, time, warnings
#import gobject, gtk, pango

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject
from gi.repository import GLib

import pysql, sutil
 
GAP = 4                     # Gap in pixels
TABSTOP = 4

FGCOLOR  = "#000000"
BGCOLOR  = "#ffff88"
FRCOLOR  = "#cccc00"

TOPSTOP = 50
BUTSTOP = 50

# Where things are stored (backups, orgs, macros)
#config_dir = os.path.expanduser("~/.pystick")

# ------------------------------------------------------------------------
# Collection of windows:

class stickList():

    def __init__(self):
        self.data = []
        pass

    def add(self, item):
        self.data.append(item)

# Globals
slist = stickList()
xxx = 0; yyy = 50

# ------------------------------------------------------------------------
# The surface of the yellow sticky

class stickDoc(Gtk.DrawingArea):

    def __init__(self, par, head, text):

        self.par    = par
        self.parwin = par.window
        self.head   = head
        self.text   = text
        self.gap    = GAP

        # Parent widget
        GObject.GObject.__init__(self)
        #self.set_flags(Gtk.CAN_FOCUS | Gtk.CAN_DEFAULT| Gtk.SENSITIVE | Gtk.PARENT_SENSITIVE)
        #self.set_flags(Gtk.CAN_FOCUS | Gtk.SENSITIVE)
        self.set_flags(Gtk.SENSITIVE)

        self.set_events(Gdk.EventMask.ALL_EVENTS_MASK )

        self.colormap = Gtk.widget_get_default_colormap()
        self.fgcolor  = self.colormap.alloc_color(FGCOLOR)
        self.bgcolor  = self.colormap.alloc_color(BGCOLOR)
        self.frcolor  = self.colormap.alloc_color(FRCOLOR)

        self.modify_bg(Gtk.StateType.NORMAL, self.bgcolor)
        self.pangolayout = self.create_pango_layout("a")

        self.connect("motion-notify-event", self.area_motion)
        self.connect("button-press-event", self.area_button)
        self.connect("expose-event", self.area_expose_cb)
        self.connect("key-press-event", self.key_press_event)
        #self.connect("destroy", self.OnExit)

    def area_button(self, area, event):
        #print "yellow butt"
        if  event.type == Gdk.EventType.BUTTON_PRESS:
            self.ex = event.x; self.ey = event.y
        elif  event.type == Gdk._2BUTTON_PRESS:
            #se = sticked.StickEd(self.par.window, 
            #    self.par.me.mainwin.done_dlg, self.head, self.text)
            pass
        return False

    def area_motion(self, area, event):
        #print "motion event", event.get_state(), event.x, event.y
        if event.get_state() & Gdk.ModifierType.BUTTON1_MASK:
            #print "dragx", self.ex, event.x, "dragy", self.ey, event.y
            #par = self.get_parent_window()
            x, y = self.parwin.get_position()
            newx = int(x + (event.x - self.ex))
            newy = int( y + (event.y-self.ey))
            
            self.parwin.move(newx, newy)
            self.parwin.xx = newx; self.parwin.yy = newy
            #global stickdb
            #stickdb.putpos(self.head, newx, newy)
            #print  self.parwin.xx, self.parwin.yy

    def key_press_event(self, text_view, event):
        print "widget keypress"
        #if event.get_state() & Gdk.ModifierType.MOD1_MASK:
        #    if event.keyval == Gdk.KEY_x or event.keyval == Gdk.KEY_X:
        #        sys.exit(0)
        #return False
        return True 

    def setfont(self, fam, size):
        fd = Pango.FontDescription()
        fd.set_family(fam)
        fd.set_size(size * Pango.SCALE);
        self.pangolayout.set_font_description(fd)

        warnings.simplefilter("ignore")
        # Get Pango steps
        self.cxx, self.cyy = self.pangolayout.get_pixel_size()
        warnings.simplefilter("default")

        # Get Pango tabs
        '''self.tabarr = Pango.TabArray(80, False)
        for aa in range(self.tabarr.get_size()):
            self.tabarr.set_tab(aa, Pango.TabAlign.LEFT, aa * TABSTOP * self.cxx * Pango.SCALE)
        self.pangolayout.set_tabs(self.tabarr)
        ts = self.pangolayout.get_tabs()
        if ts != None:
            al, self.tabstop = ts.get_tab(1)
        self.tabstop /= self.cxx * Pango.SCALE'''

    def area_expose_cb(self, area, event):

        style = self.get_style()
        self.gc = style.fg_gc[Gtk.StateType.NORMAL]

        gcx = Gdk.GC(self.window); gcx.copy(self.gc)
        gcx.set_foreground(self.fgcolor)

        self.setfont("system", 14)
        self.pangolayout.set_text(self.head)
        x = 2 * self.gap; y = self.gap
        self.window.draw_layout(gcx, x, y, self.pangolayout, self.fgcolor, self.bgcolor)
        cxx, cyy = self.pangolayout.get_pixel_size()

        self.setfont("system", 11)
        self.pangolayout.set_text(self.text)
        x = 2 * self.gap; y += self.cyy + self.cyy / 2
        self.window.draw_layout(gcx, x, y, self.pangolayout, self.fgcolor, self.bgcolor)
        cxx2, cyy2 = self.pangolayout.get_pixel_size()

        #print  cxx, cyy, cxx2, cyy2

        # Resize if needed:
        if cxx < cxx2: cxx = cxx2
        rqx = cxx + 4 * self.gap;
        rqy = cyy + cyy2 + 2 * self.gap

        self.ww, self.hh = self.get_size_request()
        if self.ww != rqx or self.hh != rqy:
            self.set_size_request(2 * rqx, 2 * rqy)

        win = self.get_window()
        ww, hh = Gdk.Window.get_size(win)

        #print "ww,hh", ww, hh
        ww -= 1; hh -= 1

        # Draw Closer cross
        ulx = ww -  12;  uly = 2
        urx = ww -   2;  ury = 2
        llx = ww -  12;  lly = 12
        lrx = ww -   2;  lry = 12

        gcx.set_line_attributes(1, Gdk.LINE_SOLID,
                        Gdk.CAP_NOT_LAST, Gdk.JOIN_MITER)

        win.draw_line(gcx, ulx, uly, lrx, lry)
        win.draw_line(gcx, llx, lly, urx, ury)

        # Draw frame
        gcx.set_line_attributes(2, Gdk.LINE_SOLID,
            Gdk.CAP_BUTT, Gdk.JOIN_MITER)
        gcx.set_foreground(self.frcolor)
        win.draw_line(gcx, 0, 0, ww, 0)
        win.draw_line(gcx, ww, 0, ww, hh)
        win.draw_line(gcx, 0, 0, 0, hh)
        win.draw_line(gcx, 0, hh, ww, hh)

# ------------------------------------------------------------------------
# Sticky window:

class stickWin():

    def __init__(self, me, head, text):

        global xxx, yyy, slist
        self.head = head
        self.me = me
        self.text = text

        www = Gdk.Screen.width(); hhh = Gdk.Screen.height();

        self.window = window = Gtk.Window(Gtk.WindowType.TOPLEVEL)
        #self.window = window = Gtk.Window(Gtk.WindowType.POPUP)

        window.set_default_size(50, 50)
        window.set_decorated(False)

        try:
            window.set_icon_from_file("icon.png")
        except:
            pass

        # That wat the window manager will not list it
        window.set_type_hint(Gdk.WindowTypeHint.UTILITY)
        #window.set_type_hint(Gdk.WindowTypeHint.DIALOG)
        #window.set_type_hint(Gdk.WindowTypeHint.TOOLBAR)

        window.set_events(Gdk.EventMask.ALL_EVENTS_MASK )

        '''window.set_events(  Gdk.EventMask.POINTER_MOTION_MASK |
                    Gdk.EventMask.POINTER_MOTION_HINT_MASK |
                    Gdk.EventMask.BUTTON_PRESS_MASK |
                    Gdk.EventMask.BUTTON_RELEASE_MASK |
                    Gdk.EventMask.KEY_PRESS_MASK |
                    Gdk.EventMask.KEY_RELEASE_MASK |
                    Gdk.EventMask.FOCUS_CHANGE_MASK )'''

        window.set_accept_focus(False)
        window.connect("key-press-event", self.key_press_event)
        window.connect("button-press-event", self.area_button)

        #window.connect("motion-notify-event", self.area_motion)
        #window.connect("destroy", self.OnExit)
        #window.connect("event", self.OnExit)

        window.set_flags(Gtk.SENSITIVE)
        #window.set_flags(Gtk.CAN_FOCUS | Gtk.SENSITIVE)
        #window.set_flags(Gtk.CAN_FOCUS | Gtk.CAN_DEFAULT| Gtk.SENSITIVE | Gtk.PARENT_SENSITIVE)
        window.set_destroy_with_parent(True )
        window.set_transient_for(me)

        self.sticky = stickDoc(self, head, text)
        window.add(self.sticky)
        window.show_all()
        sutil.usleep(1)           # Present window
        
        #Gdk.Window.set_skip_pager_hint(window.get_window(), True )
        #Gdk.Window.set_skip_taskbar_hint(window.get_window(), True )
        #window.set_keep_above(False)
        #Gdk.Window.set_decorations(window.get_window(), Gdk.DECOR_BORDER)
        
        if Gdk.Display.supports_composite(Gdk.Display.get_default()):
            Gdk.Window.set_composited(window.get_window(), True )
            Gdk.Window.set_opacity(window.get_window(), .5)

        # Arrange it in peace
        '''yyy = TOPSTOP; xxx = www / 2
        for ww in slist.data:
            xx, yy = Gdk.Window.get_position(ww.window.get_window())
            ww, hh = Gdk.Window.get_size(ww.window.get_window())
            print "setting position", xx, yy, "size", ww, hh
            if yyy + hh >= hhh - 2 * BUTSTOP:
                xxx += 200
                yyy = TOPSTOP
                if xxx > www - 100:
                    xxx = TOPSTOP
            else:
                yyy +=  hh + 4
           '''
           
        #print  xxx, yyy
        #window.move(xxx, yyy)
        #self.window.xx = xxx; self.window.yy = yyy
        #slist.add(self)
        #global stickdb
        #stickdb = pysql.sticksql(config_dir + "/data")

    def area_button(self, area, event):
        #print "win butt", event
        win = self.window.get_window()
        ww, hh = Gdk.Window.get_size(win)

        ulx = ww -  12;  uly = 2
        urx = ww -   2;  ury = 2
        llx = ww -  12;  lly = 12
        lrx = ww -   2;  lry = 12

        if event.x > ulx and event.x < urx:
            if event.y > ury and event.y < lry:
                #print "hit", event
                self.window.destroy()
        return False

    def key_press_event(self, text_view, event):
        print "window keypress", self.head
        #if event.get_state() & Gdk.ModifierType.MOD1_MASK:
        #    if event.keyval == Gdk.KEY_x or event.keyval == Gdk.KEY_X:
        #        sys.exit(0)
        #return False
        
        if event.keyval == Gdk.KEY_Tab:
            #self.me.mainwin.next(self)
            pass
        return False 

    def invalidate(self, rect = None):                        
        if rect == None:
            ww, hh = self.window.window.get_size()
            rect = (0,0, ww, hh)
        #print "Invalidate:", rect
        self.window.window.invalidate_rect(rect, False)

    def OnExit(self, aa, bb = ""):
        print "onexit", bb
        #while Gtk.main_level():
        #    Gtk.main_quit()
        
        xx, yy = self.window.window.get_position()

        #pedconfig.conf.sql.put("xx", xx)
        #//pedconfig.conf.sql.put("yy", yy)

        ww, hh = self.window.window.get_size()

        #//pedconfig.conf.sql.put("ww", ww)
        #//pedconfig.conf.sql.put("hh", hh)
        
        #print "remember sticky", xx, yy, ww, hh




