#!/usr/bin/env python3

from __future__ import absolute_import
from __future__ import print_function

import sqlite3, datetime, uuid

file = "test.sqlite"

def xjoinlen(rr):
    lenx = 0
    for aa in rr:
        lenx += len(str(aa))
    return lenx

def xjoin(rr):
    strx = ""
    for aa in rr:
        strx += str(aa)
    return strx

def printrec(rec):

    for aa in rec:
        print(aa)
        #if xjoinlen(aa) > 70:
        #    print()


conn = sqlite3.connect(file)
curs = conn.cursor()

sqlstr = "create table if not exists clients (pri INTEGER PRIMARY KEY, entryid text3, xdate text, xdate2 real)"
#print("sqlstr=", sqlstr)
curs.execute(sqlstr)

'''
for aa in range(8):
    dnnn = datetime.datetime.now()
    entryid = uuid.uuid4()
    #print( "inserting", entryid)
    sqlstr = "insert into clients (entryid, xdate, xdate2) values( ?, ?, ?)"
    arr = [str(entryid), datetime.datetime.isoformat(dnnn),  dnnn.timestamp()]
    curs.execute(sqlstr, arr)

conn.commit()
curs.execute("select count(*) from clients")
rr = curs.fetchall()
print(rr)
'''
curs.execute("select xdate, xdate2 from clients limit 100")
rr = curs.fetchall()
printrec(rr)
print("")

dsss = "2020-12-12T18:39:27.770327"
print("dsss", dsss)

dddd = datetime.datetime.fromisoformat(dsss).timestamp()

curs.execute("select xdate, xdate2 from clients where xdate2 > ? order by xdate2", (dddd, ))
rr = curs.fetchall()
printrec(rr)

print("")
curs.execute("select xdate, xdate2 from clients where xdate2 < ? order by xdate2 desc", (dddd, ))
rr = curs.fetchall()
printrec(rr)

