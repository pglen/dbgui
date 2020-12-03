#!/usr/bin/env python3

from __future__ import absolute_import
from __future__ import print_function

import os, sys, getopt, signal, uuid, subprocess
import socketserver, socket
import random, time

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject
from gi.repository import GLib
from gi.repository import Pango

import newcust, pysql, treehand, yellow, custselect

sys.path.append('../pycommon')
import sutil, pgentry, pgbox

sys.path.append('../pyvserv/common')
import pypacker
packer = pypacker.packbin()

class MyUDPHandler(socketserver.BaseRequestHandler):
    """
    This class works similar to the TCP handler class, except that
    self.request consists of a pair of data and client socket, and since
    there is no connection the client address must be given explicitly
    when sending data back via sendto().
    """

    def setup(self):
        #print("in setup")
        pass

    def handle(self):
        global myip

        data = self.request[0].strip()

        socket = self.request[1]
        print("{} wrote: '{}'".format(self.client_address[0], data) )
        #print(data)
        ddd = "{} -> {} -- {}".format(self.client_address[0], myip, data.upper() )
        ppp = packer.encode_data("", [self.client_address[0], myip, data.upper()])

        socket.sendto(bytes(ppp, "cp437"), self.client_address)

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP


# ------------------------------------------------------------------------
# Start of program:

if __name__ == '__main__':

    global myip

    print("Py db net server");

    hname = socket.gethostname()
    print("hostname",  hname)

    #hinf = socket.getaddrinfo(hname, 80) #, proto=socket.IPPROTO_TCP)
    #print("hinf", hinf)
    #print("hinf[] '{}' ".format(hinf[0][4][0]))

    myip = get_ip()

    print("my ip", myip)

    #HOST, PORT = "localhost", 7777
    HOST, PORT = "", 7777
    with socketserver.UDPServer((HOST, PORT), MyUDPHandler) as server:
        server.serve_forever()


    # Fallback
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

    # Enable port reusage so we will be able to run multiple clients and servers on single (host, port).
    # Do not use socket.SO_REUSEADDR except you using linux(kernel<3.9): goto https://stackoverflow.com/questions/14388706/how-do-so-reuseaddr-and-so-reuseport-differ for more information.
    # For linux hosts all sockets that want to share the same address and port combination must belong to processes that share the same effective user ID!
    # So, on linux(kernel>=3.9) you have to run multiple servers and clients under one user to share the same (host, port).
    # Thanks to @stevenreddie
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

    # Enable broadcasting mode
    server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    server.bind(('', 7777))
    while True:
        data,addr = server.recvfrom(1024)
        print("server received message: %s %s"%(data, addr))
        server.sendto(data.upper(), addr)
