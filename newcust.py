#!/usr/bin/env python

import os, sys, getopt, signal
#import gobject, gtk, pango

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject
from gi.repository import GLib

import random, time
import treehand, sutil, padding

class NewCust(Gtk.Window):
    
    def __init__(self, par, cback, uuid_name, datax = None):
    
        self.cback = cback
        self.ok = False
        self.arr = []
        GObject.GObject.__init__(self)
        self.set_transient_for(par)
        self.set_modal(True)
        
        if datax  == None:
            self.set_title("Create new DIBA customer.")
        else:
            self.set_title("Edit DIBA customer.")
            
        self.set_position(Gtk.WindowPosition.CENTER)
        
        #ic = Gtk.Image(); ic.set_from_stock(Gtk.STOCK_DIALOG_INFO, Gtk.IconSize.BUTTON)
        #window.set_icon(ic.get_pixbuf())
        #www = Gdk.Screen.width(); hhh = Gdk.Screen.height();
        
        #www, hhh = sutil.get_screen_wh()
        www, hhh = 1024, 768
        
        self.set_default_size(3*www/4, 3*hhh/4)
        
        #self.set_flags(Gtk.CAN_FOCUS | Gtk.SENSITIVE)
         
        self.set_events(  Gdk.EventMask.POINTER_MOTION_MASK |
                            Gdk.EventMask.POINTER_MOTION_HINT_MASK |
                            Gdk.EventMask.BUTTON_PRESS_MASK |
                            Gdk.EventMask.BUTTON_RELEASE_MASK |
                            Gdk.EventMask.KEY_PRESS_MASK |
                            Gdk.EventMask.KEY_RELEASE_MASK |
                            Gdk.EventMask.FOCUS_CHANGE_MASK )
         
        self.connect("key-press-event", self.key_press_event)        
        self.connect("button-press-event", self.area_button)        
        
        try:
            self.set_icon_from_file("icon.png")
        except:
            pass 

        self.arr.append(("custid", str(uuid_name)))
        
        # We use gobj instead of SIGALRM, so it is more multi platform
        #GObject.timeout_add(1000, self.handler_tick)
        
        vbox = Gtk.VBox()
        vbox2 = Gtk.VBox();
      
        sg = Gtk.SizeGroup(Gtk.SizeGroupMode.HORIZONTAL)
          
        tp1 =("Full Name: ", "cname", "Enter full name (TAB to advance)", None)
        tp2 = ("Date of birth: ", "dob", "Date of birth, YYYY/MM/DD", None) 
        lab1, lab2 = self.entryquad(vbox2, tp1, tp2)
        sg.add_widget(lab1);     sg.add_widget(lab2)
        
        tp3 = ("Location of birth: ", "lob", "Location, City and Country", None) 
        tp4 = ("Numeric ID: ", "numid", "Social Security Number or national ID", None) 
        lab3, lab4 = self.entryquad(vbox2, tp3, tp4)
        sg.add_widget(lab3);     sg.add_widget(lab4)
        
        tp3a = ("Address Line 1: ", "addr1", "Address line one. (Number, Street)", None) 
        tp4a = ("Address Line 2: ", "addr2", "Addressline two. (if applicable)", None) 
        lab5, lab6 = self.entryquad(vbox2, tp3a, tp4a)
        sg.add_widget(lab5);     sg.add_widget(lab6)
        
        tp5 = ("City: ", "city", "City or Township", None) 
        tp6 = ("County / Territory: ", "county", "County or Teritory or Borough", None) 
        lab7, lab8 = self.entryquad(vbox2, tp5, tp6)
        sg.add_widget(lab7);     sg.add_widget(lab8)
        
        tp7 = ("Zip: ", "zip", "Zip code or Postal code", None) 
        tp8 = ("Country: ", "country", "Coutry of residence", None) 
        lab9, lab10 = self.entryquad(vbox2, tp7, tp8)
        sg.add_widget(lab9);     sg.add_widget(lab10)
        
        tp7a = ("Phone: ", "phone", "Phone or text number. ", None) 
        tp8a = ("Email: ", "email", "Primary Email", None) 
        lab9a, lab10a = self.entryquad(vbox2, tp7a, tp8a)
        sg.add_widget(lab9a);     sg.add_widget(lab10a)
        
        tp7b = ("Phone: (secondary)", "phone2", "Secondary phone or text number. ", None) 
        tp8b = ("Email: (Secondary)", "email2", "Secondary Email", None) 
        lab9b, lab10b = self.entryquad(vbox2, tp7b, tp8b)
        sg.add_widget(lab9b);     sg.add_widget(lab10b)
        
        self.vspacer(vbox)
        vbox.pack_start(vbox2, False, 0, 0)
        
        vbox3 = Gtk.VBox();
        
        lab1a = self.textviewpair(vbox3, "Comments: ", "comments", \
                "Enter comments. This field could contain additiona data. "
                "   (Ctrl-TAB to advance)")
        sg.add_widget(lab1a)
        
        lab5 = self.textviewpair(vbox3, "Free Text: ", "freetext", \
                "Enter free flowing text, relevant to the entry.")
        sg.add_widget(lab5)
        
        lab2a = self.textviewpair(vbox3, "Log entry:", "log", \
                "Enter log entry. (Append at end, keep old entries.)")
        sg.add_widget(lab2a)
        
        vbox.pack_start(vbox3, False, 0, 0)
        self.vspacer(vbox, expand = True)
        
        # Draw buttons
        hbox = Gtk.HBox()
        
        #lab00 = Gtk.Label(label="        ")
        #hbox.pack_start(lab00, False, 0, 0)
        
        lab0 = Gtk.Label(label="               " \
                "Customer ID:  '" + str(uuid_name) + "'")
        hbox.pack_start(lab0, False, 0, 0)
        
        lableft = Gtk.Label(label="     ")
        hbox.pack_start(lableft, True, 0, 0)
        
        lab1 = Gtk.Label("Alt-X or ESC or Alt-C to Exit, Alt-O to OK, TAB or Ctrl-TAB to advance")
        hbox.pack_start(lab1, False, 0, 0)
        
        lab2 = Gtk.Label(label="     ")
        hbox.pack_start(lab2, False, 0, 0)
        
        butt1 = Gtk.Button("     _OK      ")
        butt1.connect("clicked", self.click_ok, self)
        hbox.pack_start(butt1, False, 0, 0)
        self.spacer(hbox)
        
        butt2 = Gtk.Button("    _Cancel    ")
        butt2.connect("clicked", self.click_can, self)
        hbox.pack_start(butt2, False, 0, 0)
        self.spacer(hbox)
        
        self.vspacer(vbox)
        vbox.pack_start(hbox, False, 0, 0)
        self.vspacer(vbox)
        self.add(vbox)
        
    # Run as modal dialog until destroyed
    def run(self):
        self.show_all()
        while True:
            ev = Gdk.event_peek()
            #print ev
            if ev:
                if ev.type == Gdk.DELETE:
                    break
                if ev.type == Gdk.UNMAP:
                    break
            Gtk.main_iteration_do()
            
        return self.ok
        
    # --------------------------------------------------------------------
    
    def spacer(self, hbox, xstr = "    ", expand = False):
        lab = Gtk.Label(label=xstr)
        hbox.pack_start(lab, expand, 0, 0)
       
    def vspacer(self, vbox, xstr = "     ", expand = False):
        lab = Gtk.Label(label=xstr)
        vbox.pack_start(lab, expand , 0, 0)
        
    def click_ok(self, butt, xx):
        err = self.cback(self)
        if err == "":
            self.ok = True
            self.destroy()
        else:
            sutil.message("Operator entry incomplete.\n\n" + err, self)
        pass
        
    def click_can(self, butt, xx):
        self.destroy()
        pass
    
    def key_press_event(self, win, event):
        if event.keyval == Gdk.KEY_Escape:
            self.destroy()
        #print "keystate", event.get_state()
        if event.keyval == Gdk.KEY_x and event.get_state() & Gdk.ModifierType.MOD1_MASK:
            self.destroy()
    
    def  area_button(self, butt):
        pass
    
    def scrolledtext(self, name, body = None):
        textx = Gtk.TextView();
        textx.set_border_width(4)
        self.arr.append((name, textx))
        if body != None: 
            self.text.grab_focus()
            buff = Gtk.TextBuffer(); buff.set_text(body)
            self.text.set_buffer(buff)

        sw = Gtk.ScrolledWindow()
        sw.add(textx)
        sw.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
        sw.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        return sw
    
    # Expects two tuples of stuff
    # labtext, labname, tip, defval = None: 
    
    def entryquad(self, vbox, entry1, entry2):
    
        hbox2 = Gtk.HBox()
        
        lab1a = Gtk.Label(label="      ")
        hbox2.pack_start(lab1a, False, 0, 0)
        lab1 = Gtk.Label(label=entry1[0]) ; lab1.set_alignment(1, 0)
        lab1.set_tooltip_text(entry1[2])
        hbox2.pack_start(lab1, False, 0, 0)
        lab1a = Gtk.Label(label="      ")
        hbox2.pack_start(lab1a, False, 0, 0)
        headx = Gtk.Entry();
        if entry1[3] != None: 
            headx.set_text(entry1[3])
        hbox2.pack_start(headx, True, 0, 0)
        lab3 = Gtk.Label(label="        ")
        hbox2.pack_start(lab3, False, 0, 0)
        self.arr.append((entry1[1], headx))
        
        lab1b = Gtk.Label(label="      ")
        hbox2.pack_start(lab1b, False, 0, 0)
        lab2 = Gtk.Label(label=entry2[0])  ; lab2.set_alignment(1, 0)
        lab2.set_tooltip_text(entry2[2])
        hbox2.pack_start(lab2, False, 0, 0)
        lab1b = Gtk.Label(label="      ")
        hbox2.pack_start(lab1b, False, 0, 0)
        headx2 = Gtk.Entry();
        if entry2[3] != None: 
            headx2.set_text(entry2[3])
        hbox2.pack_start(headx2, True, 0, 0)
        lab3b = Gtk.Label(label="        ")
        hbox2.pack_start(lab3b, False, 0, 0)
        self.arr.append((entry2[1], headx2))
        self.vspacer(vbox)
        vbox.pack_start(hbox2, True, True, 0)
        return lab1, lab2  
    
    # Create a label entry pair    
    def entrypair(self, vbox, labtext, labname, tip, defval = None): 
        
        hbox2 = Gtk.HBox()
        lab1b = Gtk.Label(label="      ")
        hbox2.pack_start(lab1b, False, 0, 0)
        
        lab1 = Gtk.Label(label=labtext) ; lab1.set_alignment(1, 0)
        hbox2.pack_start(lab1, False, 0, 0)
        
        lab1a = Gtk.Label(label="      ")
        hbox2.pack_start(lab1a, False, 0, 0)
        
        headx = Gtk.Entry();
        if defval != None: 
            headx.set_text(defval)
        hbox2.pack_start(headx, True, 0, 0)
        lab3 = Gtk.Label(label="        ")
        hbox2.pack_start(lab3, False, 0, 0)
        self.arr.append((labname, headx))
        
        self.vspacer(vbox)
        vbox.pack_start(hbox2, False, 0, 0)
        lab1.set_tooltip_text(tip)

        return lab1

    def textviewpair(self, vbox, labtext, labname, tip, defval = None): 
            
        hbox2 = Gtk.HBox(); 
        self.spacer(hbox2)
        
        lab2a = Gtk.Label(label="     ")
        hbox2.pack_start(lab2a, False , 0, 0)
        
        lab2 = Gtk.Label(label=labtext); lab2.set_alignment(1, 0)
        lab2.set_tooltip_text(tip)
        hbox2.pack_start(lab2, False , 0, 0)
        sw = self.scrolledtext(labname)
        self.spacer(hbox2)
        hbox2.pack_start(sw, True, True, 0)
        self.spacer(hbox2)
        self.vspacer(vbox)
        
        lab2b = Gtk.Label(label="     ")
        hbox2.pack_start(lab2b, False , 0, 0)
        vbox.pack_start(hbox2, True, True, 0)
        return lab2    
        
    def handler_tick(self):
        GObject.timeout_add(1000, self.handler_tick)
            
    '''wid = padding.Padding()
    wid.set_size_request(lenx, 30)
    cm = Gdk.colormap_get_system() 
    col = cm.alloc_color(10, 100, 100)
    wid.modify_fg(Gtk.StateType.NORMAL, col)
    wid.modify_bg(Gtk.StateType.NORMAL, col)
    wid.modify_fg(Gtk.StateType.ACTIVE, col)
    wid.modify_bg(Gtk.StateType.ACTIVE, col)
    wid.modify_fg(Gtk.StateType.INSENSITIVE, col)
    wid.modify_bg(Gtk.StateType.INSENSITIVE, col)
    wid.modify_fg(Gtk.StateType.SELECTED, col)
    wid.modify_bg(Gtk.StateType.SELECTED, col)
    #hbox2.pack_start(wid, False)'''
    








