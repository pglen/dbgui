#!/usr/bin/env python3

from __future__ import absolute_import
from __future__ import print_function

import os, sys, getopt, signal, uuid, subprocess
import random, time, socket

import pysql

sys.path.append('../pycommon')
import pypacker

HOST, PORT = "255.255.255.255", 7777

pgdebug = 0

#ppp = packer.encode_data("", [1,2,3])
#print("packed", ppp)
#print("unpacked", packer.decode_data(ppp))

class PeerList():

    def __init__(self, data, timeout = 0.1):

        self.packer = pypacker.packbin()

        # SOCK_DGRAM is the socket type to use for UDP sockets
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.sock.settimeout(timeout)

        # As you can see, there is no connect() call; UDP has no connections.
        # Instead, data is directly sent to the recipient via sendto().

        try:
            self.sock.sendto(bytes(data + "\n", "utf-8"), (HOST, PORT))
            if pgdebug:
                print("Sent:     '{}'".format(data))
        except:
            pass

    # --------------------------------------------------------------------

    def getlist(self, data):
        allcli = []
        while(True):
            try:
                received = str(self.sock.recv(1024), "utf-8")
                if pgdebug:
                    print("Received: '{}'".format(received))
                dec = self.packer.decode_data(received)
                if dec[2] == data:
                    #print("Got dec", dec[1])
                    if dec[1] not in allcli:
                        allcli.append(dec[1])
            except:
                #print("No more replies, socket timeout")
                break
        self.sock.close()
        return allcli

class PeerData():

    def __init__(self, dibadb, timeout = 0.1):
        self.packer = pypacker.packbin()
        # SOCK_DGRAM is the socket type to use for UDP sockets
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.sock.settimeout(timeout)

    def getdata(self, challenge, peer, port):

        enc = self.packer.encode_data("", challenge)
        self.sock.sendto(bytes(enc + "\n", "utf-8"), (peer, port))
        received = str(self.sock.recv(1024), "utf-8")
        if pgdebug:
            print("Received: '{}'".format(received))

        dec = self.packer.decode_data(received)
        if pgdebug:
            print("Dec", dec)
        return dec

# ------------------------------------------------------------------------
# Test client actions:

if __name__ == '__main__':

    if len(sys.argv) == 1:
        #print("Use: dbcli.py str")
        #sys.exit(0)
        data = "dbgui"
    else:
        data = " ".join(sys.argv[1:])

    pl = PeerList(data)
    allcli = pl.getlist(bytes(data.upper(), "cp437"))

    if len(allcli) == 0:
        print("No peers, exiting.")
        sys.exit(0)

    print("Current peer list:", allcli)

    dibadb = pysql.dibasql(pysql.data_dir + "/data.mysql")
    pd = PeerData(dibadb, 1)
    ddd = pd.getdata( ("count",), allcli[0], 7778)

    #pypacker.pgdebug = 1
    fff = pd.getdata( ("first",), allcli[0], 7778)
    lll = pd.getdata( ("last",), allcli[0], 7778)

    if fff[0][0] != "OK":
        print ("Error", fff)
    else:
        print("First:", fff)

    if lll[0][0] != "OK":
        print ("Error", lll)
    else:
        print("Last:", lll)

    ddd = fff[0][2][0][0]
    print("ddd", ddd)
    nnn = pd.getdata( ("next", ddd), allcli[0], 7778)
    if nnn[0][0] != "OK":
        print("Err")
    print("nnn", nnn)

    zzz = lll[0][2][0][0]
    aaa = pd.getdata( ("prev", zzz), allcli[0], 7778)
    if aaa[0][0] != "OK":
        print("Err")
    print("aaa", aaa)
