import os
import sys
import subprocess
#import AutomationSetup
from subprocess import Popen, PIPE
import time
import logging

ABP_DB = {'dbUser':'dbUser', 'dbPass':'dbPass','dbInstance':'${APP_DB_INST}','dbHost':'${APP_DB_NODE}','dbPort':1521}
UNIX_SERVERS ={'CRM':"${AUTO_CRM_USER}@${AUTO_CRM_HOST}" , 'OMS' :"${AUTO_OMS_USER}@${AUTO_OMS_HOST}" ,'ABP':""}


class serversInfo():
    
    # This class specify all server in the system, and the path to INRA scripts
    ## INFRA RESPONSIBILITY TO populate the info##

    def __init__(self):
        
        logging.basicConfig(filename='serverHandling.log', filemode='w', level=logging.DEBUG)
        logging.debug('we are in ServerInfo class')      
    
     
    
    def CRM(self,action):
        serverName = "crmwrk1"
        #print( action + " CRM Server ")
        logging.debug(action + " CRM Server ")
        HOME_SCRIPT = ' "cd /users/gen/crmwrk1/JEE/CRMProduct/scripts/CRMDomain/CRMServer;'        
        userAction ='./' + action + 'CRMServer.sh' +'"'
        #Query = HOME_SCRIPT + './pingCRMServer.sh"'#OLD TO DELETE   
        Query = HOME_SCRIPT + userAction   
        #print(Query) 
        return (serverName,Query)

    def CRM_UIF(self,action):
        serverName = "crmwrk1"
        #print(action + " CRM UIF Server ")
        logging.debug(action + " CRM UIF Server ")
        HOME_SCRIPT = ' "cd /users/gen/crmwrk1/JEE/CRMProduct/scripts/SmartClientDomain/SmartClientServer;'        
        userAction ='./' + action + 'SmartClientServer.sh' +'"'
        #Query = HOME_SCRIPT + './pingCRMServer.sh"'#OLD TO DELETE   
        Query = HOME_SCRIPT + userAction    
        return (serverName,Query)
  
    
    def OMS(self,action):
        serverName = "omswrk1"
        #print(action + " OMS Server ")
        logging.debug(action + " CRM UIF Server ")
        HOME_SCRIPT = ' "cd /users/gen/omswrk1/JEE/OMS/scripts/OmsDomain/OmsServer;'   
        userAction ='./' + action + 'OmsServer.sh' +'"'
        Query = HOME_SCRIPT + userAction          
        #print(Query)   
        return (serverName,Query)

    def ABP(self,action):
        serverName = "abpwrk1"
        #print(action + " ABP Server ")
        logging.debug(action + " ABP Server ")
        HOME_SCRIPT = ' "cd /users/gen/abpwrk1/J2EEServer/config/ABP-FULL/ABPServer/scripts;'    
        userAction ='./' + action+ 'ABPServer.sh' +'"'    
        Query = HOME_SCRIPT + userAction
        return (serverName,Query)
    #//need to fix ABP CALL TODO

    def OMNI(self,action):
        serverName = "omsserver"
        #print(action + " OMNI Server ")
        logging.debug(action + " OMNI Server ")        
        HOME_SCRIPT = ' "cd ~omnwrk1/JEE/LightSaberDomain/scripts/LightSaberDomain/omni_LSJEE;'   
        userAction ='./' + action + 'omni_LSJEE.sh' +'"'
        Query = HOME_SCRIPT + userAction       
        #print(Query)   
        return (serverName,Query)        

    def OMS_UIF(self,action):
        serverName = "omswrk1"
        #print(action + " OMS_UIF Server ")
        logging.debug(action + " OMS_UIF Server ")
        HOME_SCRIPT = ' "cd /users/gen/omswrk1/JEE/OMS/scripts/OmsClient/OMS_SmartClient;'   
        userAction ='./' + action + 'OMS_SmartClient.sh' +'"'
        Query = HOME_SCRIPT + userAction
        return (serverName,Query)          

    def OMS_SLR(self,action):
        serverName = "omsserver"
        #print(action + " OMS_SLR ")
        logging.debug(action + " OMS_SLR ")
        HOME_SCRIPT = ' "cd ~slroms1/JEE/SolrProduct/scripts/SolrDomain_SolrServer/SolrServer;'   
        userAction ='./' + action + 'SolrServer.sh' +'"'
        Query = HOME_SCRIPT + userAction
        return (serverName,Query)              

    def OMS_SIMULATOR(self,action):
        serverName = "omsserver"        
        logging.debug(action + " OMS Simulator ")
        HOME_SCRIPT = ' "cd ~omswrk1/simulator/SoapSimulator;'   
        if (action == "forceStop"):
            action = "Stop"
            print(action + " OMS Simulator ")
        elif (action == "start"):
            action = "Run"
            print(action + " OMS Simulator ")                
        userAction ='./' + action + 'SoapSimulator.sh' +'"'
        Query = HOME_SCRIPT + userAction
        return (serverName,Query)          



serversInfo = serversInfo()
        
        