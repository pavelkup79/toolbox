
'''
@author: pavelkup
'''
import unittest
from LoggerConf import dictLogConfig
import logging

#import logging.config


'''
Created on Sep 19, 2018

@author: pavelkup

'''
NO_OUTPUT=' 1>/dev/null 2>/dev/null'

logger = logging.getLogger("AutoToolBox")

#################################################################################################



################################################## df ###########################################################################################################
# need to add validations to set_path function

def fs_report_cmd():
   return "cd;df -k . | tail -1 | sed -e 's/%.*$//g' -e 's/^.* //'"

##################################### FIND Command ###################################################################

def del_logs_cmd( mtime=1 , maxdepth ="",del_format="*.log*",excl_format='*xpi*' , path='.'):
    """build_del_logs_cmd- function builds Unix command in format of 'find . -type f -iname '*.log' -mtime n -exec rm {} \; 1>/dev/null 2>/dev/null"""
    if ('log' in del_format or 'core' in del_format or 'test' in del_format) and str(del_format)>3  :
        del_cmd =build_find_cmd(mtime,maxdepth ,del_format ,excl_format,'rm' ,path)
        logger.debug( del_logs_cmd.__name__ + "->output: " +  del_cmd)
        return del_cmd
    else:
        logger.error( del_logs_cmd.__name__ + "->File format to delete is not safe: " +  del_format)   
        return False

#last added and not tested maxdepth
def build_find_cmd( mtime=0  ,maxdepth ="",find_format=None,excl_format=None , exec_cmd = None , path='.', output="N"):
    """build_find_cmd - function builds Unix command in format of 'find . -type f -iname '*.log' -mtime n -exec cmd {} \; 1>/dev/null 2>/dev/null"""
    find_cmd ="find " + set_path(path) +  set_maxdepth(maxdepth)+ set_file_format(find_format) + set_excl_format(excl_format) + set_mtime(mtime)  +  set_exec_cmd(exec_cmd)+";" + set_output(output)
    logger.debug( build_find_cmd.__name__ + "->output: " +  find_cmd)
    return find_cmd

def find_last_folder_cmd(folder_name ,maxdepth=""):
    return 'find ES_FR1051' +set_maxdepth(maxdepth)+' -type d -name "*" | sort -n | grep -v AutoBackup | tail -1'
    
"""
def build_find_cmd( mtime=0  ,find_format=None,excl_format=None , exec_cmd = None , path='.', output="N"):
    find_cmd ="find " + set_path(path) + set_file_format(find_format) + set_excl_format(excl_format) + set_mtime(mtime)  +  set_exec_cmd(exec_cmd)+";" + set_output(output)
    logger.debug( build_find_cmd.__name__ + "->output: " +  find_cmd)
    return find_cmd
"""

def set_mtime(numOfDays):
    if not str(numOfDays).isdigit:
            logger.error("set_mtime -Bad value of numOfDays=" +str(numOfDays)+", should be integer")
            raise ValueError("set_mtime -Bad value of numOfDays= " +str(numOfDays)+", should be integer")
    elif(int(numOfDays) == 0 or not numOfDays or numOfDays==None):
        mtime = ""
    elif (int(numOfDays) > 0) :
        mtime = " -mtime +" + str(int(numOfDays)-1) 
    else :
        logger.error( ">>> set_mtime -Bad value of numOfDays=" + str(numOfDays) +  ". Value should be positive.")
        #raise ValueError(">>> set_mtime -Bad value of numOfDays=" + str(numOfDays) +  ". Value should be positive.")
    return mtime  

def set_maxdepth(maxdepth): 
    if maxdepth=="":
        return "" 
    else :
        return " -maxdepth " +str(maxdepth)
    
def set_output(output):
    if output=="N" :
        return NO_OUTPUT
    else:
        return ""

def set_excl_format(excl_format):
    if not excl_format :
        return ""
    else:
        return " -not -path  '*AutoToolBox.log*'" +" -not -path "  + "'"+ str(excl_format) + "'"
    

def set_file_format(find_format):
    if not find_format :
        return ""
    else:
        return " -type f -iname "  + "'"+ str(find_format) + "'"
    
def set_path(path):
    if not path: 
        return "."
    else:
        return path
    
