#!/usr/bin/env python

'''Tree View/List Store

import os, sys, getopt, signal, uuid, subprocess
#import gobject, gtk, pango, 

import random, time
import newcust, pysql, sutil, treehand, yellow
import custselect

import os, sys, getopt, signal
import sutil

The GtkListStore is used to store data in list form, to be used
later on by a GtkTreeView to display it. This demo builds a
simple GtkListStore and displays it. See the Stock Browser
demo for a more advanced example.'''

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject
from gi.repository import GLib

(
    COLUMN_FIXED,
    COLUMN_NUMBER,
    COLUMN_SEVERITY,
    COLUMN_DESCRIPTION
) = range(4)

'''data = \
((False, 60482, 'Normal', 'scrollable notebooks and hidden tabs'),
 (False, 60620, 'Critical',
  'gdk_window_clear_area(gdkwindow-win32.c) is not thread-safe'),
 (False, 50214, 'Major', 'Xft support does not clean up correctly'),
 (True,  52877, 'Major', 'GtkFileSelection needs a refresh method. '),
 (False, 56070, 'Normal', "Can't click button after setting in sensitive"),
 (True,  56355, 'Normal', 'GtkLabel - Not all changes propagate correctly'),
 (False, 50055, 'Normal', 'Rework width/height computations for TreeView'),
 (False, 58278, 'Normal', "gtk_dialog_set_response_sensitive() doesn't work"),
 (False, 55767, 'Normal', 'Getters for all setters'),
 (False, 56925, 'Normal', 'Gtkcalender size'),
 (False, 56221, 'Normal', 'Selectable label needs right-click copy menu'),
 (True,  50939, 'Normal', 'Add shift clicking to GtkTextView'),
 (False, 6112,  'Enhancement', 'netscape-like collapsable toolbars'),
 (False, 1,     'Normal', 'First bug :=)'))'''

class ListCust(Gtk.Window):

    def __init__(self, parent, data):
    
        # Create window, etc
        self.data = data
        GObject.GObject.__init__(self)
        try:
            self.set_screen(parent.get_screen())
        except AttributeError:
            self.connect('destroy', lambda *w: Gtk.main_quit())
        
        self.set_title("Diba Customer List")
        
        self.set_transient_for(parent)
        self.set_modal(True)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.ok = False
        
        #self.set_border_width(8)
        #www, hhh = sutil.get_screen_wh()
        www, hhh = 1024, 768
        
        
        self.set_default_size(2*www/4, 2*hhh/4)
        #self.set_default_size(400, 300)

        vbox = Gtk.VBox(False, 8)
        #vbox = self.get_content_area()
        #print vbox
        #self.add_content_widget(vbox, 1)
        self.add(vbox)

        label = Gtk.Label(label='Select DIBA Customer')
        vbox.pack_start(label, False, False, 0)

        self.connect("key-press-event", self.key_press_event)        
        
        hbox = Gtk.HBox()
        vbox.pack_start(hbox, False, 0, 0)
        hbox.pack_start(Gtk.Label("    "), True, True, 0)
        
        for aa in range(ord("Z") - ord("A") + 1):
            sss =  str(chr(ord("A") + aa) )
            hbox.pack_start(Gtk.Button(sss), True, 0, 0)
        hbox.pack_start(Gtk.Label("    "), True, True, 0)
        
        sw = Gtk.ScrolledWindow()
        sw.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
        sw.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        vbox.pack_start(sw, True, True, 0)

        # create tree model
        model = self.__create_model()

        # create tree view
        treeview = Gtk.TreeView(model)
        treeview.set_rules_hint(True)
        treeview.set_search_column(COLUMN_DESCRIPTION)

        sw.add(treeview)

        # add columns to the tree view
        self.__add_columns(treeview)
        self.show_all()
        
    def __create_model(self):
        lstore = Gtk.ListStore(
            #GObject.TYPE_BOOLEAN,
            #GObject.TYPE_UINT,
            GObject.TYPE_STRING,
            GObject.TYPE_STRING,
            GObject.TYPE_STRING,
            GObject.TYPE_STRING)

        for item in self.data:
            iter = lstore.append()
            lstore.set(iter,
                COLUMN_FIXED, str(item[COLUMN_FIXED]),
                COLUMN_NUMBER, item[COLUMN_NUMBER],
                COLUMN_SEVERITY, item[COLUMN_SEVERITY],
                COLUMN_DESCRIPTION, item[COLUMN_DESCRIPTION])
        return lstore

    def fixed_toggled(self, cell, path, model):
        # get toggled iter
        iter = model.get_iter((int(path),))
        fixed = model.get_value(iter, COLUMN_FIXED)

        # do something with the value
        fixed = not fixed

        # set new value
        model.set(iter, COLUMN_FIXED, fixed)

    def __add_columns(self, treeview):
        model = treeview.get_model()

        # column for fixed toggles
        #renderer = Gtk.CellRendererToggle()
        #renderer.connect('toggled', self.fixed_toggled, model)
        #column = Gtk.TreeViewColumn('Primary', renderer, active=COLUMN_FIXED)
        column = Gtk.TreeViewColumn('Primary', Gtk.CellRendererText(), text=COLUMN_FIXED)

        # set this column to a fixed sizing(of 50 pixels)
        #column.set_sizing(Gtk.TreeViewColumnSizing.FIXED)
        #column.set_fixed_width(50)

        treeview.append_column(column)

        # column for bug numbers
        column = Gtk.TreeViewColumn('Customer Name', Gtk.CellRendererText(),
                                    text=COLUMN_NUMBER)
        column.set_sort_column_id(COLUMN_NUMBER)
        treeview.append_column(column)

        # columns for severities
        column = Gtk.TreeViewColumn('Customer ID', Gtk.CellRendererText(),
                                    text=COLUMN_SEVERITY)
        column.set_sort_column_id(COLUMN_SEVERITY)
        treeview.append_column(column)

        # column for description
        column = Gtk.TreeViewColumn('Description', Gtk.CellRendererText(),
                                     text=COLUMN_DESCRIPTION)
        column.set_sort_column_id(COLUMN_DESCRIPTION)
        treeview.append_column(column)

    def key_press_event(self, win, event):
        if event.keyval == Gdk.KEY_Escape:
            self.destroy()
        #print "keystate", event.get_state()
        if event.keyval == Gdk.KEY_x and event.get_state() & Gdk.ModifierType.MOD1_MASK:
            self.destroy()
    
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
        self.destroy()
        return self.ok
    
def main():
    ListCust()
    Gtk.main()

if __name__ == '__main__':
    main()






