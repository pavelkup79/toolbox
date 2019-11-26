#from OraDBConnect import OracleDBConnector
'''
@author: pavelkup
'''
import logging
import platform
import os
import string
from server import *
from SystemHandling import SystemHandler,subproc_popen,print_data
from UnixCmdBuilder import sqlplus_query, clean_mro_queue_cmd
from Menu import Menu
from DaemonBase import DaemonHandlerBase
from ABPDaemonData import DaemonData

logger = logging.getLogger("AutoToolBox")
NO_OUTPUT=' 1>/dev/null 2>/dev/null'
db =ABP_DB


class ABPDaemonsHandler(DaemonHandlerBase):
    def __init__(self):
        DaemonHandlerBase.__init__(self)
        #d_name_to_StartCmd - dict {"daemon name":"StartCommand"} when StartCommand = command +params from l_DaemonData
        #DaemonData -list external dict that contain all related info per daemon
        #d_type_to_names  -dict  { "type" :["daemonName1","daemonName2"]} 
        #d_name_to_PsuString  - dict  { "name" :"psu_String"} 
        
        self.d_DaemonsData=DaemonData# get from external module
        self.d_name_to_StartCmd ,self.d_name_to_PsuString,self.d_name_to_PassStr=self.get_all_ABPdata()

    
    
    def get_all_ABPdata(self): 
        name_to_StartCmd={}
        name_to_PsuString={}
        name_to_PassStr={}
        for daemon in self.d_DaemonsData:
            name_to_StartCmd.update({daemon :  self.d_DaemonsData[daemon]['START_COMMAND']+ NO_OUTPUT}) 
            name_to_PsuString.update({daemon : self.d_DaemonsData[daemon]['PSU_STRING']}) 
            name_to_PassStr.update({daemon : self.d_DaemonsData[daemon]['LOG_PASS_STR']}) 
        return   name_to_StartCmd ,name_to_PsuString,name_to_PassStr
    
    def clean_trb(self):
       logger.info("Cleaning TRB tables... ")
       TRB_QRY='''delete from TRB1_AMC_HISTORY;
       delete from TRB1_AUDIT_INTERVAL;
       delete from TRB1_ENG_CNTRL;
       delete from TRB1_ERR_DEPENDENT;
       delete from TRB1_IMP_PERIOD;
       delete from TRB1_MEMBER_ADMIN;
       delete from TRB1_MONITOR_INFO;
       delete from TRB1_QUE_CNTRL;
       delete from TRB1_RECV_DATA;
       delete from TRB1_SUB_APPL_CNTRL;
       delete from TRB1_THR_CNTRL;
       delete from TRB1_USER_CONFIG;
       delete from TRB1_SUB_APPL_CNTRL;
       delete from TRB1_ERR_DEPENDENT;
       commit;'''
       data= subproc_popen(sqlplus_query(TRB_QRY,db,set_echo='On'))
       print_data(data)
       
       
    def clean_mro(self):
       logger.info("Stopping AMC and MRO....")
       self.handle_daemons('Stop','AMC_SERVER','MRO')
       logger.info("Cleaning MRO queue ....")
       subproc_popen(clean_mro_queue_cmd())
       logger.info("Starting AMC ,AMC Daemon Manager and MRO ....")
       self.handle_daemons('Trigger','AMC_SERVER','AMC_DAEMON_MANAGER','MRO')
    
    def update_ar1_control(self, proc_name ='AR1BILINTER'):
       AR1_CNTRL_QRY= '''update ar1_control shutdown_flag='Y' where  CONTROL_APPLICATION_ID ='AR1BILINTER';commit;'''
       data= subproc_popen(sqlplus_query(AR1_CNTRL_QRY,db,set_echo='On'))
       print_data(data)
    
    

     
     
     
     
def clean_mro_queue(self):
    data = subproc_popen(clean_mro_queue_cmd())
    
    
    
       
        
               
        
    
    
    
    
    
    
################################################################################################################    
######################################### MENU ###################################################
##############################################################################################
       
