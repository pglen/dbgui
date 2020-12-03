#!/usr/bin/env python3

from __future__ import absolute_import
from __future__ import print_function

import os, sys, getopt, signal, uuid, subprocess
import random, time, socket

sys.path.append('../pyvserv/common')
import pypacker

#HOST, PORT = "localhost", 7777
HOST, PORT = "255.255.255.255", 7777
#HOST, PORT = "<broadcast>", 7777

if len(sys.argv) == 1:
    print("Use: dbcli.py str")
    sys.exit(0)

data = " ".join(sys.argv[1:])
packer = pypacker.packbin()

#ppp = packer.encode_data("", [1,2,3])
#print("packed", ppp)
#print("unpacked", packer.decode_data(ppp))

# SOCK_DGRAM is the socket type to use for UDP sockets
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

# As you can see, there is no connect() call; UDP has no connections.
# Instead, data is directly sent to the recipient via sendto().

sock.sendto(bytes(data + "\n", "utf-8"), (HOST, PORT))
received = str(sock.recv(1024), "utf-8")

print("Sent:     '{}'".format(data))
print("Received: '{}'".format(received))

print("Dec",   packer.decode_data(received))
