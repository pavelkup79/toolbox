#from OraDBConnect import OracleDBConnector
'''
Created on Sep 13, 2018

@author: pavelkup
'''
import logging
import platform
from server import *
import os
import string
from SystemHandling import SystemHandler,subproc_popen
from UnixCmdBuilder import clean_shared_memory_cmd,sqlplus_query,check_psu_count_cmd,kill_by_psu_string_cmd
from Menu import Menu
from DaemonBase import DaemonHandlerBase
from LogHandling_Class import   *

logger = logging.getLogger("AutoToolBox")
db = ABP_DB
#Check Logs

"""
LogPath ='${OP_LOG_DIR}' 
format ='ES_RB1212*log' 
log_exist = [ -f *"ES_RB1213"*".log" ] && echo 'Pass' || echo 'Fail
path = '/users/gen/abpwrk1/var/mps/log'
"""

class TCDaemonsHandler(DaemonHandlerBase,LogHandling):
    """ ATTRIBUTES:  daemonName-name of daemon like ES_RB1024
                     type (group) - daemon type , relevant only for TC like  ES_RB
                     psu_string - string that we are using to filter the daemon in Unix by psu 
                     startCmd -command that we are using to start the daemon in Unix
                     stopCmd- command we are using to stop the daemon in Unix
                     GetTCDaemonsCMDsQuery - query that we are using to get all attributes from DB 
                     
        FUNCTIONS :
                    db_get_all_TCcommands  - query DB and get all daemos and it's data (used only once when Instance is created)
                    clean_sharedMemory - cleaning shared memory
                    get_psu_string - helper function to get psu_string (used only once when Instance is created)
    """
    def __init__(self):
        DaemonHandlerBase.__init__(self)
        logger.debug("Creating TCDaemonHandler Instance , running SQl DB Quesry to load TC Daemon Data.... ")      
        self.GetTCDaemonsCMDsQuery = '''SELECT DISTINCT PTC.SCRIPT_NAME || ' -n ' || PIC.PROCESS_CODE || ' -c '||'#'|| PIC.STATIC_PROC_ARGS||' '|| PIC.DYNAMIC_PROC_ARGS ||'#'||PIC.PROCESS_CODE
        FROM GN1_SYS_PROCESS_TYPE_CFG PTC, GN1_SYS_PROC_INSTANCE_CFG PIC, GN1_SYS_SEG_PROC_CFG SPC
        WHERE PTC.PROCESS_TYPE_ID = PIC.PROCESS_TYPE_ID
        AND PTC.PROCESS_TYPE_CODE IN ('ES', 'RRP_OG','DB2E',' DB2E_ERR','DSP', 'F2E', 'GAT2E', 'NTF','UHI','UHF', 'UQ_SERVER','ELA')
        AND (PRIORITY_WITHIN_GROUP = 0 OR PRIORITY_WITHIN_GROUP = 99)
        AND PIC.PROCESS_CODE NOT LIKE '%EOC%'
        AND PIC.PROCESS_GROUP_ID=SPC.PROCESS_EXEC_ID
        AND SPC.BACKUP_ORDER=0
        ORDER BY 1'''#
        self.LOG_PASS_STR ="running the process in Background.."


        #d_name_to_StartCmd - dict {"daemon name":"StartCommand"} when StartCommand = command +params from l_DaemonData
        #l_DaemonData -list ['command','params','processName',"Type",'psu_string']
        #d_type_to_names  -dict  { "type" :["daemonName1","daemonName2"]} 
        #d_name_to_PsuString  - dict  { "name" :"psu_String"} 
        #d_name_to_PassStr
        if platform.system() =='Linux':
            self.d_name_to_StartCmd ,self.l_DaemonData,self.d_type_to_names,self.d_name_to_PsuString,self.d_name_to_PassStr,self.d_name_to_LogLocation,self.d_name_to_LogFormat= self.db_get_all_TCcommands()
        else:
            logger.error("Program is running not on Linux platform")

    def db_get_all_TCcommands(self):
        """ function return:
         dict {tcdaemonName:StartCommand } and
         list ['command','params','processName',"Type",'psu_string']
         dict {Type: [processName1 ,processName2] }
         dict {'daemonName' : 'psu_string'}        
         dicy {daemonName' :"pass String"}"""
        data = subproc_popen(sqlplus_query(self.GetTCDaemonsCMDsQuery,db))#Run DataBase query to get TC commands
        type_to_names ={}
        name_to_psuString ={} 
        name_to_logFormat={}
        name_to_logLocation={}
        TCDaemons={} 
        name_to_passStr={}
        DaemonData =[]
          
        DaemonData=str(data[0]).rstrip('\n')#Remove last enter in the response and copy tuple to the list        
        DaemonData=str(DaemonData).split('\n')# split the list by '\n' will create list of lists .list per daemon
        i=0
        for daemon in DaemonData:
            DaemonData[i] =daemon.split('#') #go over list of lists and for each one of lists split using predefined '#' sign in query
            DaemonData[i].extend([DaemonData[i][2].rstrip(string.digits)])
            DaemonData[i].extend([self.get_psu_string(DaemonData[i][3],DaemonData[i][2])])
            TCDaemons.update({DaemonData[i][2]: DaemonData[i][0] +'"' + DaemonData[i][1]+ ' "' })#insert daemon name and its command to dictionary
            name_to_psuString.update({ DaemonData[i][2] : DaemonData[i][4] })
            name_to_passStr.update({ DaemonData[i][2] :self.LOG_PASS_STR})
            name_to_logLocation.update({ DaemonData[i][2] : self.get_log_path() })
            name_to_logFormat.update({ DaemonData[i][2] : '*'+DaemonData[i][2]+'*.log*'  })
            if DaemonData[i][3] in type_to_names:
               type_to_names[DaemonData[i][3]].extend( [DaemonData[i][2]] ) 
            else:
               type_to_names.update({  DaemonData[i][3] : [DaemonData[i][2]]}) 
            i=i+1
        return TCDaemons ,DaemonData,type_to_names,name_to_psuString,name_to_passStr,name_to_logLocation,name_to_logFormat
     
    def clean_sharedMemory(self):
        logger.info("Cleaning shared memory...." ) 
        data =subproc_popen(clean_shared_memory_cmd())
        return data

    def get_psu_string (self,type,process_id):
        """get PSU_STRING - return string that we check with if proces is up"""
        PSU_STRING={('ES_FR','ES_RB','DB2E','F2E','UQ_SERVER','DSP','NTF','ELA','GAT2E','RRP_OG','ROR','RER','ROR_SERVER'):"gcpf1fwcApp.*" + str(process_id),
                         ('UHI_GD','UHI_RT','UHF','UHF_RT','UHF_BYCYC','UHF_Mini_GD','UHF_Mini_RT'):"DuhProcInst.*" + str(process_id) +".*DuhProfile="} 
        is_exist =False
        for row in PSU_STRING:
            if type in row:
                is_exist =True
                logger.debug("get_psu_string for  input type =" +str(type) + ", process_id ="+ str (process_id)+" output: "+ PSU_STRING[row] )
                return PSU_STRING[row]
        if is_exist ==False:
                logger.error("get_psu_string for  input type =" +str(type) + ", process_id ="+ str (process_id)+" output: Type doesn't exist" )

    def __del__(self): 
        pass   
    
    
    
    
    
     
