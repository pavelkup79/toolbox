#!/usr/bin/python

import subprocess
import time
from Graphics_Class import Graphics
from LogHandling_Class import LogHandling

class JobHandling:	
	def RunJob(self,JobName,ReqType="BYREQ",PreCommand="",TimeOut=60):
		print ("------------ RunJobFull -------- ")
		subprocess.check_output('mkdir -p ~/AutoToolBox/Logs', shell=True).rstrip("\n")
		SysDate=subprocess.check_output('date \'+%d%m%Y_%H%M%S\'', shell=True).rstrip("\n")
		ErrorLog='RunJobFull_'+JobName+'_'+ReqType+'_'+SysDate+'Err.log'
		ExecLog='RunJobFull_'+JobName+'_'+ReqType+'_'+SysDate+'.log'
		JobPath=subprocess.check_output('echo $OP_LOG_DIR | sed \'s/.*var/var/g\'', shell=True).rstrip("\n")
		print (">>> Log Path : ~/"+JobPath)
		if PreCommand!="":
			PreCommand=PreCommand+";"
		
		JobLog = LogHandling()
		JobLog.BackupOldLog (JobPath,JobName)
					
		cmd=PreCommand+"RunJobs "+JobName+" "+ReqType
		print (">>> Job Command : "+cmd)
		cmd=PreCommand+"RunJobs "+JobName+" "+ReqType +" 1> ~/AutoToolBox/Logs/"+ExecLog+" 2> ~/AutoToolBox/Logs/"+ErrorLog+" &"
		#print (">>> Job Command : "+cmd)
		try:
			subprocess.check_output(cmd, shell=True).rstrip("\n")
		except:
			print (">>> Command Error")
			return 1
		print (">>> Job has been triggered , checking logs in ~/AutoToolBox/Logs")
		ResultCode=JobLog.CheckStrInLog ('AutoToolBox/Logs/',ErrorLog,'Failed to get job',5,1)
		if ResultCode == 0:
			print (">>> Job not exist in OPR table : OPPAR OPPAR_DB")
			return 1
		else:
			print (">>> Job exist in OPR table : OPPAR OPPAR_DB ,will continue to check logs")
		
		JobLog.CheckStrInLog ('AutoToolBox/Logs/',ExecLog,'Operational Job ended successfully@Operational Job ended with failure',TimeOut,10)
		ResultCode=JobLog.CheckStrNoPrint ('AutoToolBox/Logs/',ExecLog,'Operational Job ended successfully',2)
		if ResultCode == 0:
			print (">>> "+JobName+" Ended successfully")
			print (JobName+"=PASS")
			return 0
		else:
			print (">>> "+JobName+" Execution Failed")
			print (JobName+"=FAILED")
			return 1
		
		def StopJob(self,JobName):
			pass
            