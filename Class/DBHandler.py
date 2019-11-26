import os
import sys
import subprocess
#import AutomationSetup
from subprocess import Popen, PIPE
import time
import logging


class runCommandtoSQL():
    
    #===========================================================================
    # # To run this class:
    # # 1. import PrintResults
    # # 2. run: PrintResults.runCommandtoSQL(sql,DB_Path).runsql(sql,DB_Path,timer)
    # # 3. sql = the full query you want to send 
    # # 4. DB_Path = the full DB login like username/password@DB_INST
    # # 5. timer, how much seconds to wait between each retry - wait for record. retrying up to 4 times.
    # # 6. type = which type is the sql query. option: get, update
    # @author: idan Shabat
    #===========================================================================
    
    
    global count
    count = 0

    def __init__(self, sql, DB_Path):
        # This Class get DB info from the env. need to run on ABP server.
        #print("running print")
        self.sql = sql
        self.DB_Path = DB_Path
        logging.basicConfig(filename='serverHandling.log', filemode='w', level=logging.DEBUG)
        logging.debug('Starting class DB Handler')
        
    def waitForRecord(self,timer,type):
        #this function waiting 4 times until record is presented. if no record fount after 4 times it return no result found
        #user is setting the time between each search
         
        
        global count
        count +=1
        
        if count < 4:
            print("waiting For Record...\n")        
            time.sleep(timer)
            print(" No record found, trying again in %s seconds" % (timer))
            self.runsql(self.sql,self.DB_Path,timer,type)
        else:
            print(" No Results found")
            return
        
                


    def runsql(self, sql, DB_Path,timer,type):
        
        quary = 'echo "set echo off head off verify off feed off pages 0;\nset linesize 4000;\n'                           
        add = '"'
        end = " | sqlplus -S "
        #combine the sql query in unix
        sqlCommand = quary + sql + add + end + DB_Path      
        
        #echo "set echo off head off verify off feed off pages 0;\nset linesize 4000;\n select logical_date from logical_date where rownum=1;" | sqlplus -S ${AUTO_ABP_DB_APP}     
        logging.debug(sqlCommand)
        #print(quary + DB_Path +  "<<<" + add + sql + add)       
        p = Popen(sqlCommand, shell=True, stdout=PIPE)
        out = p.communicate()
        #print("this is out")
        #print(out[0])        
        getvalue = out[0]
        
        if (type.upper() == "UPDATE" or type.upper() == "DELETE") :
            logging.debug("committing")
            
            #auto commit 
            sqlCommand = quary + "commit;" + add + end + DB_Path
            
            p = Popen(sqlCommand, shell=True, stdout=PIPE)
            out = p.communicate()

            
        else:
            if (len(getvalue) > 0) :
                print("record found")
                return (getvalue)
            else:
                self.waitForRecord(timer,type)
            
        


# pre-condition: send the desire sql command that u need. example below:
#sql = "select * from logical_date;"
#pre condition to use this script is to provide the full $alias to DB. as example below
#DB_Path = "$AUTO_ABP_DB_APP"


#GetDB = runCommandtoSQL()
#GetDB.runsql(sql,DB_Path)




