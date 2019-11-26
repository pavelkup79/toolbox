'''
Created on Sep 13, 2018

@author: pavelkup
'''
from UnixCmdBuilder import check_psu_count_cmd ,kill_by_psu_string_cmd ,bcolors
from SystemHandling import subproc_popen
import logging
import unittest
from LogHandling_Class import   *
logger = logging.getLogger("AutoToolBox")

class DaemonHandlerBase (object):
    
    def __init__(self,name_to_StartCmd ={},name_to_PsuString ={},name_to_Loglocation ={},name_to_LogFormat ={}):
        self.actions=("Trigger","Stop","Restart","Status")
        self.LOG_ERROR_STR =['FATAL',"ERROR:", "ORA-" ,"Exception","failed"]
        #d_name_to_StartCmd - dict {"daemonname":"StartCommand"} when StartCommand = command +params from l_DaemonData
        #l_DaemonData -list ['command','params','processName',"Type",'psu_string']
        #d_type_to_names  -dict  { "type" :["daemonName1","daemonName2"]} 
        #d_name_to_PsuString  - dict  { "name" :"psu_String"}         
        self.d_name_to_StartCmd=name_to_StartCmd
        self.d_name_to_PsuString=name_to_PsuString
        self.d_name_to_LogLocation =name_to_Loglocation
        self.d_name_to_LogFormat=name_to_LogFormat
        self.d_name_to_PassStr={}
          
        self.unix_check_psu_cmd = check_psu_count_cmd   
        self.unix_kill_dmn_cmd=kill_by_psu_string_cmd  
       
    def handle_daemons(self,action, *daemons): 
        if action not in self.actions:
            logger.error ("handleDaemonsByList -> Wrong action provided :" + str(action))
            return False
        logger.info("Handling daemons with action :" +str(action) )
        logger.debug("handleDaemonsByList-> daemons =" +str(daemons) + ", action =" +str(action) ) 
        daemons=sorted(daemons)
        statuses=self.get_daemon_satuses(*daemons)
        self.print_statuses(**statuses)
        if action in ('Stop','Restart') and  len(statuses['UP']) > 0 : 
            self.stop_daemons(* statuses['UP']) 
            if action =='Stop':
                self.handle_daemons('Status',* statuses['UP'])   
            elif action =='Restart':
                self.handle_daemons('Trigger',*statuses['UP'])             
        if action in ('Trigger','Restart') and  len(statuses['DOWN']) > 0 :                    
            self.start_daemons(* statuses['DOWN'])
            self.handle_daemons('Status',*statuses['DOWN']) 
        return True
    
    def handle_daemons_with_validation(self,action, *daemons): 
        if action not in self.actions:
            logger.error ("handleDaemonsByList -> Wrong action provided :" + str(action))
            return False
        logger.info("Handling daemons with action :" +str(action)+ " and log validation")
        logger.debug("handleDaemonsByList-> daemons =" +str(daemons) + ", action =" +str(action) ) 
        daemons=sorted(daemons)
        statuses=self.get_daemon_satuses(*daemons)
        self.print_statuses(**statuses)
        if action in ('Stop','Restart') and  len(statuses['UP']) > 0 :           
            self.stop_daemons(* statuses['UP']) 
            if action =='Stop':
                self.handle_daemons_with_validation('Status',* statuses['UP'])   
            elif action =='Restart':
                self.handle_daemons_with_validation('Trigger',*statuses['UP'])             
        if action in ('Trigger','Restart') and  len(statuses['DOWN']) > 0 :  
            for daemon  in statuses['DOWN']:
                log_location=self.d_name_to_LogLocation[daemon]
                log_format=self.d_name_to_LogFormat[daemon]
                if   self.check_log_exist(log_location ,log_format)== True:
                     self.backup_log(log_location,log_format )                
            self.start_daemons(* statuses['DOWN'])
            for daemon  in statuses['DOWN']:
                self.is_str_in_log( log_location , log_format ,self.d_name_to_PassStr[daemon])
                self.check_errs_in_log( log_location , log_format,self.LOG_ERROR_STR)
            self.handle_daemons_with_validation('Status',*statuses['DOWN']) 
        return True          
                   
    def get_daemon_satuses (self , * daemons ):  
        """get daemons list and return statuses {'UP':['DB2E' ,'F2E'], 'DOWN' :['ES_RB']"""
        logger.info("Checking statuses..." )
        statuses ={'UP':[],'DOWN':[]}
        for daemon_name in daemons:  
            if daemon_name not in self.d_name_to_PsuString.keys():
                logger.error("Daemon Doesn't exist in the list :"+str(daemon_name) )  
                return 
            psu_string =self.d_name_to_PsuString[daemon_name]       
            if self.IsDaemonNameValid (psu_string): 
                psu_cmd = self.unix_check_psu_cmd(psu_string)                 
                logger.info("Checking status with  : " +  psu_cmd)   
                data =subproc_popen(psu_cmd)
                if int(str(data[0]).rstrip('\n'))>0:
                    statuses['UP'].extend([daemon_name])
                elif int(str(data[0]).rstrip('\n')) ==0:
                    statuses['DOWN'].extend([daemon_name])
                else :
                    logger.error("checkDaemonStatus-> issue with status " +str(data[0]).rstrip('\n') )
        return statuses                 
                              
    def start_daemons(self, *daemons):      
        """ get list  of daemons and starting all daemons """  
        for daemon_name  in daemons:
            if self.IsDaemonNameValid (self.d_name_to_StartCmd[daemon_name]):
                start_cmd = self.d_name_to_StartCmd[daemon_name]
                logger.info("Starting " + str(daemon_name) + "...with command : "+ str(start_cmd)  )#+ start_cmd
                subproc_popen(start_cmd)



    def stop_daemons(self, * daemons):  
        """ get unix function to get status from Unix an list of psu_string """
        logger.info("Stopping daemons...." )
        for name in daemons:  
            psu_string =str(self.d_name_to_PsuString[name])
            if self.IsDaemonNameValid (psu_string):                                 
                kill_cmd = self.unix_kill_dmn_cmd(psu_string)
                logger.debug("Running stopDaemon -> with : psu_string=" + str(psu_string) + " ,unix_cmd=" + kill_cmd )   
                logger.info("Stop daemon  with  : " +  kill_cmd)   
                data =subproc_popen(kill_cmd)



    def print_statuses(self,**statuses): 
        """ get dictionary    {"UP": [Daemons list],"DOWN" :[DaemonsList] } and print  statuses  when status UP or DOWN"""
        logger.debug("printDaemonStatuses-> statuses =" +str(statuses) )
        if type(statuses) is dict and statuses  : 
                for daemon in statuses['UP']:
                    print "================================"
                    print (str(daemon) +" is " +bcolors.OKGREEN  + 'UP'+bcolors.ENDC )
                    
                for daemon in statuses['DOWN']:
                    print "================================"
                    print (str(daemon) +" is " +bcolors.FAIL  + 'DOWN' + bcolors.ENDC)

    def  print_all_commands(self,**daemons):
        """function gets dict of type {"daemonName":"StartCommand"} and print "StartCommand" values"""
        logger.info("Printing all start commands for " +self.__class__.__name__ )
        logger.debug("Printing all start commands..." )
        for daemon in daemons   :
            print daemons[daemon]      

              
    def IsDaemonNameValid(self,proc_name):
        if  proc_name <> None and proc_name <> "" and len(proc_name) > 2 :
            return True
        else:
            logger.error(">>>IsDaemonNameValid -> proc_name is not valid :" + str(proc_name) )
            return False
        
    def get_log_path(self):
        data =subproc_popen('echo ${OP_LOG_DIR}')
        return str(data[0]).rstrip('\n')               

    
    """               
    def stopDaemon(self,proc_name ,psu_string="" ,get_unix_cmd  = kill_by_psu_string_cmd):  
        #get psu_string of daemon as parameter for unix function and unix function to get status from Unix 
        logger.info("Stopping daemon...." )
        logger.debug("Running stopDaemon -> with : proc_name=" + proc_name +" ,psu_string="+ str(psu_string)+ 
                    " ,get_unix_cmd=" +str(get_unix_cmd) )        
        proc_name =str(proc_name)
        if self.IsDaemonNameValid (proc_name):
            if not self.IsDaemonNameValid(psu_string):
               psu_string = proc_name                                     
            psu_cmd = get_unix_cmd(psu_string)
            logger.info("Stop daemon  with  : " +  psu_cmd)   
            data =subproc_popen(psu_cmd)


    def startDaemon(self, proc_name ,start_cmd):        
        logger.info("Starting " + str(proc_name ) + "...with command : "+ str(start_cmd)  )#+ start_cmd
        data=subproc_popen(start_cmd)
        return data



    def handleDaemonsByList(self,action ='Status', *daemons): 
        
        logger.info("Handling daemons with action :" +str(action) )
        logger.debug("handleDaemonsByList-> daemons =" +str(daemons) + ", action =" +str(action) ) 
        daemons=sorted(daemons)
        statuses={}
        for daemon in daemons:
            statuses.update( self.checkDaemonStatus( daemon,self.d_name_to_PsuString[daemon]) )# by default will use functioncheck_psu_count_cmd
        self.printDaemonStatuses(statuses)
        for daemon in statuses:
            if action in ('Stop','Restart') and   statuses[daemon] =="UP": 
                self.stopDaemons(kill_by_psu_string_cmd,self.d_name_to_PsuString[daemon]) #by default will use kill_by_psu_string_cmd
                if action =='Stop':
                    self.handleDaemonsByList('Status',daemon)   
                elif action =='Restart':
                    self.handleDaemonsByList('Trigger',daemon)             
            if action in ('Trigger','Restart') and statuses[daemon] =='DOWN':                    
                         self.startDaemons(**{daemon: self.d_name_to_StartCmd[daemon]} )
                         self.handleDaemonsByList('Status',daemon) 
            if action not in ('Status','Trigger','Stop','Restart'):
                logger.error ("handleDaemonsByList -> Wrong action provided" )
                return

    
    def checkDaemonStatus(self,proc_name ,psu_string="" ,get_unix_cmd = check_psu_count_cmd ):  
        #get psu_string of daemon as parameter for unix function and unix function to get status from Unix 
        and return statuses as dictionary
        statuses ={}
        proc_name =str(proc_name)
        logger.info("Running checkDaemonStatus -> with : proc_name=" + proc_name +" ,psu_string="+ str(psu_string)+ 
                    " ,get_unix_cmd=" +str(get_unix_cmd) )
        if self.IsDaemonNameValid (proc_name):
            if not self.IsDaemonNameValid(psu_string):
               psu_string = proc_name                                     
            psu_cmd = get_unix_cmd(psu_string)
            logger.info("Checking status with  : " +  psu_cmd)        
            data =subproc_popen(psu_cmd)
            if int(str(data[0]).rstrip('\n'))>0:
                statuses.update({proc_name:'UP'})
            elif int(str(data[0]).rstrip('\n')) ==0:
                statuses.update({proc_name:'DOWN'})
            else :
                logger.error("checkDaemonStatus-> issue with status " +str(data[0]).rstrip('\n') )
        return statuses  

      
    def startDaemons(self, **start_commands):      
        #get dict of {'daemon:'Start command'}  and starting all daemons
        for daemon_name  in start_commands:
            if self.IsDaemonNameValid (start_commands[daemon_name]):
                logger.info("Starting " + str(daemon_name) + "...with command : "+ str(start_commands[daemon_name])  )#+ start_cmd
                subproc_popen(start_commands[daemon_name])


    def checkDaemonsStatus(self, get_unix_cmd = check_psu_count_cmd ,*daemons ):  
        #get list of daemon as parameter for unix function and unix function to get status from Unix 
        #and return statuses as dictionary
        statuses ={}
        for daemon_name in daemons:
            psu_string =self.d_name_to_PsuString[daemon_name] 
            if self.IsDaemonNameValid (psu_string):
                psu_cmd = get_unix_cmd(psu_string )
                logger.info("Running checkDaemonStatus -> with : proc_name=" + str(daemon_name)+" ,psu_string="+ str(psu_string)+ 
                    " ,get_unix_cmd=" +str(get_unix_cmd) )
                data =subproc_popen(psu_cmd)
                if int(str(data[0]).rstrip('\n'))>0:
                    statuses.update({proc_name:'UP'})
                elif int(str(data[0]).rstrip('\n')) ==0:
                    statuses.update({proc_name:'DOWN'})
                else :
                    logger.error("checkDaemonStatus-> issue with status " +str(data[0]).rstrip('\n') )
        return statuses 

    def printDaemonStatuses(self,statuses): 
        #get and print  statuses   {"DemonName": "status"}  when status UP or DOWN
        logger.debug("printDaemonStatuses-> statuses =" +str(statuses) )
        if type(statuses) is dict and statuses  : 
            for daemon in statuses.iteritems():
                print "================================"
                if daemon[1]=='UP' :           
                    print (str(daemon[0]) +" is " +bcolors.OKGREEN  + str(daemon[1]))+bcolors.ENDC
                elif daemon[1]=='DOWN' :
                    print (str(daemon[0]) +" is " +bcolors.FAIL  + str(daemon[1]))+bcolors.ENDC
                else :
                    logger.error("printDaemonStatuses-> status is not valid for "+daemon[0]+ " ,status =" +str(daemon[1]))
                print "================================"
        else:
            logger.error("printDaemonStatuses->statuses retrieved are not valid  " )
     
    def stopDaemons(self,get_unix_cmd  = kill_by_psu_string_cmd, *psu_strings):  
        #get unix function to get status from Unix an list of psu_string
        logger.info("Stopping daemon...." )
        for name in psu_strings:  
            if self.IsDaemonNameValid (name):                                 
                kill_cmd =  self.unix_kill_dmn_cmd(name)
                logger.debug("Running stopDaemon -> with : psu_string=" + str(name) + " ,get_unix_cmd=" +kill_cmd)    
                logger.info("Stop daemon  with  : " +  kill_cmd)   
                data =subproc_popen(kill_cmd)
"""
    
####################################UNIT TEST #############################################



#if __name__ == "__main__":


                   