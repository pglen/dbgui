#!/usr/bin/env python3

from __future__ import absolute_import
from __future__ import print_function

import os, sys, getopt, signal, uuid, subprocess
import socketserver, socket, random, time, threading

import pysql

sys.path.append('../pycommon')
import pypacker

packer = pypacker.packbin()

myip = ""

pgdebug = 0

def get_myip():

    global myip
    # Only ask once
    if not myip:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # doesn't even have to be reachable
            s.connect(('10.255.255.255', 1))
            myip = s.getsockname()[0]
            #print("Resolved myip", myip)
        except Exception:
            myip = '127.0.0.1'
        finally:
            s.close()
    return myip


class BroadUDPHandler(socketserver.BaseRequestHandler):

    def __init__(self, *arg):
        if pgdebug:
            print("in BroadUDPHandler __init__")
        socketserver.BaseRequestHandler.__init__(self, *arg)
        pass

    def setup(self):
        #print("in BroadUDPHandler setup")
        pass

    def handle(self):
        data = self.request[0].strip()
        socket = self.request[1]
        if pgdebug > 1:
            print("{} wrote: '{}'".format(self.client_address[0], data) )
            #print(data)
        print("BroadUDPHandler Got", data);
        ddd = "{} -> {} -- {}".format(self.client_address[0], get_myip(), data.upper() )
        #pypacker.pgdebug = 2
        ppp = packer.encode_data("", self.client_address[0], get_myip(), data.upper())
        socket.sendto(bytes(ppp, "cp437"), self.client_address)

# Deliver response from the data base

class RespUDPHandler(socketserver.BaseRequestHandler):

    def __init__(self, *arg):
        if pgdebug:
            print("in RespUDPHandler __init__")
        socketserver.BaseRequestHandler.__init__(self, *arg)
        pass

    def setup(self):
        if pgdebug:
            print("in RespUDPHandler setup")
        pass

    def getdbname(self):
        dbfile = pysql.data_dir + "/data.mysql"
        if not os.path.isfile(dbfile):
            raise ValueError("No db file", dbfile)
        return dbfile

    def handle(self):

        data = self.request[0].strip()
        socket = self.request[1]

        #print("DB here", dibadb)
        print("RespUDPHandler Got", data);

        if data == b"hello":
            reply = "OK", "Hello acknowledged."
        elif data == b"count":
            dibadb = pysql.dibasql(self.getdbname())
            reply = "OK", "Count reply", str(dibadb.getcount())
            del dibadb
        elif data == b"last":
            dibadb = pysql.dibasql(self.getdbname())
            reply = "OK", "Last reply", str(dibadb.getlast())
            del dibadb
        else:
            reply = "Hell No"

        ppp = packer.encode_data("", reply)
        socket.sendto(bytes(ppp, "cp437"), self.client_address)

class  bcastserv(threading.Thread):

    # Added port argument here
    def __init__(self, *arg, **narg):
        self.portx = narg['port']
        del narg['port']
        if pgdebug:
            print("in bcastserv __init__", self.portx)

        threading.Thread.__init__(self, *arg, **narg)
        pass

    def run(self):
        if pgdebug:
            print("Started bcastserv", self.portx)
        HOST, PORT = "", self.portx

        # Downgraded to no non context server
        #with socketserver.UDPServer((HOST, PORT), BroadUDPHandler) as server:
        #    server.serve_forever()

        ss = socketserver.UDPServer((HOST, PORT), BroadUDPHandler)
        ss.serve_forever()


class  respserv(threading.Thread):

    # Added port / db argument here
    def __init__(self, *arg, **narg):
        self.portx = narg['port'];  del narg['port']

        if pgdebug:
            print("in respserv __init__", self.portx)
        threading.Thread.__init__(self, *arg, **narg)
        pass

    def run(self):
        if pgdebug:
            print("Started respserv", self.portx)
        HOST, PORT = "", self.portx

        # Downgraded to no non context server
        #with socketserver.UDPServer((HOST, PORT), RespUDPHandler) as server:
        #    server.serve_forever()

        ss = socketserver.UDPServer((HOST, PORT), RespUDPHandler)
        ss.serve_forever()


class  netpeer():

    def __init__(self, ):

        self.th = bcastserv(daemon=True, port=7777);
        self.th.start()

        self.th2 = respserv(daemon=True, port=7778);
        self.th2.start()

    # Wait for the thread (for testing)
    def block(self):
        self.th.join()

# ------------------------------------------------------------------------
# Start of program:

if __name__ == '__main__':

    #print("Py db net server");

    hname = socket.gethostname()
    print("Server started; hostname: '{}'".format(hname) )

    np = netpeer()
    np.block()

    # This was the old code ... just in case it is needed

    #hinf = socket.getaddrinfo(hname, 80) #, proto=socket.IPPROTO_TCP)
    #print("hinf", hinf)
    #print("hinf[] '{}' ".format(hinf[0][4][0]))
    #HOST, PORT = "localhost", 7777
    #HOST, PORT = "", 7778
    #with socketserver.UDPServer((HOST, PORT), MyUDPHandler) as server:
    #    server.serve_forever()
    #print("Threads", threading.enumerate())
    # Fallback
    #server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    # Enable port reusage so we will be able to run multiple clients and servers on single (host, port).
    # Do not use socket.SO_REUSEADDR except you using linux(kernel<3.9): goto https://stackoverflow.com/questions/14388706/how-do-so-reuseaddr-and-so-reuseport-differ for more information.
    # For linux hosts all sockets that want to share the same address and port combination must belong to processes that share the same effective user ID!
    # So, on linux(kernel>=3.9) you have to run multiple servers and clients under one user to share the same (host, port).
    # Thanks to @stevenreddie
    #server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    # Enable broadcasting mode
    #server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    #server.bind(('', 7777))
    #while True:
    #    data,addr = server.recvfrom(1024)
    #    print("server received message: %s %s"%(data, addr))
    #    server.sendto(data.upper(), addr)
    #

