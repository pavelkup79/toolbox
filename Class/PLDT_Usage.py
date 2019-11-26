from UnixConnector import *
from OraDBConnect import *
from UnixCmdBuilder import *
import time

host='1.1.1.1'
username=dbUser='someuser'
password=dbPass='somepassword'
port=2214
dbPort=1521
db_Admin ={'dbUser':'someuser', 'dbPass':'somepassword','dbInstance':'ADMIN','dbHost':'1.1.1.1','dbPort':1521}

dbInstance='CUST1'
keyfile_path = 'private_key_file'
WAIT_TIME=10

usage_path='/export/home/arbor/BP/tenantId2_data/usage/remote/ready'
file_name='SMVAS20181025000300_000497.data'
filepath = usage_path +"/"+file_name
localpath = './'+file_name
dbPass,dbInstance,dbPort
if __name__ == "__main__":
  print ">>>> Coping CDR to usage location..."
  put_sftp_file (host, port, username, password, filepath,localpath)
  execute_ssh_transport_command(host, port, username, password, None, None, "cd /export/home/arbor;source PQA_env.sh")
  print ">>>> Checking if file is copied " 
  """
  print ">>>> Checking if file is copied " 
  execute_ssh_transport_command(host, port, username, password, None, None, "cd " + usage_path+"; ls -rt")
  """
  
  #DB= OracleDBConnector(host,dbUser,dbPass,dbInstance,dbPort)
  #DB= OracleDBConnector('illinqw933','ABPAPP1','ABPAPP1','VFIDB933',1521)
  #result=DB.query ('select LOGICAL_DATE FROM LOGICAL_DATE')
  #result=DB.query ('select control_file_expected from EXT_CONTACTS where ext_contact_id= 20')
  #print result
  print ">>>> Checking if only data file is required  " 
  result  = execute_ssh_transport_command(host, port, username, password, None, None,
                                 sqlplus_query('select control_file_expected from EXT_CONTACTS where ext_contact_id= 20' ,db_Admin ))
  
  
  print ">>>> Deleting process_status  and process_sched   " 
  Del_Qry="""delete from process_status where process_name = 'com13';
             delete from process_sched where process_name = 'com01';
             commit;
          """
  execute_ssh_transport_command(host, port, username, password, None, None,sqlplus_query(Del_Qry ,db_Admin ))
  
  InsCOM_Qry="""insert into PROCESS_SCHED (PROCESS_NAME,TASK_NAME,TASK_CYCLE,TASK_MODE, SCHED_START,TASK_INTRVL,TASK_STATUS,TASK_PRIORITY,SLIDE_TIME,DB_NAME,SQL_QUERY,DEBUG_LEVEL,PLAT_ID,USG_CRT_HOUR,USG_PLAT_ID,USG_VERSION) 
  values ('com02','com02','N',0,sysdate,86400,0,0,0,'ADMIN','EXT_CONTACTS.ext_contact_id=20',0,null,null,null,null);
  commit;"""
  print(">>>> Inserting into PROCESS_SCHED for COM ...")
  execute_ssh_transport_command(host, port, username, password, None, None,sqlplus_query(InsCOM_Qry ,db_Admin ))
  RunCOM ="COM com02 2 -tid 2"
  print ">>>> Starting COM....."
  execute_ssh_transport_command(host, port, username, password, None, None,RunCOM)
  print ">>>> Waiting 30 seconds...."
  time.sleep(30)
  print ">>>> Printing result for FILE_STATUS....."
  COM_sts_Qry ="select count(file_status) from FILE_STATUS  where file_name like '%" +file_name.rstrip('.data') +"%';"
  execute_ssh_transport_command(host, port, username, password, None, None,sqlplus_query(COM_sts_Qry ,db_Admin ))


  InsMCAP_Qry="""
  insert into PROCESS_SCHED (PROCESS_NAME,TASK_NAME,TASK_CYCLE,TASK_MODE, SCHED_START,TASK_INTRVL,TASK_STATUS,TASK_PRIORITY,SLIDE_TIME,DB_NAME,SQL_QUERY,DEBUG_LEVEL,PLAT_ID,USG_CRT_HOUR,USG_PLAT_ID,USG_VERSION) 
  values ('mcap03','mcap03','N',0,sysdate,86400,0,0,0,'ADMIN',null,0,null,null,null,null);
  commit;"""
  print(">>>> Inserting into PROCESS_SCHED for MCAP ...")
  result=execute_ssh_transport_command(host, port, username, password, None, None,sqlplus_query(InsMCAP_Qry ,db_Admin ))
  
  print ">>>>  Done"
  
  
  