def set_exec_cmd(exec_cmd):
    if not exec_cmd :
        return ""
    elif exec_cmd in ['rm']:        
        return " -exec " + exec_cmd +" {} \\"
    else :
        raise ValueError()
    #">>> set_exec_cmd -command is not supported: " + str(exec_cmd)
        return False
################################################KILL COMMAND ##################################################################

#need to replace 'grep -v 'CleanFileSystem. with variable)
# may be need to replace awk with sed  an remove remote flag because awk has issues with ssh
#last added ; before No_OUTPUT in case of 'N" (need to test)
def build_kill_cmd (isRemote="N",proc_name=None):  
    """function returns Unix command to filter and to kill ALL processes excluding one that contains CleanFileSystem.  """
    if (isRemote =="N" and proc_name==None):
        cmd="ps -fu $USER | grep -v $$ | grep -v '\-ksh' | grep -v 'ssh' | grep -v '/bin/sh'| grep -v 'CleanFileSystem.' | grep -v 'MainMenu.py' | grep -v 'grep'|   grep -iv 'sshd' | grep -v PID | awk '{print $2}'| xargs kill -9 " 
        
    elif (isRemote =="Y" and proc_name==None):
        cmd="kill -9 -1;"
    elif (isRemote =="N" and proc_name is not None):
        cmd="ps -fu $USER | grep -v $$ | grep -v '\-ksh' | grep -v 'ssh' | grep -v '/bin/sh'| grep -v "+"'"+ proc_name +"'" +" | grep -v 'grep'|   grep -iv 'sshd' | grep -v PID | awk '{print $2}'| xargs kill -9 "
        #cmd="ps aux | grep -v 'root' |grep -v 'oracle' | grep -v 'grep' |  grep '" + proc_name  + "' | grep -v 'grep'| grep -v PID | awk '{print $2}'| xargs kill -9 "
    logger.debug(">>>build_kill_cmd : output->" + cmd + NO_OUTPUT)
    return cmd + NO_OUTPUT

def build_kill_daemons_cmd() :
    """ function will create unix commanse do kill allTC daemons"""
    pass #mot ready

def kill_dmn_cmd(PID=None):
    """function gets PID and return Unix command to kill process"""
    if PID:
      return "kill-9 " + str(PID) + NO_OUTPUT
    else :
      logger.error(">>>kill_dmn_cmd : Missing PID for kill  daemon")

def kill_by_psu_string_cmd(psu_string):
    psu_string = str(psu_string)
    if psu_string <> None  and psu_string <> "" and len(psu_string)>3:
      return 'kill -9 `ps -fu $USER | grep -i "' + str(psu_string) +'''" | grep -v grep | grep -v echo  |grep -v $$ | awk '{print $2}'`'''
    else :
        logger.error("kill_by_psu_string_cmd -> Invalid psu_string ")
##################################   PSU  ##########################################################
def get_PID(psu_string=None):
    """function gets psu_string and return daemon PID according to the string"""
    return '''`ps -fu $USER | grep -i "''' + str(psu_string) +'''" | grep -v grep | grep -v echo  |grep -v $$ | awk '{print $2}' | tail -1`'''


def check_psu_count_cmd(psu_string):
    """function gets psu_string and return psu count """
    logger.debug(">>>Running check_psu_count_cmd with:" +str(psu_string))
    if (psu_string==None or psu_string==''):
        logger.error(">>>get_PID : psu_string is empty")   
    else:  
        return "ps -fu $USER  | grep '"+str(psu_string) +"' | grep -v $$ |grep -v grep| wc -l"

############################################## grep #########################################################
def grep_str_cmd(*string_list ):
    """ function gets list of string and concatinate to grep command with -e option"""
    str_list = "grep -A 2 -B 2"
    for item in string_list :
        if len(item) > 2 :
            str_list+=' -e "' +str(item) + '"'
        else :
            logger.error("String value to fine in the log is too short or not valid :"+ str(item))
    logger.debug("grep_str_cmd -> cmd: " + str_list + NO_OUTPUT)
    return str_list + NO_OUTPUT
    