################################################################################################################    
 ######################################### MENU ###################################################
 ##############################################################################################
       
class TCDaemonsMenu(TCDaemonsHandler,Menu):  
    def __init__(self):
        TCDaemonsHandler.__init__(self)
        #super(TCDaemonsHandler, self).__init__()
        self.MenuName="TC Daemons Menu"
        self.selectedItemToTCType={"ES Rating":"ES_RB" ,"ES Guiding":"ES_FR","File2E":"F2E","DB2E":"DB2E","UQ - Usage Query":"UQ_SERVER",
                              "Dispatcher":"DSP","RRP - Ongoing Rerate" :"RRP_OG" ,"ELA":"ELA","GAT2E":"GAT2E",
                              "UH Incr - Rating":"UHI_RT","UH Incr - Guiding": "UHI_GD","UH Full - Rating":"UHF_RT" ,"UH Full - Guiding":"UHF" ,"All TC Daemons":"All TC Daemons",
                              "All TC Daemons with validation":"All TC Daemons with validation"}
        self.TCType=None
        self.IsMenuActive=True
        self.TCAllList=['ES_FR1049','ES_FR1051','ES_RB1046','ES_RB1212','F2E1068','F2E1069','DB2E1074','DB2E1076','DSP1056','DSP1061']
        self.selectedList =[]#  list to populate  according to user selection 
        self.menuItems= [ 
            {"Show all start commands for TC daemons": self.get_All_TCcommands_menu },
            {"Clean shared memory": self.cleanSharedMemory_menu  },
            {"ES Rating":self.tcDaemonsOperations_menu},
            {"ES Guiding": self.tcDaemonsOperations_menu},
            {"File2E":self.tcDaemonsOperations_menu},
            {"DB2E":self.tcDaemonsOperations_menu},
            {"UQ - Usage Query": self.tcDaemonsOperations_menu},
            {"Dispatcher":self.tcDaemonsOperations_menu},
            {"RRP - Ongoing Rerate":self.tcDaemonsOperations_menu},
            {"ELA": self.tcDaemonsOperations_menu},
            {"GAT2E":self.tcDaemonsOperations_menu},
            {"UH Incr - Rating":self.tcDaemonsOperations_menu},
            {"UH Incr - Guiding": self.tcDaemonsOperations_menu},
            {"UH Full - Rating" : self.tcDaemonsOperations_menu},
            {"UH Full - Guiding": self.tcDaemonsOperations_menu},
            {"All TC Daemons": self.tcDaemonsOperations_menu},
            {"All TC Daemons with validation": self.tcDaemonsOperations_menu},
            {"TC Daemons for event processing":self.get_All_TCcommands_menu},
            {"Back": self.back_menu},
            {"Exit": self.exit_menu}
            ]

    def get_All_TCcommands_menu (self,option=None):
        """ Menu get all TC daemons start commands  """
        MenuName ="Showing all start commands for TC daemons "
        os.system('clear')
        #TCDaemonsHandler().print_all_TC_commands()
        self.print_all_commands(**self.d_name_to_StartCmd)
        self.print_menu_items(menuName=MenuName)
        
    def cleanSharedMemory_menu(self,option=None):   
        """ Menu clean TC shared Memory"""     
        MenuName ="Cleaning shared memory with maainfo -rm"
        os.system('clear')
        TCDaemonsHandler().clean_sharedMemory()      
        self.print_menu_items(menuName=MenuName)
        
    def tcDaemonsOperations_menu(self,DaemonTypeChoice): 
        """ Menu to start stop or get status for preselected TC daemon""" 
        MenuName="TC Daemons - Operations"
        handle_daemon =self.handle_daemon_bylist_menu
        if self.selectedItemToTCType[DaemonTypeChoice] in ( "All TC Daemons" ,"All TC Daemons with validation"):
            self.selectedList =self.TCAllList
            if self.selectedItemToTCType[DaemonTypeChoice] =="All TC Daemons with validation":
               handle_daemon =self.handle_daemon_validate_menu 
            
        else:
           self.selectedList = self.d_type_to_names[self.selectedItemToTCType[DaemonTypeChoice] ] 
           handle_daemon =self.handle_daemon_bylist_menu

        menuItems= [ 
            {"Status": handle_daemon},
            {"Stop": handle_daemon},
            {"Trigger": handle_daemon},
            {"Restart": handle_daemon},
            {"Back": self.activate_menu},
            {"Exit": self.exit_menu}]
        os.system('clear')
        print "Please select operation for " +self.selectedItemToTCType[DaemonTypeChoice]
        self.print_menu_items(menuItems,MenuName)
        
        
    def handle_daemon_bylist_menu(self,action=None): 
        """ Menu function to start TC daemons according to type"""
        print "Handling  " + str(action) +" for " + str( self.selectedList) + " daemons ...Please wait !"    
        self.handle_daemons(action,*self.selectedList)
        self.print_menu_items()

    def handle_daemon_validate_menu(self,action=None): 
        """ Menu function to start TC daemons with validations"""
        print "Handling  " + str(action) +" for " + str( self.selectedList) + " daemons ...Please wait !"    
        self.handle_daemons_with_validation(action,*self.selectedList)
        self.print_menu_items()
                


