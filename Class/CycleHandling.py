'''
@author: pavelkup
'''
import logging
import time
from server import *
from SystemHandling import SystemHandler,subproc_popen,print_data,wait_db_update
from UnixCmdBuilder import sqlplus_query, clean_mro_queue_cmd
from Menu import Menu
from LDHandler import  set_logical_date

from ABPDaemons import ABPDaemonsHandler
from JobHandling_Class import JobHandling
logger = logging.getLogger("AutoToolBox") 
db = ABP_DB
  
class CycleHandler(ABPDaemonsHandler,JobHandling):
    def init(selfself):
       ABPDaemonsHandler.__init__(self)
       DefDay="select to_char(sysdate,'DD') from dual;"
       DefMonth="select to_char(sysdate,'MM') from dual;" 
       DefYear ="select to_char(sysdate,'YYYY') from dual;"
       
    def run_cycle_maint(self,date=None,CleanInd="Y"):
        """ running cycle maintanence , when indicator is Y will clean existing Cycle instances from tables
        when date is None will set LD to be sytemDate"""
        ClnTRB="""delete from trb1_pub_log where GENERAL_DATA_C like '%NEW_CYCLE_INSTANCE%'
                  OR GENERAL_DATA like '%NEW_CYCLE_INSTANCE%';
                  delete from trb1_mst_log where GENERAL_DATA_C like '%NEW_CYCLE_INSTANCE%'
                  OR GENERAL_DATA like '%NEW_CYCLE_INSTANCE%';
                  delete from trb1_sub_log where GENERAL_DATA_C like '%NEW_CYCLE_INSTANCE%' 
                  OR GENERAL_DATA like '%NEW_CYCLE_INSTANCE%';
                  delete from trb1_sub_errs where GENERAL_DATA_C like '%NEW_CYCLE_INSTANCE%' 
                  OR GENERAL_DATA like '%NEW_CYCLE_INSTANCE%';
                  commit;"""
                  
        ClnCycleInstData="""delete ADJ1_CYCLE_STATE;
                            delete BL1_CYCLE_CONTROL;
                            delete CM1_CYCLE_INSTANCE;
                            delete  RPL1_CYCLE_INSTANCE;
                            commit;"""
                            
        InstanceCount="""select trim(count(*)) from bl1_cycle_control where cycle_code=(select CYCLE_CODE 
                          from bl1_cycle_code where FREQUENCY='M' and rownum <=1)  and trunc(END_DATE) >= 
                           (select distinct(logical_date) from logical_date 
                            where LOGICAL_DATE_TYPE='B' and EXPIRATION_DATE is null);"""   
        CheckTRBErrs ='''select count(*) from TRB1_SUB_ERRS where GENERAL_DATA_C like '%NEW_CYCLE_INSTANCE%'
          or GENERAL_DATA like '%NEW_CYCLE_INSTANCE%';'''
        GetTRBErrs ='''select ERROR_TEXT1  from TRB1_SUB_ERRS where GENERAL_DATA_C like '%NEW_CYCLE_INSTANCE%'
          or GENERAL_DATA like '%NEW_CYCLE_INSTANCE%';'''
        CheckCM="""Select count(*) from CM1_CYCLE_INSTANCE"""
        CheckADJ="""Select count(*) from ADJ1_CYCLE_STATE"""
                            
        ValBTLSOR =""""""              
                  

        self.handle_daemons('Stop','BLBDI');
        #self.stop_daemons('BL1CYCLEMAINT') # need to update function to woth without PSU string or to write new 
        logger.info("Cleaning TRB tables....")
        data = subproc_popen(sqlplus_query(ClnTRB,db,set_echo='On')); 
        print_data(data);
        if (CleanInd=='Y'):
            logger.info("Cleaning all Cycle instances ....")
            data= subproc_popen(sqlplus_query(ClnCycleInstData,db,set_echo='On'));
            print_data(data);
        logger.info("Updating Logical Date ....")
        if date:   
            set_logical_date(date,'N')
        else:
            set_logical_date('sysdate','N')#will set to sysdate     
                           
        self.handle_daemons('Trigger' ,'AMC_SERVER', 'AMC_DAEMON_MANAGER' , 'TRB', 'INVOKER1' ,'INVOKER2' ,'INVOKER10' , 'BTLSOR' ,'BTLQUOTE')
        self.RunJob('BL1CYCLEMAINT','ENDDAY');
        #Check invoicing is updated
        if wait_db_update(InstanceCount,db) < 2:
            logger.error("BL1_CYCLE_CONTROL was not updated ,Check that Trx 2006 was Processed")
            return
        else:
            logger.info("BL1_CYCLE_CONTROL is updated!")
        time.sleep(10)#waiting for BTLSOR to finish all entries 
        logger.info("Checking CM tables..")
        if wait_db_update(CheckCM,db) < 2:
            logger.error("CM1_CYCLE_INSTANCE is not updated check TRB Tables")
            return
        else:
            logger.info("CM tables are updated.... " + ( subproc_popen(sqlplus_query(CheckCM,db)) )[0].rstrip('/n') +" entries found" )
        logger.info("Running ADJ1CYCMNTEOD ...")
        self.RunJob('ADJ1CYCMNTEOD','ENDDAY');
        #if wait_db_update(InstanceCount,db) < 2:
            
        logger.info("Wating for requests to be processed...")
        #CheckADJ is update is Updated 
        if wait_db_update(CheckADJ,db) <2:
            logger.error("ADJtable is not populated ,check TRB for 3017")
            logger.error( ( subproc_popen(sqlplus_query(CheckADJ,db)) )[0].rstrip('/n') )
            return
        else:
            logger.info("ADJ1_CYCLE_STATE is populated .... " + ( subproc_popen(sqlplus_query(CheckADJ,db)) )[0].rstrip('/n') +" entries found" )       

        # check no errors in TRB 
        if wait_db_update(CheckTRBErrs,db,timeout=0) > 0:
            logger.error("TRB error is detected for Cycle Maintanence")
            logger.error( ( subproc_popen(sqlplus_query(GetTRBErrs,db)) )[0].rstrip('/n') )
            return
        else:
            logger.info("No TRB Errors detected.... ")
        
        
        
    
######################################################################################################    
##########################################     MENU     ###############################################
####################################################################################################

class CycleHandlerMenu(Menu,CycleHandler):
    def __init__(self):
        CycleHandler.__init__(self)
        #super(TCDaemonsHandler, self).__init__()
        self.MenuName="CycleMaintanence Menu"  
        self.IsMenuActive=True
        self.menuItems= [ 
            {"Run Cycle Maintanence": self.run_cycle_maint_menu },
            {"Back": self.back_menu},
            {"Exit": self.exit_menu}
          ]
            
    def run_cycle_maint_menu (self,option = None ):  
        self.run_cycle_maint();
         
  
  
  
if __name__ == "__main__":
    Menu= CycleHandlerMenu()
    Menu.activate_menu()      
        
        
        
  
