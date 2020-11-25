#!/usr/bin/env python3

from __future__ import absolute_import
from __future__ import print_function

import os, sys, getopt, signal, uuid, subprocess

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject
from gi.repository import GLib
from gi.repository import Pango

import random, time
import newcust, pysql, treehand, yellow, custselect

sys.path.append('../pycommon')

import sutil
import pgentry, pgbox

version = 1.0
verbose = False

# Where things are stored (backups, orgs, macros)
#data_dir = os.path.expanduser("~/.dbgui")

# The production code will put it somwhere else
dataroot = os.getcwd()

#print( "datatroot", dataroot)

data_dir        = dataroot + "/data/customers/"
#key_dir         = dataroot + "/data/customers/keys/"
#currency_dir    = dataroot + "/data/currency/"
blockchain_dir  = dataroot + "/data/blockchain/"
audit_dir       = dataroot + "/data/audit/"

def showgtk():
    pprint(Gtk.__dict__)

def pprint(ddd):
    for aa in ddd:
        print( aa, "\t", ddd[aa])

# ------------------------------------------------------------------------

class MainWin():

    def __init__(self):

        self.timerx = 0
        self.serial = ""
        self.window = window = Gtk.Window(type=Gtk.WindowType.TOPLEVEL)
        window.set_title("DBGui Main Screen")
        window.set_position(Gtk.WindowPosition.CENTER)

        #ic = Gtk.Image(); ic.set_from_stock(Gtk.STOCK_DIALOG_INFO, Gtk.IconSize.BUTTON)
        #window.set_hands(ic.get_pixbuf())

        www, hhh = sutil.get_screen_wh()
        window.set_default_size(15*min(www,hhh)/16, 12*min(www,hhh)/16)
        window.set_events(Gdk.EventMask.ALL_EVENTS_MASK )

        window.connect("unmap", self.OnExit)
        window.connect("key-press-event", self.key_press_event)
        window.connect("button-press-event", self.area_button)

        try:
            window.set_hands_from_file("images/hands.png")
        except:
            pass

        GLib.timeout_add(1000, self.handler_tick)

        #yellow.stickWin(window, "hello", "Want")

        notebook = Gtk.Notebook(); self.notebook = notebook
        notebook.popup_enable()
        notebook.set_scrollable(True)

        notebook.add_events(Gdk.EventMask.ALL_EVENTS_MASK)

        notebook.connect("switch-page", self.note_swpage_cb)
        notebook.connect("focus-in-event", self.note_focus_in)


        hbox = self.mainline()
        hbox3 = self.mainline_two()

        lab4 = Gtk.Label(label="");  hbox3.pack_start(lab4, True, 0, 0)
        self.account = Gtk.Label(label="DBGui: No client selected");
        attr = Pango.AttrList()
        #attr.insert(Pango.AttrSize(30000, 0, -1))
        #attr.insert(Pango.AttrForeground(0, 0, 65535, 0, -1))
        #self.account.set_attributes(attr)

        self.activity = Gtk.Label(label="Current activity: Idle ");
        #attr2 = Pango.AttrList()
        #attr2.insert(Pango.AttrSize(20000, 0, -1))
        #self.activity.set_attributes(attr2)


        self.progress("DBGui: Done init")

        # Put the notebook together
        vbox2 = self.mainpage(hbox, hbox3)
        notebook.append_page(vbox2)
        notebook.set_tab_label(vbox2, Gtk.Label(label="  Main  "));

        vbox = self.monpage()
        notebook.append_page(vbox)
        notebook.set_tab_label(vbox, Gtk.Label(label="  Monitor  "));

        vbox3 = Gtk.VBox();
        vbox3.pack_start(Gtk.Label(label=" Cal "), True, True, 0)
        notebook.append_page(vbox3)
        notebook.set_tab_label(vbox3, Gtk.Label(label="  Calendar  "));

        vbox4 = Gtk.VBox()
        vbox4.pack_start(Gtk.Label(label=" Reports "), True, True, 0)
        notebook.append_page(vbox4)
        notebook.set_tab_label(vbox4, Gtk.Label(label="  Reports  "));

        vbox5 = Gtk.VBox()
        vbox5.pack_start(Gtk.Label(label=" Admin "), True, True, 0)
        notebook.append_page(vbox5)
        notebook.set_tab_label(vbox5, Gtk.Label(label="  Admin  "));

        # Assemble page

        vboxm = Gtk.VBox();  hboxm = Gtk.HBox()
        hboxm.pack_start(Gtk.Label(label="  "), False, 0, 0)
        hboxm.pack_start(Gtk.Label(label=" Menu goes here"), False, 0, 0)
        hboxm.pack_start(Gtk.Label(label="  "), True, 0, 0)

        vboxm.pack_start(pgbox.xSpacer(), False, False, 0)
        vboxm.pack_start(hboxm, False, False, 0)
        vboxm.pack_start(pgbox.xSpacer(), False, False, 0)
        vboxm.pack_start(notebook, True, True, 0)

        vboxm.pack_start(self.activity, False, 0, 0)
        vboxm.pack_start(pgbox.xSpacer(), False, False, 0)

        window.add(vboxm)

    def monpage(self):

        vbox = Gtk.VBox();
        hbox2 = Gtk.HBox()
        self.tree = treehand.TreeHand(self.tree_sel_row)
        hbox2.pack_start(self.tree.stree, True, True, 0)

        self.txt1 = Gtk.Label(label="None")
        hbox2.pack_start(self.txt1, True, True, 0)

        vbox.pack_start(hbox2, True, True, 0)

        return vbox


    def mainpage(self, hbox, hbox3):

        vbox2 = Gtk.VBox()
        vbox2.pack_start(Gtk.Label(label=" "), True, True, 0)
        vbox2.pack_start(self.account, False, 0, 0)
        vbox2.pack_start(hbox, False, 0, 0)
        vbox2.pack_start(hbox3, False, 0, 0)

        hbox4b = Gtk.HBox()
        hbox4b.pack_start(Gtk.Label(label="  "), True, 0, 0)
        hbox4b.pack_start(Gtk.Label(label="  "), False, 0, 0)
        hbox4b.pack_start(Gtk.Label(label="  "), True, 0, 0)
        vbox2.pack_start(hbox4b, True, True, 0)

        return vbox2


    def mainline(self):

        hbox = Gtk.HBox();
        lab3 = Gtk.Label(label="");  hbox.pack_start(lab3, True, 0, 0)

        ib2 = pgentry.imgbutt("images/person.png", " Ne_w Client ", self.new_account, self.window)
        hbox.pack_start(ib2, False, 0, 0)

        ib2 = pgentry.imgbutt("images/select.png", " Selec_t Client ", self.sel_account, self.window)
        hbox.pack_start(ib2, False, 0, 0)

        ib2 = pgentry.imgbutt("images/person3.png", " _Edit Client ", self.ed_account, self.window)
        hbox.pack_start(ib2, False, 0, 0)

        ib2 = pgentry.imgbutt("images/search.png", " _Search ", self.search, self.window)
        hbox.pack_start(ib2, False, 0, 0)

        ib2 = pgentry.imgbutt("images/transact.png", " Show T_ransactions ", self.transact, self.window)
        hbox.pack_start(ib2, False, 0, 0)

        lab2e = Gtk.Label(label="");  hbox.pack_start(lab2e, True, 0, 0)

        return hbox


    def mainline_two(self):

        hbox3 = Gtk.HBox()
        lab3 = Gtk.Label(label="");  hbox3.pack_start(lab3, True, 0, 0)

        ib2 = pgentry.imgbutt("images/person2.png", "  _Delete Client  ", self.del_client, self.window)
        hbox3.pack_start(ib2, False, 0, 0)

        ib2 = pgentry.imgbutt("images/hands.png", "  H_ide One  ", self.hide_one, self.window)
        hbox3.pack_start(ib2, False, 0, 0)

        #ib2 = pgentry.imgbutt("images/hands.png", "  _Delete One   ", self.del_one, self.window)
        #hbox3.pack_start(ib2, False, 0, 0)

        ib2 = pgentry.imgbutt("images/hands.png", "  Hide _Main  ", self.hide_main, self.window)
        hbox3.pack_start(ib2, False, 0, 0)

        ib2 = pgentry.imgbutt("images/summary.png", " Show Summ_ary ", self.show_one, self.window)
        hbox3.pack_start(ib2, False, 0, 0)

        ib2 = pgentry.imgbutt("images/hands.png", "   E_xit  ", self.exit_all, self.window)
        hbox3.pack_start(ib2, False, 0, 0)

        return hbox3


    def exit_all(self, area = None, win = None):
        #print( "exit_all")
        self.window.hide()

    def next(self, org):
        print( "next", org.head)

    def transact(self, area, me):
        pass

    def get_one(self, area, me):
        pass

    def show_one(self, area, me):
        pass

    def  note_focus_in(self, win, act):
        pass

    def  note_swpage_cb(self, tabx, page, num):
        pass

    def del_one(self, area, me):
        pass

    def above_one(self, area, me):
        pass

    def hide_one(self, area, me):
        pass

    def done_dlg(self, dlg):
        global window2, dibadb
        head = dlg.head.get_text()
        buff = dlg.text.get_buffer()
        ss = buff.get_start_iter(); ee = buff.get_end_iter()
        text = buff.get_text(ss, ee)
        #print(  "done_dlg", head, text)
        dibadb.put(head, text)
        dibadb.putshow(head, 1)

        self.window.present()

    def sel_account(self, area, me):
        #print( "sel_account")
        selx = custselect.ListCust(self, dibadb)
        selx.run()
        if selx.results:
            print( selx.results)
            self.account.set_text("Current Client: " + selx.results[1])
            self.serial = selx.results[2]
        #print( "done list")

    def progress(self, text):
        self.activity.set_text(text)
        sutil.usleep(20);
        self.timerx = 5;

    def getkeyid(self, fname):
        return ""

    def unlink_noerr(self, fname):
        try:
            os.unlink(fname)
        except:
            pass

    # Evaluate callback, return string with error. Empty string for OK.
    def callback(self, form):
        global dibadb
        self.arr2 = {}
        for aa in form.arr:
            if type(aa[1])  == Gtk.Entry:
                #print( "entry", aa[0],  aa[1].get_text())
                self.arr2[aa[0]] = aa[1].get_text()
            elif type(aa[1])  == Gtk.TextView:
                buff = aa[1].get_buffer()
                txtx = buff.get_text(buff.get_start_iter(), buff.get_end_iter(), False)
                #print( "textview", aa[0], txtx)
                self.arr2[aa[0]] = txtx
            else:
               self.arr2[aa[0]] = aa[1]

        if self.arr2['cname'] == "":
            return "Name cannot be empty."

        isaddr =  self.arr2['addr1'] != "" and  self.arr2['city'] != ""
                     #and \
                     #self.arr2['county'] != "" and self.arr2['country'] != ""

        if self.arr2['phone'] == "" and self.arr2['email'] == "" and \
                                not isaddr:
            return "Must have phone or address or email."

        dibadb.put(self.arr2)

        return ""

    def ed_account(self, area, me):
        #print( "ed_account" )
        if self.serial == "":
            sutil.message("\nPlease select a client first.\n", self.window)
            return
        datax  = dibadb.get(self.serial)
        #print( "ed datax", datax)
        custform = newcust.NewCust(self, self.serial, datax)
        custform.run()

    def new_account(self, area, me):
        #print( "new_account" )
        serial = uuid.uuid4()
        custform = newcust.NewCust(self, serial)
        custform.run()
        if custform.ok == False:
            self.progress("Cancelled account generation. ")
            return
        ret = ""; retcode = 0

    def search(self, area, me):
        #print( "search")
        pass

    def del_client(self, area, me):
        #print( "del_client")
        if self.serial == "":
            sutil.message("\nPlease select a client first.\n", self.window)
            return

        datax  = dibadb.get(self.serial)

        #sutil.message("delete " + self.serial + "?", self.window)
        ret = sutil.yes_no_cancel("Are you sure?",
                "Are you sure you want to delete client '" + datax['cname'] + "' ?",
                        False, self.window)

        #print( "ret", ret)
        if ret == Gtk.ResponseType.YES:
            self.progress("Deleting ...")
            dibadb.rm(self.serial)
            self.progress("Deleted.")
        else:
            self.progress("Delete cancelled")

        return False

    def hide_main(self, area, me):
        #print( "hide_main")
        me.iconify()

    def area_button(self, area, event):
        #print( "main butt")
        return False

    def tree_sel_row(self, xtree):
        #print( tree)
        return False

    def key_press_event(self, area, event):
        #print( "main keypress" #, area, event)
        return False

    def OnExit(self, aa):
        #print( "OnExit")
        # Save data
        Gtk.main_quit()
        return False

    def handler_tick(self):
        if self.timerx > 0:
            self.timerx -= 1
        if self.timerx == 1:
            self.activity.set_text("DBGui Idle")
        GLib.timeout_add(1000, self.handler_tick)

