#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import print_function

# Tree View/List Store

import os, sys, getopt, signal, uuid, subprocess

import newcust, pysql, sutil, treehand, yellow
import custselect

'''The GtkListStore is used to store data in list form, to be used
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
    COLUMN_DESCRIPTION,
    COLUMN_DATE
) = range(5)

verbose = 0

# -------------------------------------------------------------------
class ListCust(Gtk.Window):

    def __init__(self, self2, dibadb):

        # Create window, etc
        self.self2 = self2
        self.dibadb = dibadb
        GObject.GObject.__init__(self)

        self.set_title("Client List")

        self.set_transient_for(self2.window)
        self.set_modal(True)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.ok = False
        self.results = ()

        www, hhh = sutil.get_screen_wh()
        self.set_size_request(3*www/4, 3*hhh/4)

        vbox = Gtk.VBox(False, 0)
        self.add(vbox)

        self.connect("key-press-event", self.key_press_event)

        hbox = Gtk.HBox(False, 2)
        vbox.pack_start(hbox, False, 0, 8)
        hbox.pack_start(Gtk.Label("    "), True, True, 0)

        for aa in range(ord("N") - ord("A") + 1):
            sss =  str(chr(ord("A") + aa ))
            bbb = Gtk.Button(sss)
            bbb.connect("clicked", self.butt_handler)
            hbox.pack_start(bbb, False, 0, 0)
        hbox.pack_start(Gtk.Label("    "), True, True, 0)

        hbox2 = Gtk.HBox(False, 2)
        vbox.pack_start(hbox2, False, 0, 2)
        hbox2.pack_start(Gtk.Label("    "), True, True, 0)

        for aa in range(ord("Z") - ord("O") + 1):
            sss =  str(chr(ord("O") + aa ) )
            bbb = Gtk.Button(sss)
            bbb.connect("clicked", self.butt_handler)
            hbox2.pack_start(bbb, False, 0, 0)

        hbox2.pack_start(Gtk.Label("    "), True, True, 0)

        tp1 =("Search: ", "cname", "Enter search string (TAB to advance)", None)

        self.src_box = self.srcentry(vbox, tp1)

        sw = Gtk.ScrolledWindow()
        sw.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
        sw.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        vbox.pack_start(sw, True, True, 0)

        self.create_model()
        # create tree view
        self.treeview = Gtk.TreeView(self.lstore)
        self.treeview.set_rules_hint(True)
        self.treeview.set_search_column(COLUMN_DESCRIPTION)
        self.add_columns(self.treeview)
        sw.add(self.treeview)

        self.treeview.connect("row-activated",  self.tree_sel)
        self.treeview.connect("cursor-changed",  self.tree_sel_row)

        self.show_all()
        self.src_box.grab_focus()

        sutil.usleep(10)
        GObject.timeout_add(100, self.handler_tick)

    def butt_handler(self, but):
        ttt = but.get_label()
        res = [];  self.lstore.clear()
        try:
            res = self.dibadb.getcustnames(ttt + '%')
            '''print( "Listing search res:")
            for aa in res:
                print( aa)
            print( "Done,")
            '''

        except:
            self.self2.progress("Cannot fetch search results.")
            print( "Cannot fetch name list.", sys.exc_info())
            pass

        if res == []:
            sutil.message("\nNo matcing record for '%s'.\n\n" % ttt, self)
            return

        self.fill_data(res)


    def tree_sel(self, xtree, xiter, xpath):
        #print("tree_sel", xtree, xiter, xpath)
        sel = xtree.get_selection()
        xmodel, xiter = sel.get_selected()
        if xiter:
            xstr = xmodel.get_value(xiter, 0)
            xstr2 = xmodel.get_value(xiter, 1)
            xstr3 = xmodel.get_value(xiter, 2)
            self.results = (xstr, xstr2, xstr3)
            self.destroy()

    def tree_sel_row(self, xtree):
        pass
        #print( "Selected", xstr, xstr2)
        '''sel = xtree.get_selection()
        xmodel, xiter = sel.get_selected()
        if xiter:
            xstr = xmodel.get_value(xiter, 0)
            xstr2 = xmodel.get_value(xiter, 1)'''

    # Add columns to the tree view
    def handler_tick(self):

        self.self2.progress("Reading client data")

        res = []; cnt = 0
        try:
            res = self.dibadb.getcustnames()

            if verbose:
                print( "Listing database:")
                for aa in res:
                    print( aa)
                print( "Done,")

        except:
            self.self2.progress("Cannot fetch name list.")
            print( "Cannot fetch name list.", sys.exc_info())
            pass

        self.fill_data(res)

    def create_model(self):
        self.lstore = Gtk.ListStore(
            GObject.TYPE_STRING,
            GObject.TYPE_STRING,
            GObject.TYPE_STRING,
            GObject.TYPE_STRING,
            GObject.TYPE_STRING)

    def limstr(self, strx):
        if len(strx) > 44:
            stry = strx[0:44]
        else:
            stry = strx
        return stry

    def fill_data(self, res):
        for item in res:
            iter = self.lstore.append()
            self.lstore.set(iter,
                COLUMN_FIXED, str(item[COLUMN_FIXED]),
                COLUMN_NUMBER, self.limstr(item[COLUMN_NUMBER]),
                COLUMN_SEVERITY, item[COLUMN_SEVERITY],
                COLUMN_DESCRIPTION, item[COLUMN_DESCRIPTION],
                COLUMN_DATE, item[COLUMN_DATE])

    def fixed_toggled(self, cell, path, model):
        # get toggled iter
        iter = model.get_iter((int(path),))
        fixed = model.get_value(iter, COLUMN_FIXED)
        # do something with the value
        fixed = not fixed

        # set new value
        model.set(iter, COLUMN_FIXED, fixed)

    def add_columns(self, treeview):
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
        #column.set_sort_column_id(COLUMN_NUMBER)
        treeview.append_column(column)

        # columns for severities
        column = Gtk.TreeViewColumn('Customer ID', Gtk.CellRendererText(),
                                    text=COLUMN_SEVERITY)
        #column.set_sort_column_id(COLUMN_SEVERITY)
        treeview.append_column(column)

        # column for description
        column = Gtk.TreeViewColumn('Description', Gtk.CellRendererText(),
                                     text=COLUMN_DESCRIPTION)
        #column.set_sort_column_id(COLUMN_DESCRIPTION)
        treeview.append_column(column)

        # column for date
        column = Gtk.TreeViewColumn('Update Date', Gtk.CellRendererText(),
                                     text=COLUMN_DATE)
        column.set_sort_column_id(COLUMN_DATE)
        treeview.append_column(column)

    def key_press_event(self, win, event):
        if event.keyval == Gdk.KEY_Escape:
            self.destroy()
        #print( "keystate", event.get_state())
        if event.keyval == Gdk.KEY_x and event.get_state() & Gdk.ModifierType.MOD1_MASK:
            self.destroy()

    # Run as modal dialog until destroyed
    def run(self):
        self.show_all()
        sutil.mainloop()
        return self.ok

    def srcentry(self, vbox, entry1):

        hbox2 = Gtk.HBox(False, 4)

        lab1a = Gtk.Label(label="      ")
        hbox2.pack_start(lab1a, True, 0, 0)
        lab1 = Gtk.Label(label=entry1[0]) #; lab1.set_alignment(1, 2)
        lab1.set_tooltip_text(entry1[2])
        hbox2.pack_start(lab1, False, 0, 0)
        lab1a = Gtk.Label(label="      ")
        hbox2.pack_start(lab1a, False, 0, 0)
        headx = Gtk.Entry();  headx.set_width_chars(33)
        if entry1[3] != None:
            headx.set_text(entry1[3][entry1[1]])
        hbox2.pack_start(headx, False, 0, 0)

        bbb = Gtk.Button.new_with_mnemonic("_Search")
        bbb.connect("clicked", self.click_src)
        hbox2.pack_start(bbb, False, 0, 0)

        bbb = Gtk.Button.new_with_mnemonic("_Clear Search")
        bbb.connect("clicked", self.click_clear)
        hbox2.pack_start(bbb, False, 0, 0)

        lab3 = Gtk.Label(label="        ")
        hbox2.pack_start(lab3, True, 0, 0)
        #self.arr.append((entry1[1], headx))

        vbox.pack_start(hbox2, False, 0, 4)

        return headx

    def click_src(self, butt):
        ttt = self.src_box.get_text()
        #print( "searching ", ttt)
        if ttt == "":
            sutil.message("\nPlease specify search string.\n\n", self)
            return

        res = [];  self.lstore.clear()
        try:
            res = self.dibadb.getcustnames("%" + ttt + "%")
            '''print( "Listing search res:")
            for aa in res:
                print( aa)
            print( "Done,")
            '''

        except:
            self.self2.progress("Cannot fetch search results.")
            print( "Cannot fetch name list.", sys.exc_info())
            pass

        if res == []:
            sutil.message("\nNo matcing name for '%s'.\n\n" % ttt, self)
            return

        self.fill_data(res)

    def click_clear(self, butt):
        self.src_box.set_text("")

        res = [];  self.lstore.clear()
        try:
            res = self.dibadb.getcustnames()
            print( "Listing search res:")
            for aa in res:
                print( aa)
            print( "Done,")

        except:
            self.self2.progress("Cannot fetch search results.")
            print( "Cannot fetch name list.", sys.exc_info())
            pass

        self.fill_data(res)

# testing ...

def main():
    ListCust()
    Gtk.main()

if __name__ == '__main__':
    main()



