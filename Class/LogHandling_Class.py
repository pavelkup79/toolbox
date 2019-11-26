#!/usr/bin/python

#V1
import subprocess
import time
import logging 
from SystemHandling import SystemHandler,subproc_popen,print_data ,find_files
from Graphics_Class import Graphics
from UnixCmdBuilder import check_file_exist_cmd, build_find_cmd,cat_str_in_file,grep_str_cmd

logger = logging.getLogger("AutoToolBox")

class LogHandling:	
	def CheckLogFileExist(self,Path,FileName,Timeout):
		print ("------------ CheckLogFileExist -------- ")
		FullFileName="~/"+Path+"/"+FileName
		print (">>> "+FullFileName)
		cmd="[ -f "+FullFileName+" ] && echo 'Pass' || echo 'Fail'"
		try:
			output = subprocess.check_output(cmd, shell=True).rstrip("\n")
		except:
			print ("> Command Error")
			return 1
		
		MyProgress = Graphics()		
		Tout=0
		while output.find('Pass') and Tout<=Timeout :		
			output = subprocess.check_output(cmd, shell=True).rstrip("\n")
			MyProgress.progress(Tout,Timeout,'Waiting for log file')
			time.sleep(1)
			Tout=Tout+1
		print ("\n")
		if output.find('Pass') == -1:
			print ("> Validation Failed")
			return 1
		else:
			print ("> Validation Pass")
	
	
    #Added by Pavel with full 'Path'	
	def check_log_exist (self,Path,FileName,Timeout=1):
		""" function gets full path and checking if log exist by count  using unix 'find' command"""	
		if str( Path[0] ) =='/': 
			FullFileName = str( Path ) +"/"+str( FileName )
			logger.info( "Checking if log exist for "+ FullFileName )
		else:
			logger.error(" check_log_exist ->Invalid log path :" +Path )	
		is_log_exist=False
		#MyProgress=Graphics()		
		Tout=0	
		while is_log_exist == False  and Tout<=Timeout :
			data = find_files(maxdepth=1,find_format=FileName,path=Path)
			count = int( len( data[0].rstrip('\n') )  )			
			if count > 0:
				logger.info("Log is located..")
				is_log_exist = True
			elif count == 0:
				logger.info ("Log is not found..")
				#MyProgress.progress(Tout,Timeout,'Waiting for log file')
				time.sleep(1)
				Tout=Tout+1
				is_log_exist = False
		return is_log_exist
	
	
	
	def BackupOldLog(self,Path,FileName):
		print ("------------ BackupOldLog -------- ")
		FullFileName="~/"+Path+"/"+FileName+"*"
		print (">>> BackUp : "+FullFileName)
		cmd="ls -ltr "+FullFileName+" 2>/dev/null |wc -l"
		print ("> Command : "+cmd)
		try:
			output = subprocess.check_output(cmd, shell=True).rstrip("\n")
		except:
			print ("> Command Error")
			return 1

		if int(output)==0 :
			print ("> Files Not found , nothing to backup")	
			return 1
		else:
			print ("> Files found , will continue with backup process")
		
		cmd="cd ~/"+Path+";mkdir -p AutoBackupFolder;mv "+FileName+"* ./AutoBackupFolder"
		print ("> Command : "+cmd)
		try:
			subprocess.check_output(cmd, shell=True).rstrip("\n")
		except:
			print ("> Command Error")
			return 1

		cmd="ls -ltr "+FullFileName+" 2>/dev/null |wc -l"
		try:
			output = subprocess.check_output(cmd, shell=True).rstrip("\n")
		except:
			print ("> Command Error")
			return 1

		if int(output)==0 :
			print ("> Backup Completed")	
		else:
			print ("> Backup Failed")
			return 1
			
	
	def backup_log(self,Path,FileName):
		""" function gets full path and backup file in AutoBackupFolder folder """
		FullFileName=Path+"/"+FileName+"*"
		logger.info("BackUp : "+FullFileName)
		cmd="ls -ltr "+FullFileName+" 2>/dev/null |wc -l"
		print ("> Command : "+cmd)
		try:
			output = subprocess.check_output(cmd, shell=True).rstrip("\n")
		except:
			logger.error("Command Error")
			return 1

		if int(output)==0 :
			logger.info("Files Not found , nothing to backup")	
			return 1
		else:
			logger.debug("Files found , will continue with backup process")
		
		cmd="cd "+Path+";mkdir -p AutoBackupFolder;mv "+FileName+"* ./AutoBackupFolder"
		logger.debug("Command : "+cmd)
		try:
			subprocess.check_output(cmd, shell=True).rstrip("\n")
		except:
			logger.error("Command Error")
			return 1

		cmd="ls -ltr "+FullFileName+" 2>/dev/null |wc -l"
		try:
			output = subprocess.check_output(cmd, shell=True).rstrip("\n")
		except:
			logger.error("Command Error")
			return 1

		if int(output)==0 :
			logger.info("Backup Completed")	
		else:
			logger.error("Backup Failed")
			return 1

	def check_errs_in_log(self,Path,FileName='*.log*', strs_to_find=[],NumOfLines =7):
		"""	function gets file path and format and check that list of strings (Error, FATAl) not in the log"""
		if str( Path[0] ) =='/' : 
			FullFileName = str( Path ) +"/"+str( FileName )
			logger.info( "Checking if log exist for "+ FullFileName )
		else:
		    logger.error(" check_log_exist ->Invalid log path :" +Path)	
		if  len(strs_to_find)==0:
			logger.warning( "No strings to check in log  provided" )
			return True
		grep_cmd =grep_str_cmd(strs_to_find)
		cat_cmd =cat_str_in_file(grep_cmd,FileName,count='Y')
		data = subproc_popen(cat_cmd)
		count = int( str(data[0]).rstrip('\n')  )
			
		if count > 0:
			logger.info(" Errors detected in the log")
			return True
		else :
			logger.info("No errors detected in the log ")
			return False
		    
		
		  
			
					
	def CheckStrInLogFull(self,Path,FileName,MyStr,Timeout,NumOfLines):
		MyStrPrint=MyStr.replace("@", "\\")
		MyStrSearch=MyStr.replace("@", "' -e '")
		MyStrSearch="'"+MyStrSearch+"'"
		print ("------------ CheckStrInLog -------- ")
		FullFileName="~/"+Path+"/"+FileName+"*"
		print (">>> File :"+FullFileName)
		print (">>> String to search : "+"'"+MyStrPrint+"'")

		cmd="ls -ltr "+FullFileName+"|wc -l"
		print (">>> Command : "+cmd)
		try:
			output = subprocess.check_output(cmd, shell=True).rstrip("\n")
		except:
			print (">>> Command Error")
			return 1

		if int(output)==0 :
			print (">>> Failure - There are no files that match to file : "+FullFileName)
			return 1
		elif int(output)>1:
			print (">>> WARNING - There are "+output+" files that match to file : "+FullFileName)
			
		cmd="cd ~/"+Path+";ls -tr "+FileName+"* | tail -1"
		print (">>> Command : "+cmd)
		try:
			LogFile = subprocess.check_output(cmd, shell=True).rstrip("\n")
		except:
			print (">>> Command Error")
			return 1	
		
	def is_str_in_log(self,Path,FileName,MyStr,Timeout=60,NumOfLines=1):
		MyStrPrint=MyStr.replace("@", "\\")
		MyStrSearch=MyStr.replace("@", "' -e '")
		MyStrSearch="'"+MyStrSearch+"'"
		FullFileName=Path+"/"+FileName+"*"
		logger.debug("is_str_in_log -> File :"+FullFileName)
		logger.debug("is_str_in_log ->String to search : "+"'"+MyStrPrint+"'")

		cmd="ls -ltr "+FullFileName+"|wc -l"
		logger.debug("is_str_in_log ->Command : "+cmd)
		try:
			output = subprocess.check_output(cmd, shell=True).rstrip("\n")
		except:
			logger.error("is_str_in_log ->Command Error")
			return False

		if int(output)==0 :
			logger.info("is_str_in_log ->Failure - There are no files that match to file : "+FullFileName)
			return False
		elif int(output)>1:
			logger.warning("is_str_in_log ->WARNING - There are "+output+" files that match to file : "+FullFileName)
			
		cmd="cd "+Path+";ls -tr "+FileName+"* | tail -1"
		logger.debug("is_str_in_log-> Command : "+cmd)
		try:
			LogFile = subprocess.check_output(cmd, shell=True).rstrip("\n")
		except:
		    logger.error("is_str_in_log ->Command Error")
				 
		FullFileName=Path+"/"+LogFile
		logger.debug("The file that will be processed : "+ FullFileName)
		cmdFind="cat "+FullFileName+" |grep -e "+MyStrSearch+"| wc -l"
		cmdFindOutput="cat "+FullFileName+"| grep -C" + str(NumOfLines) + " -e " + MyStrSearch
		
		logger.debug("is_str_in_log ->Command : "+cmdFind)
		try:
			output = subprocess.check_output(cmdFind, shell=True).rstrip("\n")
		except:
			logger.error("is_str_in_log ->Command Error")

		
		MyProgress = Graphics()	
		Tout=0
	
		while int(output) < 1 and Tout<=Timeout :		
			output = subprocess.check_output(cmdFind, shell=True).rstrip("\n")
			MyProgress.progress(Tout,Timeout,'Waiting for string in file')
			time.sleep(1)
			Tout=Tout+1
		print ("\n")
		if int(output) < 1:
			print (">>> String validation Failed")
			return False
		else:
			print (">>> String Validation Pass")
			print ("======== Output Results ==========")
			LinesOutput = subprocess.check_output(cmdFindOutput, shell=True).rstrip("\n")
			print (LinesOutput)
			print ("==================================")
			return True	
		
	
	def CheckStrInLog(self,Path,FileName,MyStr,Timeout,NumOfLines):
		MyStrPrint=MyStr.replace("@", "\\")
		MyStrSearch=MyStr.replace("@", "' -e '")
		print ("------------ CheckStrInLog -------- ")
		FullFileName="~/"+Path+"/"+FileName+"*"
		print (">>> File : "+FullFileName)
		print (">>> String to search : "+"'"+MyStrPrint+"'")
		cmd="ls -ltr "+FullFileName+"|wc -l"
		try:
			output = subprocess.check_output(cmd, shell=True).rstrip("\n")
		except:
			print (">>> Command Error")
			return 1

		if int(output)==0 :
			print (">>> Failure - There are no files that match to file : "+FullFileName)
			return 1
			
		cmd="cd ~/"+Path+";ls -tr "+FileName+"* | tail -1"
		try:
			LogFile = subprocess.check_output(cmd, shell=True).rstrip("\n")
		except:
			print (">>> Command Error")
			return 1			
						
		FullFileName="~/"+Path+"/"+LogFile
		#print (">>> The file that will be processed : "+ FullFileName)
		cmdFind="cat "+FullFileName+" |grep -e "+"'"+MyStrSearch+"'"+"| wc -l"
		#print (">>> Find Command : "+cmdFind)
		cmdFindOutput="cat "+FullFileName+"| grep -C" + str(NumOfLines) + " -e " +"'"+MyStrSearch+"'"
		try:
			output = subprocess.check_output(cmdFind, shell=True).rstrip("\n")
		except:
			print (">>> Command Error")
			return 1		
		
		MyProgress = Graphics()	
		Tout=0
	
		while int(output) < 1 and Tout<=Timeout :		
			output = subprocess.check_output(cmdFind, shell=True).rstrip("\n")
			MyProgress.progress(Tout,Timeout,'Waiting for string in file')
			time.sleep(1)
			Tout=Tout+1
		print ("\n")
		if int(output) < 1:
			print (">>> String Not found")
			return 1
		else:
			print ("======== Output Results ==========")
			LinesOutput = subprocess.check_output(cmdFindOutput, shell=True).rstrip("\n")
			print (LinesOutput)
			print ("==================================")
			return 0
		
	def CheckStrNoPrint(self,Path,FileName,MyStr,Timeout):
		MyStrPrint=MyStr.replace("@", "\\")
		MyStrSearch=MyStr.replace("@", "' -e '")
		FullFileName="~/"+Path+"/"+FileName+"*"
		cmd="ls -ltr "+FullFileName+"|wc -l"
		try:
			output = subprocess.check_output(cmd, shell=True).rstrip("\n")
		except:
			print (">>> Command Error")
			return 1

		if int(output)==0 :
			print (">>> Failure - There are no files that match to file : "+FullFileName)
			return 1
			
		cmd="cd ~/"+Path+";ls -tr "+FileName+"* | tail -1"
		try:
			LogFile = subprocess.check_output(cmd, shell=True).rstrip("\n")
		except:
			print (">>> Command Error")
			return 1			
						
		FullFileName="~/"+Path+"/"+LogFile
		cmdFind="cat "+FullFileName+" |grep -e "+"'"+MyStrSearch+"'"+"| wc -l"
		try:
			output = subprocess.check_output(cmdFind, shell=True).rstrip("\n")
		except:
			print (">>> Command Error")
			return 1		
		Tout=0
	
		while int(output) < 1 and Tout<=Timeout :		
			output = subprocess.check_output(cmdFind, shell=True).rstrip("\n")
			time.sleep(1)
			Tout=Tout+1
		if int(output) < 1:
			return 1
		else:
			return 0	