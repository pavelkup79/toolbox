import os
import sys
import subprocess
from subprocess import Popen, PIPE
from threading import Timer
import logging
from SystemHandling import run_sql
import time
import server
import serverSelection
import DBHandler
import datetime
from JobHandling_Class import JobHandling

db ={'dbUser':'ABPAPP1', 'dbPass':'ABPAPP1','dbInstance':'VFIDB480','dbHost':'illinqw480','dbPort':1521}

# Added by Pavel 
def set_logical_date(date='sysdate',refresh = 'Y'):
    """ set logical_date , by default to be system date in DD/MM/YY format"""
    setLD="update logical_date set logical_date =to_date(" + str(date)+ ",'DD/MM/YY') where EXPIRATION_DATE is null;commit;"
    run_sql(setLD,db)
    if refresh == 'Y':
        JobHandling().RunJob("UTL1REFNOT")
    


def update_logical_date(delta = 1,refresh = 'Y'):
    """ update logical_date , by default will forward LD  by one"""
    updateLD="update logical_date set logical_date =logical_date +" + str(delta)+ " where EXPIRATION_DATE is null;commit;"
    run_sql(updateLD,db)
    if refresh == 'Y':
        JobHandling().RunJob("UTL1REFNOT")




class LDHandler:
    
    #===========================================================================
    # this class will handle LD changes
    # @author: idan Shabat
    #===========================================================================

    def __init__(self):
        logging.basicConfig(filename='serverHandling.log', filemode='w', level=logging.DEBUG)
        logging.debug('Starting class LD Handler')
        #self.Menu() #Unmark to use the menu
    
    
    def LDoneline(self,type,date):
        DB_Path = "$AUTO_ABP_DB_APP"
        
        logging.debug("we are in LD one liner")
        logging.debug(date)
        
        if type == "get":
            
            logging.debug("Doing Get LD now")
            sql = "select logical_date,logical_date_type from logical_date where expiration_date is null;"
            result = DBHandler.runCommandtoSQL(sql,DB_Path).runsql(sql,DB_Path,1,"get")            
            return result

            
        elif type == "update":
            logging.debug("update LD to " + date)
            logging.debug("with this SQl: ")            
            sql = "update logical_date set logical_date = " + "'" + date + "'" + " where  Expiration_Date is null;"   
            logging.debug(sql)         
            result = DBHandler.runCommandtoSQL(sql,DB_Path).runsql(sql,DB_Path,1,"update")
            print("running EOD job")
            D = JobHandling()
            J = D.RunJob("UTL1REFNOT" ,"BYREQ",'',60)
            
            return "Done"                             

    def Menu(self):

        menu = {}
        menu['1']="Show Logical_date"
        menu['2']="Show entire Logical_date table"
        menu['3']="Update logical Date"
        menu['4']="Back"
        
        DB_Path = "$AUTO_ABP_DB_APP"

        while True:
            options = menu.keys()
            options.sort()
            print ("\033[1;33;40m \nWelcome to LD Handler Menu \n \033[0m")

            i = 0
            for i,j in enumerate(menu):
                n = str(i+1)            
                print ("[ " + n + " ] " + menu[n])                
                i+=1            


            self.selection = raw_input("\nPlease select an option:\n")

            if self.selection == '1':
                os.system("clear")
                sql = "select logical_date,logical_date_type from logical_date where expiration_date is null;"
                result = DBHandler.runCommandtoSQL(sql,DB_Path).runsql(sql,DB_Path,1,"get")
                print(result)                
            elif self.selection == '2':
                os.system("clear")
                sql = "select * from logical_date;"
                result = DBHandler.runCommandtoSQL(sql,DB_Path).runsql(sql,DB_Path,1,"get")
                print(result)                
            elif self.selection == '3':
                os.system("clear")
                self.SubMenu(DB_Path)
                # add: please run the proper RunJob

            elif self.selection == '4':
                # add here a proper exit
                break

            else:
                print ("Unknown Option Selected!")
                
       

    def SubMenu(self,DB_Path):

        menu = {}
        menu['1']="Update all LD"
        menu['2']="Update LD of type 'O'"
        menu['3']="Update LD of type 'R'"
        menu['4']="Update LD of type 'B'"
        menu['5']="Back"
        
        

        while True:
                
            options = menu.keys()
            options.sort()
            print ("\033[1;33;40m \nWelcome to LD UPDATE Menu \n \033[0m")
            
            
            i = 0
            for i,j in enumerate(menu):
                n = str(i+1)            
                print ("[ " + n + " ] " + menu[n])                
                i+=1
                
               
            
            self.selection = raw_input("\nPlease select an option:\n")
                                            
            

            if self.selection == '1':
                os.system("clear")         
                
                
                endofquery = "Expiration_Date is null"                                                                            
                self.LD_update(endofquery,DB_Path)
                   
            elif self.selection == '2':
                os.system("clear")
                
                endofquery = "Logical_Date_Type = 'O' and Expiration_Date is null"                                                                            
                self.LD_update(endofquery,DB_Path) 
                                 
            elif self.selection == '3':
                os.system("clear")
                
                endofquery = "Logical_Date_Type = 'R' and Expiration_Date is null"                                                                            
                self.LD_update(endofquery,DB_Path) 
            
            
            elif self.selection == '4':
                os.system("clear")
                
                endofquery = "Logical_Date_Type = 'B' and Expiration_Date is null"                                                                            
                self.LD_update(endofquery,DB_Path)                                                  

                
            elif self.selection == '5':
                os.system("clear")
                logging.debug(self.selection)
                break
            
    def LD_update(self,endofquery,DB_Path):

        inputDate = int(input("Enter the amount of days you wish to move: [e.g: 10,1,-50 ]: \n "))
        if (inputDate >= 0):
            marker = "+"
        else:
            marker = "-"
            inputDate = abs(inputDate)
             
        # current LD
        #===============================================================
        sql = "select logical_date,logical_date_type from logical_date;"                
        result = DBHandler.runCommandtoSQL(sql,DB_Path).runsql(sql,DB_Path,1,"get")
        print("old \n" + result)                    
        #===============================================================      
        

        
        
        #Update LD    
        sql = "update logical_date set logical_date = (Logical_Date " + marker +" "+ str(inputDate) + ") where " + endofquery +";"
        logging.debug(sql)                         
        DBHandler.runCommandtoSQL(sql,DB_Path).runsql(sql,DB_Path,1,"update")            
        
        
        
        #Check new LD
        #===============================================================
        sql = "select logical_date,logical_date_type from logical_date where expiration_date is null;"
        result2 = DBHandler.runCommandtoSQL(sql,DB_Path).runsql(sql,DB_Path,1,"get")
        print("New \n" + result2)
         
        logging.debug("\nEND 2")
        #===============================================================
        
        
        #Running EOD JOB
        print("running EOD job")
        D = JobHandling()
        J = D.RunJob("UTL1REFNOT" ,"BYREQ",'',60)
        
        
        
        
        
        #print("RunJob is now running")
        #cmd = "RunJobs UTL1REFNOT BYREQ;"
        try:
            subprocess.check_output(cmd, shell=True).rstrip("\n")
        except:
            print (">>> Command Error")
            return 1
        print (">>> Job has been triggered , checking logs in ~/AutoToolBox/Logs")
        
        #JobHandling.RunJob("UTL1REFNOT","ENDDAY","",40)    
        
        logging.debug("END 3")       
            


if __name__ == '__main__':
    LDHandler()