############################################# cat ########################################################  
def cat_str_in_file(grep_cmd,file_format='*.log*', count ='Y' ):          
    """ function gets file_format and grep option (cmd)   and create apply cat file_format  |grep - str"""
    logger.debug("Running cat_str_in_file with grep_cmd =: " + grep_cmd +" and file_format =:" +file_format)
    cat_cmd="cat  "
    if count=='Y':
        str_count = " | wc -l"
    else :
        str_count = ""
    if 'grep' not in str(grep_cmd) or len(grep_cmd) < 7:
       logger.error("cat_str_in_file -> Invalid grep_cmd argument ")
    else:
       cat_cmd =cat_cmd +file_format + NO_OUTPUT+' | '+ grep_cmd +str_count
       logger.debug("cat_str_in_file ->cmd: " + cat_cmd)
       return cat_cmd

############################################## TOP command ########################################## 
def get_cpu_idle_cmd():
    return "top -n1 |grep Cpu| awk '{print $8}'"# top -n1 |grep Cpu |cut -d " " -f6
def get_cpu_user_cmd():
    return "top -n1 |grep Cpu| awk '{print $2}'"# top -n1 |grep Cpu |sed
def get_cpu_system_cmd():
    return "top -n1 |grep Cpu| awk '{print $4}'"


 
def  get_memory_total_cmd():
    return "top -n1 |grep 'KiB Mem'|awk '{print $4}'"
    #return 'top -n1 |grep Mem'
def  get_memory_used_cmd():
    return "top -n1 |grep 'KiB Mem'|awk '{print $6}'"
def  get_memory_free_cmd():
    return "top -n1 |grep 'KiB Mem'|awk '{print $8}'"




####################################Special CASES #########################################################
 
def  clean_shared_memory_cmd():
    return 'maainfo -rm <<<"f"' + NO_OUTPUT 

def  clean_mro_queue_cmd():
     return '''for q in $(ipcs -q |grep $USER|tr -s ' '|cut -d ' ' -f 2 ) 
              do 
              ipcrm -q $q 
            done'''
    
def check_file_exist_cmd(file_name):
    #return "[ -f "+str(file_name)+" ] && echo 'Pass' || echo 'Fail'"
    return "[ -f "+str(file_name)+" ] && echo 'Pass' || echo 'Fail'"
    

    
"""    
def build_kill_cmd (isRemote="N",process=None):  
    if (isRemote =="N" and process==None):
        cmd="kill -9 `ps -fu $USER | grep -v $$ | grep -v '\-ksh' | grep -v 'ssh' | grep -v '/bin/sh'| grep -v 'CleanFileSystem.' |grep -v 'grep'|   grep -iv 'sshd' | grep -v PID | awk '{print $2}' `" + NO_OUTPUT
        logger.debug(">>>build_kill_cmd : output->" + cmd)
        return cmd
    elif (isRemote =="N" and process<> None):
        cmd        

def create_file_cmd(file_name,path):
    return "touch " + file_name
"""
#ssh -t -o LogLevel=QUIET   ${AUTO_CRM_USER}@${AUTO_CRM_HOST} "top -n1 |grep Cpu "| awk '{print $8}' 
#ssh -t -o LogLevel=QUIET   ${AUTO_CRM_USER}@${AUTO_CRM_HOST} "top -n1 |grep Cpu | awk '{print \$8}'"
def create_ssh_cmd(user , host): 
    if str(user).length < 4  or str(host).length < 4 or user ==None  or  host==None:
        logger.error( ">>>create_ssh_cmd -Not valid user or password provided for ssh connection: user=" +str(user) +" host=" ++str(host))
    return "ssh " + user + "@" +host

def sqlplus_query(query,db,set_echo='Off' ):
    if set_echo =='On':
        setConfs ='"'
    elif set_echo =='Off':
        setConfs ='''"set echo off head off verify off feed off pages 0;\nset linesize 4000;\n'''
    else:
        logger.error("sqlplus_query ->Wrong parameter set_echo ")
    query=query.rstrip(';')
    sql_cmd  ="echo "+setConfs  + query + ';"' +" | sqlplus -S " + db['dbUser']+"/" +db['dbPass'] +"@" +db['dbInstance']
    logger.debug("sqlplus_query-> " + sql_cmd )
    return sql_cmd
  
    
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
        
###########################################  UNIT TEST ###########################################################

