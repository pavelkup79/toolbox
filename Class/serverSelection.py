import os
import sys
from subprocess import Popen, PIPE
import csv
import io
import subprocess, shlex
import time
import logging
#logger = logging.getLogger("AutoToolBox")


import commands



class ServerstatusMenu:
    
    #===========================================================================
    # this class will open a menu to start / stop/ ping all servers in the env.
    # need to connect this class to the main menu class 
    # @author: idan Shabat
    #===========================================================================
    

    def __init__(self):
        logging.basicConfig(filename='serverHandling.log', filemode='w', level=logging.DEBUG)
        logging.debug('Starting class')        
        
        

        
        self.Menu()

    def Menu(self):

        menu = {}
        menu['1']="ABP Server\n"
        menu['2']="CRM Server\n"
        menu['3']="CRM-UIF Server\n"
        menu['4']="OMS Server\n"
        menu['5']="OMS UIF Server\n"
        menu['6']="OMNI\n"
        menu['7']="OMS Solar\n"
        menu['8']="All Servers\n"
        menu['9']="Back"

        while True:
            options = menu.keys()
            options.sort()
            print ("\033[1;33;40m Welcome to Server Handling Menu \033[0m\n")
            serverslist = ["ABP","CRM","CRM_UIF","OMS","OMS_UIF","OMNI","OMS_SLR"]
            print ("[ 1 ] " + serverslist[0] + " Server \n[ 2 ] " + serverslist[1] + " Server \n[ 3 ] " + serverslist[2] + " Server \n[ 4 ] " + serverslist[3] + " server \n[ 5 ] " + serverslist[4] + " Server \n[ 6 ] " + serverslist[5] + " \n[ 7 ] " + serverslist[6] + "\n[ 8 ] \033[1;33;40mAll Servers \033[0m\n[ 9 ] Back")

            self.selection = raw_input("\033[1;33;40m \nPlease select an option:\033[0m\n")

            if self.selection == '1':
                self.SubMenu(serverslist[0])
                
            elif self.selection == '2':
                self.SubMenu(serverslist[1])
                
            elif self.selection == '3':
                self.SubMenu(serverslist[2])

            elif self.selection == '4':
                self.SubMenu(serverslist[3])
                
            elif self.selection == '5':
                self.SubMenu(serverslist[4])
                
            elif self.selection == '6':
                self.SubMenu(serverslist[5])
                
            elif self.selection == '7':
                self.SubMenu(serverslist[6])

            elif self.selection == '8':
                self.getallstatuses(serverslist)
                                                
            elif self.selection == '9':
                os.system("clear")                
                break                
            else:
                print ("Unknown Option Selected! please try again")
                self.Menu()
                
    def getallstatuses(self,serverslist):
                os.system("clear")
                print("Check Env Status \n")
                Downlist = []
                
                for i,value in enumerate(serverslist):
                    ping = commands.GetEnvStatus().pingme(value,"ping",10)
                                        
                    RED = "\033[31m"
                    GREEN="\033[0;32m"
                    if ping == "DOWN":
                        result = (RED + "DOWN \033[0m\n")
                        Downlist.append(value)                                                
                    elif ping == "UP":
                        result = (GREEN + "UP \033[0m\n" )
                    
                    print ("\033[1;33;40m" +value + " \033[0m server status is " + (12-len(value)) * "-" + " " +  result)
                
                print("[ 1 ] Start all servers \n[ 2 ] Ping all servers \n[ 3 ] Back ")
                allselection = raw_input("\033[1;33;40mPlease select an option: \033[0m\n")
               
                
                if (allselection == "1"):
                    if len(Downlist) != 0:
                        for i,server in enumerate(Downlist):
                            logging.debug(Downlist)
                            logging.debug("StackTrace SERRVERHANDLING #123456 ")
                            logging.debug("the server is: " + server)
                            print("Taking "+ server +" Server UP \n")
                            commands.GetEnvStatus().pingme(server,"start",10)
                    else:
                        print("All servers are UP \n")
                        
                    
                elif (allselection == "2"):
                    self.getallstatuses(serverslist)
                                        
                else:
                    pass
             
                logging.debug(Downlist)        
        
        
    
    
    def SubMenu(self,server):

        menu = {}
        menu['1']="Get Server status"
        menu['2']="STOP server"
        menu['3']="START server"
        menu['4']="RESTART server"
        menu['5']="Back"

        while True:            
            options = menu.keys()
            options.sort()
            print ("\033[1;33;40m Welcome to "+ server +"\033[0m\n")  
            
            i = 0
            for i,j in enumerate(menu):
                n = str(i+1)            
                print ("[ " + n + " ] " + menu[n])                
                i+=1            
            
                      
            #print ("[ 1 ] Get Server status \n[ 2 ] STOP server \n[ 3 ] START server \n[ 4 ] RESTART server \n[ 5 ] Back")
            logging.debug("###### Starting Menu ########")

            self.selection = raw_input("\nPlease select an option:\n")

            if self.selection == '1':
                os.system("clear")
                logging.debug(self.selection)
                print("Running command \n")
                result = commands.GetEnvStatus().pingme(server,"ping",10)
                print("Server is " + result + "\n")         
                                              
            elif self.selection == '2':
                os.system("clear")
                logging.debug(self.selection)
                result = commands.GetEnvStatus().pingme(server,"forceStop",10)
                print(server + " Server is going Down ...\n")
                 
            elif self.selection == '3':
                os.system("clear")
                logging.debug(self.selection)
                result = commands.GetEnvStatus().pingme(server,"start",10)
                print(server + " Server is going UP ... \n") 
            elif self.selection == '4':
                logging.debug(self.selection)
                os.system("clear")
                print(" Restarting "+ server + " ..... \n")
                result = commands.GetEnvStatus().pingme(server,"ping",5)             
                i = 0
                if (result == "UP"):
                    print(server + "Server is Going Down... \n")
                    stop = commands.GetEnvStatus().pingme(server,"forceStop",10)
                    time.sleep(3)
                    result = commands.GetEnvStatus().pingme(server,"ping",10)
                    if ((result == "UP") and (i<5)):
                        i+=1
                        logging.debug(i)
                        result = commands.GetEnvStatus().pingme(server,"ping",10)                        
                                                                                                                                 
                if (result == "DOWN"):                    
                    print(server + "Server is Down. going UP ... \n")
                    time.sleep(3)
                    start = commands.GetEnvStatus().pingme(server,"start",5)
                    result = commands.GetEnvStatus().pingme(server,"ping",10)
                    while ((result == "DOWN") and (i<15)):
                        i+=1
                        time.sleep(6)
                        #print (i)
                        logging.debug(i)
                        result = commands.GetEnvStatus().pingme(server,"ping",10)
                    if(result == "DOWN"):
                        print("server is still down, pleases check startup logs.\n") 
                    else:
                        logging.debug("this is the result: " + result)
                        print("server is \033[1;33;40m" + result + "\033[0m\n")   
                    return result
 
                logging.debug('we are out of restart loop\n')            
            elif self.selection == '5':
                os.system("clear")
                break
            else:
                print ("Unknown Option Selected! please try again \n")
  

        
if __name__ == '__main__':
    ServerstatusMenu()