if __name__ == "__main__":
    Menu=TCDaemonsMenu()
    Menu.activate_menu()    
   
    """
    if   MyTest.check_log_exist(MyTest.get_log_path() ,"*UQ_SERVER1084*.log")== True:
         MyTest.backup_log(MyTest.get_log_path() ,"*UQ_SERVER1084*.log")
    MyTest.handle_daemons('Restart','UQ_SERVER1084')
    if  MyTest.is_str_in_log(MyTest.get_log_path() ,"*UQ_SERVER1084*.log",MyTest.d_name_to_PassStr['UQ_SERVER1084']):
        print "Success"
    else:
        print "Failed"
    
    if MyTest.check_errs_in_log(MyTest.get_log_path(),'ADJ1_UpdateRefreshOnPassivSite_sh.log',"Passiv" )== False:
        print "Successfull"
    """
    
"""
 
    def startDaemonsByType(self,tc_type):
        if tc_type in self.d_type_to_names:
            for name in self.d_type_to_names[tc_type] :
                    start_cmd= self.d_name_to_StartCmd[name]
                    logger.info("Starting " + name +"..." +"with command : " +start_cmd )
                    subproc_popen(start_cmd)
        else:
            logger.error("startDaemonsByType -> no type found for " +str(tc_type)  )
            
    def checkDaemonStatusByType(self,tc_type):   
        statuses={}
        if tc_type in self.d_type_to_names:
            for name in self.d_type_to_names[tc_type] :
                psu_cmd= check_psu_count_cmd(self.d_name_to_PsuString[name])
                logger.info("Checking status with  : " +  psu_cmd)
                data =subproc_popen(psu_cmd)
                if int(str(data[0]).rstrip('\n'))>0:
                    statuses.update({name:'UP'})
                elif int(str(data[0]).rstrip('\n')) ==0:
                    statuses.update({name:'DOWN'})
                else :
                    logger.error("startDaemonsByType -> issue with status " +str(data[0]).rstrip('\n') )
        else:        
            logger.error("checkDaemonStatusByType->  no type found for " +str(tc_type)  ) 
        return statuses

    def stopDaemonsByType(self,tc_type):
        if tc_type in self.d_type_to_names:
            for name in self.d_type_to_names[tc_type] :
                    stop_cmd= kill_by_psu_string_cmd(self.d_name_to_PsuString[name])
                    logger.info("Killing " + name +"..." +"with command : " +stop_cmd )
                    subproc_popen(stop_cmd)
        else:
            logger.error("stopDaemonsByType -> no type found for " +str(tc_type)  )  


    
    def handleDaemonsByType(self,tc_type,action ='Status'): 
        logger.info("Handling daemons by type ...." )
        logger.debug("handleDaemonsByType-> type =" +str(tc_type) + ", action =" +str(action) ) 
        if tc_type in self.d_type_to_names:
            statuses= self.checkDaemonStatusByType(tc_type) 
            self.printDaemonStatuses(statuses)
            if action in ('Stop','Restart') and  'UP' in statuses.values() : 
                self.stopDaemonsByType(tc_type) 
                if action =='Stop':
                    self.handleDaemonsByType(tc_type,'Status') 
                elif action =='Restart':
                    self.handleDaemonsByType(tc_type,'Trigger')                                
            elif action in ('Trigger','Restart')  and 'DOWN' in statuses.values(): 
                self.startDaemonsByType(tc_type)
                self.handleDaemonsByType(tc_type,'Status')
            elif action not in ('Status','Trigger','Stop','Restart'):
                logger.error ("handleDaemonsByType -> Wrong action provided" )        
        else :
            logger.error("handleDaemonsByType -> no type found for " +str(tc_type)  )
"""
