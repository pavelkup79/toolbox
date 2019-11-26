'''
Created on Sep 25, 2018

@author: pavelkup
'''
import logging
import unittest
from Menu import Menu
from server import *
import os
#import cleanFileSystem
from  UnixCmdBuilder import *
#del_logs_cmd,build_kill_cmd,fs_report_cmd, get_cpu_idle_cmd, get_cpu_user_cmd, get_cpu_system_cmd
from SystemHandling import SystemHandler,subproc_popen

logger = logging.getLogger("AutoToolBox")

#envs= {'CRM':"${AUTO_CRM_USER}@${AUTO_CRM_HOST}" , 'OMS' :"${AUTO_OMS_USER}@${AUTO_OMS_HOST}" ,'ABP':""}


######################################################################################################################
#For ABP killing the script need to fix
# For All not calling CRM need to fix
class FileSystemCleaner(SystemHandler):
    
    def __init__(self):
        #self.envs= {'CRM':"${AUTO_CRM_USER}@${AUTO_CRM_HOST}" , 'OMS' :"${AUTO_OMS_USER}@${AUTO_OMS_HOST}",'ABP':""  }
        self.envs = UNIX_SERVERS
    def cleanFileSys(self, numOfDays=1,StopEnv="N",module=None ):
        """Cleans files system from logs and cores with option to bring environment down """
        print "Module "+ module
        if str(module) in self.envs.iterkeys():
            logger.info( "Running cleanFileSystem in " +module + " with parameters : numOfDays=" + str(numOfDays) + " ,StopEnv =" + str(StopEnv) )
            if (str(StopEnv)).upper()=="Y" and self.envs[module] <> "":
                subproc_popen(self.create_ssh_cmd(module,build_kill_cmd(isRemote='Y')))
            elif (str(StopEnv)).upper()=="Y" and self.envs[module] == "":
                self.stop_env()
            elif (str(StopEnv)).upper()<>"N":
                print "PLease provide for" +module + " Y or N if need to stop the environment "
            subproc_popen(self.create_ssh_cmd(module,del_logs_cmd(numOfDays)))
            subproc_popen(self.create_ssh_cmd(module,del_logs_cmd(numOfDays,del_format='core\.[0-9]*')))
            logger.info( "Clean " + module +" is done !!!")  
            return  
        elif str(module) == "All":
            for env in self.envs.iterkeys():
                print("Sending for " + env)
                self.cleanFileSys(numOfDays,StopEnv,env)
        else :
            print("The target system to clean logs is not provided or not exist in the list")
    
    def  fsReport(self):
        """ function is printing and returning as dictionary file system space report in percents per environment for all modules in envs """
        logger.info( "FS Report: ")
        report ={}
        for module in self.envs.iterkeys():
           report.update({module:str((subproc_popen(self.create_ssh_cmd(module,fs_report_cmd())))[0].rstrip("\n"))})
           print ( str(module) + " : " + report[module] +"%")
        print""
        return report
    
    def  cpuReport(self):
        """ function is printing an returning cpu report {module,[user,system,idle]} """
        logger.info( "CPU Report: ")
        report ={}
        for module in self.envs.iterkeys():
          if (module=='ABP'): # As WA will work only with ABP there is issue to call ssh , need to rplace awk with sed
           report.update({module: [str((subproc_popen(self.create_ssh_cmd(module,get_cpu_user_cmd())))[0].rstrip("\n") +"%"),
                                  str((subproc_popen(self.create_ssh_cmd(module,get_cpu_system_cmd())))[0].rstrip("\n") +"%"),
                                   str((subproc_popen(self.create_ssh_cmd(module,get_cpu_idle_cmd())))[0].rstrip("\n") +"%")]})
           print ( str(module) + " : " + report[module][0] +"/" +report[module][1]+"/" + report[module][2])
           print""
        return report
        
    def  memReport(self):
        """ function is printing an returning Memory report {module,[total,free,used]} """
        logger.info( "Memory Report: ")
        report ={}
        for module in self.envs.iterkeys():
          if (module=='ABP'): # As WA will work only with ABP there is issue to call ssh , need to rplace awk with sed
           report.update({module: [str((subproc_popen(self.create_ssh_cmd(module,get_memory_total_cmd())))[0].rstrip("\n")),
                                  str((subproc_popen(self.create_ssh_cmd(module,get_memory_free_cmd())))[0].rstrip("\n")),
                                   str((subproc_popen(self.create_ssh_cmd(module,get_memory_used_cmd())))[0].rstrip("\n") )]})
           print ( str(module) + " : " + "total :"+ report[module][0] +
                   " / " +"free :"+report[module][1]+"/ "+ "used :" + report[module][2])
           print""
        return report        
