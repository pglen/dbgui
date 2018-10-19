#!/usr/bin/env python

import sys, os, time, uuid, sqlite3

# Store data for the DIBA bank

# Fields in no particular order

fields = ['lob',  'city', 'cname', 'zip', 'freetext', 'dob', 
        'country', 'numid', 'email2', 'county', 'phone', 'addr2',
        'comments', 'addr1', 'phone2', 'email', 'log', 'custid' ]

# 'lob',  
# 'dob', 
#'city', 
#'cname', 
#'zip', 
#'freetext', 
#'country'
#'numid'
#'email2'
#'county'
#'phone'
#'addr2',
#'addr1'
#'comments'
#'phone2'
#'email'
#'log'
#'custid'
#'entryid'

# added by sql: p
    # 'pri' primary database key 
    # 'entryid' row id by the system

class dibasql():

    def __init__(self, file):
    
        try:
            self.conn = sqlite3.connect(file)
        except:
            print "Cannot open/create db:", file, sys.exc_info() 
            return            
        try:
            self.c = self.conn.cursor()
            
            # Create tables
            sqlstr = "create table if not exists clients \
                (pri INTEGER PRIMARY KEY, entryid string"
            for aa in fields:
                sqlstr += ", " + aa + " text"
            
            sqlstr +=  ")"
            
            #print "sql str: '" + sqlstr + "'"
            
            try:
                self.c.execute(sqlstr)
            except:
                print "Cannot initiate database", sys.exc_info()
            
            '''self.c.execute("create table if not exists pos \
                       (pri INTEGER PRIMARY KEY, head text, xx integer, yy integer, ss integer)")
            self.c.execute("create index if not exists  ipos on pos (head)")            
            self.c.execute("create index if not exists  ppos on pos (pri)")'''
            
            # Save (commit) the changes
            self.c.execute("PRAGMA synchronous=OFF")
            self.conn.commit()            
        except:
            print "Cannot create sql tables", sys.exc_info() 
             
        finally:    
            # We close the cursor, we are done with it
            #c.close()    
            pass
                            
    # --------------------------------------------------------------------        
    # Return False if cannot put data
    
    def   put(self, datax):
    
        #got_clock = time.clock()         
        
        print "datax", datax
        ret = True  
        try:      
            self.c.execute("select * from clients where cname == ?", (datax['cname'], ))
            rr = self.c.fetchall()
            if rr == []:
                entryid = uuid.uuid4()
                print "inserting", entryid
                sqlstr = "insert into clients (entryid, "
                for aa in datax:
                     sqlstr += aa + ", "
                # Erase last one    
                sqlstr = sqlstr[:-2]  
                sqlstr += ") values (?, "   # first value for rowid
                sqlstr += "?, " * len(datax)
                sqlstr = sqlstr[:-2]  
                sqlstr += ")"
                
                arr = []
                arr.append(str(entryid))
                
                for aa in datax:
                     strx = datax[aa]
                     arr.append(strx)
                
                print "sql str", sqlstr, "arr", arr
                self.c.execute(sqlstr, arr)
                
                #self.c.execute("insert into clients (head, body) \
                #    values (?, ?)", (head, val))
                pass
            else:
                #print "updating"
                #self.c.execute("update clients set body = ? where head = ?",\
                #                     (val, head))                                     
                pass
            self.conn.commit()          
        except:
            print "Cannot put sql data", sys.exc_info()             
            ret = False  
        finally:
            #c.close     
            pass

        #self.take += time.clock() - got_clock        
          
        return ret
  
    # --------------------------------------------------------------------        
    # Get table names
    
    def   getnames(self):
    
        ss = "SELECT sql FROM sqlite_master WHERE type='table'"
        try:      
            self.c.execute(ss)
            rr = self.c.fetchall()
        except:
            print "getnames: Cannot get sql data", sys.exc_info() 
        finally:
            pass
        return rr
        
    # --------------------------------------------------------------------        
    # Get names
    
    def   getcustnames(self):
        rr = []; ss = []
        try:      
            self.c.execute("select pri, cname, custid,  comments from clients")
            rr = self.c.fetchall()
        except:
            print "getcustnames: Cannot get sql data", sys.exc_info() 
            raise
        finally:
            pass
        return rr
    
    # --------------------------------------------------------------------        
    # Get All
    
    def   getall(self):
        rr = []; ss = []
        try:      
            self.c.execute("select * from clients")
            rr = self.c.fetchall()
            ss = self.c.description
        except:
            print "getall: Cannot get sql data", sys.exc_info() 
        finally:
            #c.close   
            pass
        return rr, ss
        
    # --------------------------------------------------------------------        
    # Return None if no data deleted
                                         
    def   rmall(self):
        try:      
            self.c.execute("drop table clients")
            #self.c.execute("delete from clients")
            rr = self.c.fetchone()
        except:
            print "rmall: Cannot delete sql data", sys.exc_info() 
        finally:
            #c.close   
            pass
        if rr:            
            return rr
        else:
            return None

    # --------------------------------------------------------------------        
    # Return None if no data deleted

    def   rmone(self, kkk):
        try:      
            self.c.execute("delete from clients where head == ?", (kkk,))
            rr = self.c.fetchone()
        except:
            print "rmone: Cannot delete sql data", sys.exc_info() 
        finally:
            #c.close   
            pass
        if rr:            
            return rr
        else:
            return None




























