#!/usr/bin/env python

import sys, traceback, os, time

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject
from gi.repository import GLib

disp = Gdk.Display.get_default()
scr = disp.get_default_screen()

#print "num_mon",  scr.get_n_monitors()    
#for aa in range(scr.get_n_monitors()):    
#    print "mon", aa, scr.get_monitor_geometry(aa);
    

# ------------------------------------------------------------------------
# Get current screen (monitor) width and height

def get_screen_wh():

    ptr = disp.get_pointer()
    mon = scr.get_monitor_at_point(ptr[1], ptr[2])
    geo = scr.get_monitor_geometry(mon)
    www = geo.width; hhh = geo.height
    if www == 0 or hhh == 0:
        www = Gdk.get_screen_width();
        hhh = Gdk.get_screen_height();
    return www, hhh    

# ------------------------------------------------------------------------
# Get current screen (monitor) upper left corner xx / yy

def get_screen_xy():

    ptr = disp.get_pointer()
    mon = scr.get_monitor_at_point(ptr[1], ptr[2])
    geo = scr.get_monitor_geometry(mon)
    return geo.x, geo.y

# ------------------------------------------------------------------------
# Print an exception as the system would print it

def print_exception(xstr):
    cumm = xstr + " "
    a,b,c = sys.exc_info()
    if a != None:
        cumm += str(a) + " " + str(b) + "\n"
        try:
            #cumm += str(traceback.format_tb(c, 10))
            ttt = traceback.extract_tb(c)
            for aa in ttt: 
                cumm += "File: " + os.path.basename(aa[0]) + \
                        " Line: " + str(aa[1]) + "\n" +  \
                    "   Context: " + aa[2] + " -> " + aa[3] + "\n"
        except:
            print "Could not print trace stack. ", sys.exc_info()
    print cumm


# ------------------------------------------------------------------------
# Show a regular message:

def message(strx, parent = None, title = None, icon = Gtk.MessageType.INFO):

    dialog = Gtk.MessageDialog(parent, Gtk.DialogFlags.DESTROY_WITH_PARENT,
        icon, Gtk.ButtonsType.CLOSE, strx)
    
    dialog.set_modal(True)   
    
    if title:
        dialog.set_title(title)
    else:
        dialog.set_title("DBGui Message")

    # Close dialog on user response
    dialog.connect("response", lambda d, r: d.destroy())
    dialog.show()

# -----------------------------------------------------------------------
# Sleep just a little, but allow the system to breed

def  usleep(msec):

    got_clock = time.clock() + float(msec) / 1000
    #print got_clock
    while True:
        if time.clock() > got_clock:
            break
        Gtk.main_iteration_do(False)        

# ------------------------------------------------------------------------
# Create temporary file, return name. Empty string ("") if error.

def tmpname(indir, template):
    
    fname = ""
    if not os.access(indir, os.W_OK):
        print "Cannot access ", indir
        return fname
        
    cnt = 1;
    while True:
        tmp = indir + "/" + template + "_" + str(cnt)
        if not os.access(tmp, os.R_OK): 
            fname = tmp
            break 
        # Safety valve   
        if cnt > 10000:
            break
    return fname

# ------------------------------------------------------------------------
# Execute man loop

def mainloop():
    while True:
        ev = Gdk.event_peek()
        #print ev
        if ev:
            if ev.type == Gdk.EventType.DELETE:
                break
            if ev.type == Gdk.EventType.UNMAP:
                break
        if Gtk.main_iteration_do(True):
            break
    
class Unbuffered(object):
   def __init__(self, stream):
       self.stream = stream
       
   def write(self, data):
       self.stream.write(data)
       self.stream.flush()
       
   def writelines(self, datas):
       self.stream.writelines(datas)
       self.stream.flush()
       
   def __getattr__(self, attr):
       return getattr(self.stream, attr)