def key_press_event(win, aa):
    print( "key_press_event", win, aa)

def help():

    print( )
    print( "dibagui version: ", version)
    print( )
    print( "Usage: " + os.path.basename(sys.argv[0]) + " [options] [[filename] ... [filenameN]]")
    print( )
    print( "Options:")
    print( "            -d level  - Debug level 1-10. (Limited implementation)")
    print( "            -v        - Verbose (to stdout and log)")
    print( "            -c        - Dump config")
    print( "            -s        - Show database")
    #print( "            -x        - Extras like test time routine")
    print( "            -r        - Remove database (test oly)")
    print( "            -h        - Help")
    print( "            -?        - Help")
    print()

def softmkdir(dirx):
    try:
        if not os.path.isdir(dirx):
            os.makedirs(dirx)
    except:
        print( "Cannot make directory:",  dirx)
        raise

def test_time():
    ttt = time.time()
    sss = sutil.time_n2s(ttt)
    ttt2 = sutil.time_s2n(sss)
    sss2 = sutil.time_n2s(ttt2)

    print( ttt, ttt2)
    print( sss)
    print( sss2)

# ------------------------------------------------------------------------
# Start of program:

if __name__ == '__main__':

    global dibadb, pg_debug

    verbose = False
    show_config = False; show_timing = False;
    show_database = False; remove_database = False
    pg_debug = 0

    sys.stdout = sutil.Unbuffered(sys.stdout)
    sys.stderr = sutil.Unbuffered(sys.stderr)

    #  Preconditions
    try:
        softmkdir(data_dir)
        #softmkdir(key_dir)
        #softmkdir(currency_dir)
        softmkdir(blockchain_dir)
        softmkdir(audit_dir)
    except:
        print( "Cannot make dir", sys.exc_info())
        sys.exit(2)

    # Let the user know it needs fixin'
    if not os.path.isdir(data_dir):
        print( "Cannot access data dir:", data_dir)
        sys.exit(3)
    if not os.access(data_dir, os.W_OK):
        print( "Cannot write to data dir:", data_dir)
        sys.exit(4)

    dibadb = pysql.dibasql(data_dir + "/data.mysql")

    opts = []; args = []
    try:
        opts, args = getopt.getopt(sys.argv[1:], "d:avchsr?x")
    except getopt.GetoptError as err:
        print( "Invalid option(s) on command line:", err)
        sys.exit(1)

    #print( "opts", opts, "args", args)

    for aa in opts:
        if aa[0] == "-d":
            try:
                pg_debug = int(aa[1])
                if pg_debug > 10: pg_debug = 10
                if pg_debug < 0: pg_debug = 0
                if verbose:
                    print( "Debug level ", pg_debug)
            except:
                print( "Bad argument on option -d:", sys.exc_info() )
                sys.exit(2)

        if aa[0] == "-?": help();  exit(1)
        if aa[0] == "-h": help();  exit(1)
        if aa[0] == "-v": verbose = True
        if aa[0] == "-g": showgtk(); exit(1);
        if aa[0] == "-c": show_config = True
        if aa[0] == "-t": show_timing = True
        if aa[0] == "-x": test_time(); exit(1);
        if aa[0] == "-s": show_database = True
        if aa[0] == "-r": remove_database = True

    if verbose:
        print( "dibagui running on", "'" + os.name + "'", \
            "GTK", Gtk.gtk_version, "PyGtk", Gtk.pygtk_version)

    if show_database:
        db, dd = dibadb.getall()
        print( "Showing database info:")

        if not len(db):
            print( "No data")
            exit(0)

        for aa in range(len(db)):
            for bb in range(len(dd)):
                print( dd[bb][0], "= '" + str(db[aa][bb]) + "',\t", )
            print(); print()
        print( "End database info.")
        sys.exit(0)

    # For testing
    if remove_database:
        print( "This is for testing / development. Are you sure? (yes/no)")
        aa = sys.stdin.readline()
        if aa[:3] == "yes":
            print( "Removing data ... ",)
            rr = dibadb.rmall()
            print( rr)
        else:
            print( "Not removed, Type the word 'yes' for data removal.")
        sys.exit(0)

    #if(show_config):
    #    print( dibadb.getall())

    mainwin = MainWin()
    mainwin.window.show_all()
    Gtk.main()

# EOF