class ABPDaemonsMenu(ABPDaemonsHandler,Menu):  
    def __init__(self):
        ABPDaemonsHandler.__init__(self)
        #super(TCDaemonsHandler, self).__init__()
        self.MenuName="ABP Daemons Menu"
        self.selectedItemToAction={"ES Rating":"ES_RB" ,"ES Guiding":"ES_FR","File2E":"F2E","DB2E":"DB2E","UQ - Usage Query":"UQ_SERVER",
                              "Dispatcher":"DSP","RRP - Ongoing Rerate" :"RRP_OG" ,"ELA":"ELA","GAT2E":"GAT2E",
                              "UH Incr - Rating":"UHI_RT","UH Incr - Guiding": "UHI_GD","UH Full - Rating":"NotDefined" ,"Show ABP Daemons status":"NotDefined" ,"All TC Daemons":"All TC Daemons"
                              }
        self.TCType=None
        self.IsMenuActive=True
        self.ABPAllList= self.d_name_to_StartCmd.keys()
        self.selectedList =[]#  list to populate  according to user selection 
        self.menuItems= [ 
            {"Show ABP commands": self.get_all_ABPcommands_menu },
            {"Show ABP Daemons status": self.handle_daemon_bylist_menu },
            {"Clean TRB dependencies tables":self.clean_trb_menu},
            {"Clean MRO Queue": self.clean_mro_menu},
            {"AMC_SERVER": self.abpDaemonsOperations_menu},
            {"AMC_DAEMON_MANAGER": self.abpDaemonsOperations_menu},
            {"MRO": self.abpDaemonsOperations_menu},
            {"BTLQUOTE": self.abpDaemonsOperations_menu},
            {"BTLSOR": self.abpDaemonsOperations_menu},
            {"TRB": self.abpDaemonsOperations_menu},
            {"INVOKER1": self.abpDaemonsOperations_menu},
            {"INVOKER2": self.abpDaemonsOperations_menu},
            {"INVOKER10": self.abpDaemonsOperations_menu},
            {"RQSLSNR": self.abpDaemonsOperations_menu},
            {"AR1BILINTER": self.abpDaemonsOperations_menu},
            {"Back": self.back_menu},
            {"Exit": self.exit_menu}
            ]
        
    def abpDaemonsOperations_menu(self,DaemonChoice): 
        """ Menu to start stop or get status for preselected daemons""" 
        MenuName="ABP Daemons - Operations"
        self.selectedList=[]
        self.selectedList.extend([DaemonChoice])
        menuItems= [ 
            {"Status": self.handle_action_for_selected_daemon_menu},
            {"Stop": self.handle_action_for_selected_daemon_menu},
            {"Trigger": self.handle_action_for_selected_daemon_menu},
            {"Restart": self.handle_action_for_selected_daemon_menu},
            {"Back": self.activate_menu},
            {"Exit": self.exit_menu}]
        os.system('clear')
        print "Please select operation for " + DaemonChoice
        self.print_menu_items(menuItems,MenuName)       

    def get_all_ABPcommands_menu (self,option=None):
        """ Menu get all ABP daemons start commands  """
        MenuName ="Showing all start commands for ABP daemons "
        os.system('clear')
        #TCDaemonsHandler().print_all_TC_commands()
        self.print_all_commands(**self.d_name_to_StartCmd)
        self.print_menu_items(menuName=MenuName)
    
            
    def handle_action_for_selected_daemon_menu(self,action=None): 
        """ Menu function to show status for all ABP daemons"""
        print "Handling  " + str(action) +" for  daemons ...Please wait !"    
        self.handle_daemons(action,*self.selectedList)
        self.print_menu_items()  
  
    def handle_daemon_bylist_menu(self,action=None): 
        #Menu function toshow status for all ABP daemons
        print "Handling  " + str(action) +" for  daemons ...Please wait !"    
        self.handle_daemons('Status',*self.ABPAllList)
        self.print_menu_items()  

        
    def clean_trb_menu(self,option=None): 
        self.clean_trb()
        self.print_menu_items()   
        
    def clean_mro_menu(self,option=None): 
        self.clean_mro()
        self.print_menu_items()               

if __name__ == "__main__":
    MyMenu=ABPDaemonsMenu()
    MyMenu.activate_menu()
    #MyABP.start_daemons('BTLSOR')
    #data=subproc_popen('AMC_API_USE=N',shell=False)
    #print data