class TestUnixCmdBuilder(unittest.TestCase):
    def test_set_mtime(self):        
        #self.assertEqual(calc_mtime(),"")
        self.assertEqual(set_mtime(0),"")
        self.assertEqual(set_mtime(1)," -mtime +0") 
        self.assertRaises(ValueError, set_mtime,"Wrong" )     
        
    def test_set_excl_format(self):  
        self.assertEqual(set_excl_format(None),"")
        
    
    def test_find_cmd(self): 
        self.assertEqual(build_find_cmd(),"find .; 1>/dev/null 2>/dev/null")
        self.assertEqual(build_find_cmd(find_format='*.log'),"find . -type f -iname '*.log'; 1>/dev/null 2>/dev/null")
        self.assertEqual(build_find_cmd(find_format='*.log',output="Y"),"find . -type f -iname '*.log';")
        self.assertEqual(build_find_cmd(find_format='*.log',excl_format='*xpi*',output="Y"),"find . -type f -iname '*.log' -not -path  '*AutoToolBox.log*' -not -path '*xpi*';")
        self.assertEqual(build_find_cmd(find_format='*.log',exec_cmd="rm"),"find . -type f -iname '*.log' -exec rm {} \; 1>/dev/null 2>/dev/null")
        self.assertEqual(build_find_cmd(find_format='*.log', mtime='1' ,exec_cmd="rm"),"find . -type f -iname '*.log' -mtime +0 -exec rm {} \; 1>/dev/null 2>/dev/null")
        
    def test_del_logs_cmd(self): 
        self.assertEqual(del_logs_cmd(),"find . -type f -iname '*.log*' -not -path  '*AutoToolBox.log*' -not -path '*xpi*' -mtime +0 -exec rm {} \; 1>/dev/null 2>/dev/null")        
        self.assertEqual(del_logs_cmd(1,del_format='Y'),False)   
    def test_set_exec_cmd(self):   
        self.assertEqual(set_exec_cmd("rm")," -exec rm {} \\")
        self.assertRaises(ValueError, set_exec_cmd,"Wrong command" )
    def test_find_last_folder_cmd(self):
        self.assertEqual(find_last_folder_cmd('ES_FR1051',1 ),'find ES_FR1051 -maxdepth 1 -type d -name "*" | sort -n | grep -v AutoBackup | tail -1')
       
    def test_build_kill_cmd(self):
        self.assertEqual(build_kill_cmd('N',"MainMenu.py"),"ps -fu $USER | grep -v $$ | grep -v '\-ksh' | grep -v 'ssh' | grep -v '/bin/sh'| grep -v 'MainMenu.py' | grep -v 'grep'|   grep -iv 'sshd' | grep -v PID | awk '{print $2}'| xargs kill -9 "+ NO_OUTPUT )
        self.assertEqual(build_kill_cmd('N'),"ps -fu $USER | grep -v $$ | grep -v '\-ksh' | grep -v 'ssh' | grep -v '/bin/sh'| grep -v 'CleanFileSystem.' | grep -v 'MainMenu.py' | grep -v 'grep'|   grep -iv 'sshd' | grep -v PID | awk '{print $2}'| xargs kill -9 "+NO_OUTPUT )
        self.assertEqual(build_kill_cmd('Y'),"kill -9 -1;" + NO_OUTPUT)
    
    def test_get_PID(self):
        self.assertEqual(get_PID("") ,'''`ps -fu $USER | grep -i "" | grep -v grep | grep -v echo  |grep -v $$ | awk '{print $2}' | tail -1`''')

    def test_kill_dmn_cmd(self):   
        self.assertEqual (kill_dmn_cmd(3333),  "kill-9 3333 1>/dev/null 2>/dev/null")
        
    def test_sqlplus_query(self):
        self.assertEqual (sqlplus_query("select * from logical_date",{'dbUser':'ABPAPP1', 'dbPass':'ABPAPP1','dbInstance':'VFIDB825','dbHost':'illinqw825','dbPort':1521}),
                          '''echo "set echo off head off verify off feed off pages 0;\nset linesize 4000;\nselect * from logical_date;" | sqlplus -S ABPAPP1/ABPAPP1@VFIDB825''')
        
        
######################################################################################################
if __name__ == "__main__":
    unittest.main()