#    """ 
    def create_ssh_cmd (self,env_to_connect, cmd ):
        if env_to_connect =='ABP':
            logger.debug("create_ssh_cmd for env :" + env_to_connect + ", output->"+ cmd)
            return cmd
        elif env_to_connect in self.envs:
            ssh_cmd = "ssh " +  self.envs[env_to_connect] +' "' + cmd + '"'
            logger.debug("create_ssh_cmd for env :" + env_to_connect+ ", output->"+ ssh_cmd )
            return ssh_cmd
        else:
            logger.error("Can't create ssh connection , environment option is not valid  " +str(env_to_connect) )
#    """   
    """ 
    def create_ssh_cmd (self,env_to_connect, cmd ):
        if env_to_connect =='ABP':
            logger.debug("create_ssh_cmd for env :" + env_to_connect + ", output->"+ cmd)
            return cmd
        elif env_to_connect in self.envs:
            ssh_cmd = "ssh -t -o LogLevel=QUIET " +  self.envs[env_to_connect] +' "' + cmd + '"'
            logger.debug("create_ssh_cmd for env :" + env_to_connect+ ", output->"+ ssh_cmd )
            return ssh_cmd
        else:
            logger.error("Can't create ssh connection , environment option is not valid  " +str(env_to_connect) )
    """
    #def format_ssh_cmd format 
     
    def __del__(self):   
        #logger.debug("Closing the progrumm and killing cleanFileSystem instances ")  
        #subproc_popen (build_kill_cmd ("N","cleanFileSystem.py"))
        pass
         
        
###############################################MENU#######################################################################    

        
class cleanFileSystemMenu(FileSystemCleaner,Menu):  
    def __init__(self):
        self.MenuName="Clean File System "
        self.IsMenuActive=True
        self.menuItems= [ 
            {"ABP": self.num_of_days_menu },
            {"CRM": self.num_of_days_menu },
            {"OMS": self.num_of_days_menu },
            {"All": self.num_of_days_menu},
            {"FS Report":self.fs_report_menu},
             {"CPU Report":self.cpu_report_menu},
             {"Memory Report":self.memory_report_menu},
             {"Back": self.back_menu},
             {"Exit": self.exit_menu}
            ]


    def fs_report_menu (self,option=None):
        """ Menu get file system usage in % for all modules in envs  """
        os.system('clear')
        print "Creating FS report "
        FileSystemCleaner().fsReport()
          
    def cpu_report_menu (self,option=None):
        """ Menu get CPU usage user/system/idle per module in % for all modules in envs  """
        os.system('clear')
        print "Creating CPU report "
        FileSystemCleaner().cpuReport()    
        
    def memory_report_menu (self,option=None):
        """ Menu get memory  usage total/free/used   """
        os.system('clear')
        print "Creating Memory report "
        FileSystemCleaner().memReport()   
                
                
    def stop_env_menu(self, server,num_of_days=1):
        """ Menu gets input from num_of_days_menu,gets stop_env option from user and the call to clean_file_system_menu  """
        print "Kill " + str(server) + " ? [Y/N] [ Default : 'N' ]"
        stop_env = raw_input(">> ")   
        #print stop_env, type(stop_env), len(str(stop_env))    
        if (str(stop_env)).upper()=="Y" or (str(stop_env)).upper()=="N":
            self.clean_file_system_menu(num_of_days, stop_env ,server)  
        elif stop_env=="":
            self.clean_file_system_menu(num_of_days, stop_env="N" , server=server)
        else :
            print "Invalid input,please provide for " +server + " Y or N if need to stop the environment "
            self.stop_env_menu(server,num_of_days)
        
    def num_of_days_menu(self,server):
        print "Select number Of days to clean logs on " +str(server) +" [ Zero will delete also current logs ] : [ Default : '1' ] " 
        num_of_days = raw_input(">> ")  

        if num_of_days == ""  :
            print "Running stop_env_menu with default number_of_days =1"
            self.stop_env_menu(server)
        elif int(num_of_days < 0) or not num_of_days.isdigit() :
            print "No valid value of num_of_days"
            self.num_of_days_menu(server)
        else :
            print "Running stop_env_menu with number_of_days =" +(str(num_of_days))
            self.stop_env_menu(server,num_of_days)

        
      
    def clean_file_system_menu(self,num_of_days,stop_env ,server):  
        """function gets input from stop_env_menu and call to FileSystemCleaner.cleanFileSys"""   
        os.system('clear')   
        print "cleaning logs for server " +str(server) +" starting from " + str(num_of_days) +" days back with stop_env option =" +str(stop_env)  
        FileSystemCleaner().cleanFileSys(num_of_days,stop_env ,server) 
     
####################################################UNIT TEST############################################################

class TestcleanFileSystemMenu(unittest.TestCase):

    def test_activate_menu(self):
        logger.debug( "++++++++++++++++++++++++++Test cleanFileSys Main Menu+++++++++++++++ ")
        Menu= cleanFileSystemMenu()
        Menu.activate_menu()
        





if __name__ == "__main__":
    #unittest.main()
    
    Menu= cleanFileSystemMenu()
    Menu.activate_menu()
