'''
Created on Sep 13, 2018

@author: pavelkup
'''
import platform
import subprocess
import unittest
from UnixCmdBuilder import build_find_cmd,build_kill_cmd, del_logs_cmd,find_last_folder_cmd,sqlplus_query
import logging
import time
#from LoggerConf import dictLogConfig

#open Issues
#to add few criteria for fine  or exclude?
#why need \; after exec?
# what is the tag in kill command , what is the kill command for ABP
logger = logging.getLogger("AutoToolBox")


class SystemHandler():


    def __init__(self):
        if self.check_platform()<> "Linux":
            print ">>> " + self.platform  + "Operational System is not supported"
            return False          
    
    def delete_logs(self, numOfDays=1, logs_format='*.log*',excl_format='*xpi*',   path='. '):
        logger.debug(">>> --------running delete_logs function-----------") 
        cmd = del_logs_cmd( numOfDays, logs_format, excl_format  , path ) 
        data = subproc_popen(cmd)
        return True
        #self.find_files (numOfDays , logs_format, excl_format ,  'rm' , path, output)
        #return True
    
    def stop_env(self):
        cmd =build_kill_cmd()
        logger.debug(">>>Running stop_env command: " + str(cmd)) 
        subproc_popen(cmd)
        return True
            
    def check_platform(self):
        return platform.system()   
        
    def  __del__(self): 
        pass
    
def find_last_direcory(folder_name, path="") :
    #find_last_folder_cmd
    pass
    
#################################################UNix#################################################   
def subproc_popen(cmd=None,shell =True):
    if cmd:
        logger.debug("subproc_popen running :" + str(cmd)) 
        p= subprocess.Popen(cmd,stdout =subprocess.PIPE ,shell=shell)
        #code=p.wait()
        #if code <> 0 :
            #logger.error("subprocess.Popen method for command :" + str(cmd)+" Failed with code: " + str(code) ) 
        data= p.communicate()
        #print_data(data)
        return data
    else:
        logger.error("Missing input command for subprocess.Popen method:" + str(cmd)) 
        return 
    
################################################DB####################################################    
def wait_db_update(query,db,timeout= 120):
    isDbUpdated=False
    timer=0 
    count=0
    while isDbUpdated ==False and timer <= timeout:
        data=subproc_popen( sqlplus_query(query ,db) )
        count = int( str( data[0]).rstrip('\n')  )            
        if count > 0:
            isDbUpdated = True
        elif count == 0:
            time.sleep(1)
            timer+=1            
    return count
               
def run_sql(sql_cmd,db):  
    data =subproc_popen(sqlplus_query(sql_cmd,db) )  
    return data   
               
def print_data(data):   
    for row in data:
        row =str(row)
        if row.rstrip("\n") <> 'None' and row.rstrip("\n") <> "":
            logger.info(row)
def find_files ( mtime=0,maxdepth="", find_format='*.log*' ,excl_format=None , exec_cmd = None , path='. ', output="N"):
    cmd = build_find_cmd( mtime,maxdepth, find_format, excl_format , exec_cmd , path , output) 
    logger.debug("Checking Files with command : " + str(cmd))
    data = subproc_popen(cmd)
    return data   
      
####################################################UNIT TEST############################################################


class TestSystemHandler(unittest.TestCase):
    
    def setUp(self):
        logger.debug("-------------------running UnitTest for SystemHandling-----------") 
         
    """

    def test_find_files(self):
        
        #print (" test_find_files  is running ")
        #create test file  before delete ,delete file according to format, count files after delete 
        data =subproc_popen("find . -type f -iname 'CleanFileSystem.test' | wc -l")
        if int(data[0].rstrip("\n"))  > 1 :
            subprocess.call("rm -r 'CleanFileSystem.test'; 1>/dev/null 2>/dev/null" ,shell=True)
        data =subproc_popen("find . -type f -iname 'CleanFileSystem.test' | wc -l")
        #p=subprocess.Popen("find . -type f -iname 'CleanFileSystem.test' | wc -l",stdout =subprocess.PIPE ,shell=True)
        #data = p.communicate()
        num_of_files_bf_cre = data[0].rstrip("\n")
        #print("test_find_files num Of Files before creation :"+ num_of_files_bf_cre)
        self.assertEqual(num_of_files_bf_cre , '0')
        subproc_popen("touch CleanFileSystem.test" )
        self.assertEqual(SystemHandler().find_files(find_format='*CleanFileSystem.test'),True)
        data =subproc_popen("ls *CleanFileSystem.test* | wc -l")
        num_of_files_af_cre = data[0].rstrip("\n")
        #print("test_find_files num Of Files after creation :"+ num_of_files_af_cre)
        self.assertEqual(num_of_files_af_cre , '1')

    """
    
    def test_delete_logs(self):
        logger.debug("-------------------running UnitTest for SystemHandling->delete_logs -----------") 
        #print ("test_delete_logs  is running ")
   
        #create test file  before delete ,delete file according to format, count files after delete 
        data =subproc_popen("find . -type f -iname 'CleanFileSystem.test' | wc -l")
        logger.debug( data) 
        if int(data[0].rstrip("\n"))  >= 1 :
            logger.debug("UnitTest deleting CleanFileSystem.test before test") 
            subprocess.call("rm -r 'CleanFileSystem.test'; 1>/dev/null 2>/dev/null" ,shell=True)
        logger.debug("UnitTest creating new CleanFileSystem.test ") 
        subprocess.Popen("touch CleanFileSystem.test;chmod 777 CleanFileSystem.test" ,shell=True)
        logger.debug("UnitTest counting CleanFileSystem.test before delete_logs method  ") 
        data=subproc_popen("find . -type f -iname 'CleanFileSystem.test' | wc -l")
        #print "Data =" + str(data)
        num_of_files_bf_del = data[0].rstrip("\n")
        #print("num Of Files before deleting :"+ num_of_files_bf_del)
        self.assertEqual(num_of_files_bf_del , '1')
       
        self.assertEqual(SystemHandler().delete_logs(0,logs_format='*CleanFileSystem.test'),True)
        logger.debug("UnitTest counting CleanFileSystem.test befor delete_logs method  ") 
        p=subprocess.Popen("find . -type f -iname 'CleanFileSystem.test' | wc -l",stdout =subprocess.PIPE ,shell=True)
        data = p.communicate()
        num_of_files_af_del = data[0].rstrip("\n")
        #print("number Of Files after deleting :"+ num_of_files_af_del)
        self.assertEqual(num_of_files_af_del , '0')
        #subprocess.call("rm -r 'CleanFileSystem.test*'; 1>/dev/null 2>/dev/null" ,shell=True)
       
##################################################UNIT Test ####################################################
if __name__ == "__main__":
    unittest.main()
  
    
