#!/usr/bin/env python

import os, sys, getopt, signal
#import gobject, gtk, pango

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject
from gi.repository import GLib


#if Gtk.pygtk_version < (2, 8):
#    print "PyGtk 2.8 or later required for this example"
#    raise SystemExit

try:
    import cairo
except ImportError:
    raise SystemExit("cairo required for this example")

TEXT = 'A GtkWidget implemented in PyGTK'
BORDER_WIDTH = 10

class Padding(Gtk.Widget):

    def __init__(self, text = None):
        GObject.GObject.__init__(self)
        if text == None:
            text = "Hello"
        self._layout = self.create_pango_layout(text)
        self._layout.set_font_description(Pango.FontDescription("Sans Serif 16"))

    # GtkWidget

    def do_realize(self):
        # The do_realize method is responsible for creating GDK (windowing system)
        # resources. In this example we will create a new Gdk.Window which we
        # then draw on

        # First set an internal flag telling that we're realized
        self.set_flags(Gtk.REALIZED)

        # Create a new Gdk.Window which we can draw on.
        # Also say that we want to receive exposure events by setting
        # the event_mask
        self.window = Gdk.Window(
            self.get_parent_window(),
            width=self.allocation.width,
            height=self.allocation.height,
            window_type=Gdk.WINDOW_CHILD,
            wclass=Gdk.INPUT_OUTPUT,
            event_mask=self.get_events() | Gdk.EventMask.EXPOSURE_MASK)

        # Associate the Gdk.Window with ourselves, Gtk+ needs a reference
        # between the widget and the gdk window
        self.window.set_user_data(self)

        # Attach the style to the Gdk.Window, a style contains colors and
        # GC contextes used for drawing
        self.style.attach(self.window)

        # The default color of the background should be what
        # the style (theme engine) tells us.
        self.style.set_background(self.window, Gtk.StateType.NORMAL)
        self.window.move_resize(*self.allocation)

    def do_unrealize(self):
        # The do_unrealized method is responsible for freeing the GDK resources

        # De-associate the window we created in do_realize with ourselves
        self.window.set_user_data(None)

    def do_size_request(self, requisition):
        # The do_size_request method Gtk+ is calling on a widget to ask
        # it the widget how large it wishes to be. It's not guaranteed
        # that gtk+ will actually give this size to the widget

        # In this case, we say that we want to be as big as the
        # text is, plus a little border around it.
        width, height = self._layout.get_size()
        requisition.width = width  #// Pango.SCALE + BORDER_WIDTH*4
        requisition.height = height # // Pango.SCALE + BORDER_WIDTH*4

    def do_size_allocate(self, allocation):
        # The do_size_allocate is called by when the actual size is known
        # and the widget is told how much space could actually be allocated

        # Save the allocated space
        self.allocation = allocation

        # If we're realized, move and resize the window to the
        # requested coordinates/positions
        if self.get_realized():
            self.window.move_resize(*allocation)

    def do_expose_event(self, event):
        # The do_expose_event is called when the widget is asked to draw itself
        # Remember that this will be called a lot of times, so it's usually
        # a good idea to write this code as optimized as it can be, don't
        # Create any resources in here.

        # In this example, draw a rectangle in the foreground color
        x, y, w, h = self.allocation
        cr = self.window.cairo_create()
        cr.set_source_color(self.style.fg[self.state])
        cr.rectangle(BORDER_WIDTH, BORDER_WIDTH,
                     w - 2*BORDER_WIDTH, h - 2*BORDER_WIDTH)
        cr.set_line_width(1.0)
        #cr.set_line_join(cairo.LINE_JOIN_ROUND)
        #cr.stroke()

        #print cr
        # And draw the text in the middle of the allocated space
        fontw, fonth = self._layout.get_pixel_size()
        cr.move_to((w - fontw)/2, (h - fonth)/2)
        #cr.update_layout(self._layout)
        #cr.show_layout(self._layout)

GObject.type_register(Padding)



