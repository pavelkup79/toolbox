import os
import sys
import subprocess
#import AutomationSetup
from subprocess import Popen, PIPE
from threading import Timer
import logging
import time
import server
import serverSelection



class GetEnvStatus():
    
    #===========================================================================
    # this class is getting the Host and use to send Unix commands to Unix..
    # this class is being used by serverSelection.py to start/stop server in the env. 
    # @author: idan Shabat
    #===========================================================================    


    def __init__(self):
        logging.basicConfig(filename='serverHandling.log', filemode='w', level=logging.DEBUG)
        logging.debug('Starting class Get env status class')

        
        
        
        
    def GetEnvName(self): ## TODO - update doc
                     
        ########## GET HOST NAME ##########
        getHost = 'echo ${HOSTNAME}'
        #print("Getting env info")
        hostName = self.commandMe(getHost,10)
        logging.debug("host is " + hostName)        
        #print(hostName)    
        return hostName
        

    ############# RUN COMMANDS #############    
    def commandMe(self,command,timeout=10):
       # print("this is the command " + command)
        logging.debug("this is the command " + command) 
        p = Popen(command, shell=True, stdout=PIPE)
        logging.debug("starting timer")
        #print("starting timer")
        logging.debug(timeout)
        #print(timeout)
        timer = Timer(timeout, p.kill)
        timer.start()
         
        out = p.communicate()
        timer.cancel()   
           
        value = out[0].strip()
        logging.debug(value)
        
        return value  
        
            
    
    ############# CONNECT TO EXTERNAL SERVER #############
    def connect_ssh(self,serverName,Query,timeout= 10):        
        env = self.GetEnvName()
        command = "ssh " + serverName + "@" +  env + Query        
        status = self.commandMe(command,timeout)
         
        return status
        
        
     ############# Ping #############  
     #Need server Name e.g CRM , OMS, ABP , UIF
     #action: ping, forceStop, start          
    def pingme(self,serverName,action,timout=10):
        
        if (serverName.upper() == "CRM"):
            out = server.serversInfo.CRM(action)
        elif (serverName.upper() == "CRM_UIF"):       
            out = server.serversInfo.CRM_UIF(action)        
        elif (serverName.upper() == "OMS"):            
            out = server.serversInfo.OMS(action)
        elif (serverName.upper() == "OMNI"):            
            out = server.serversInfo.OMNI(action)
        elif (serverName.upper() == "OMS_SIMULATOR"):            
            out = server.serversInfo.OMS_SIMULATOR(action)
        elif (serverName.upper() == "OMS_SLR"):            
            out = server.serversInfo.OMS_SLR(action)
        elif (serverName.upper() == "OMS_UIF"):            
            out = server.serversInfo.OMS_UIF(action)                                                           
        elif (serverName.upper() == "ABP"):
           # self.commandMe('ibin;')
           out = server.serversInfo.ABP(action)
        else:
            print ("Unknown Server Selected! please try again")
            #serverSelection.ServerstatusMenu.Menu()

        status = self.connect_ssh(out[0],out[1],timout)    
        #print (serverName.upper() + " is " + status)
        logging.debug(serverName.upper() + " is " + status) 
        return status    
           
        

#GetEnvStatus = GetEnvStatus()
if __name__ == '__main__':
     GetEnvStatus()
          
        