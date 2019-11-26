#!/usr/bin/python

import subprocess

class UnixCmd:
#	def __init__(self,Command):
#		self.cmd=Command
	def UnixCmdWithOutputVerification(self,Cmd,ExpOutput):
		print ("------------ UnixCmdWithOutputVerification -------- ")
		print (">>> "+Cmd)
		try:
			output = subprocess.check_output(Cmd, shell=True).rstrip("\n")
		except:
			print ("> Command Error")
			return 1
		else:
			print ("> Command Pass")
		if output.find(ExpOutput) == -1:
			print ("> Validation Failed")
			return 1
		else:
			print ("> Validation Pass")
			return 0
		
	def UnixCmdWithOutputPrintAndVerification(self,Cmd,ExpOutput):
		print ("------------ UnixCmdWithOutputPrintAndVerification -------- ")
		print (">>> "+Cmd)
		try:
			output = subprocess.check_output(Cmd, shell=True).rstrip("\n")
		except:
			print ("> Command Error")
			return 1
		else:
			print ("> Command Pass")
		print(output)	
		if output.find(ExpOutput) == -1:
			print ("> Validation Failed")
			return 1
		else:
			print ("> Validation Pass")
			return 0
		
	def UnixCmdExec(self,Cmd):
		print ("------------ UnixCmdExec -------- ")
		print (">>> "+Cmd)
		try:
			subprocess.check_output(Cmd, shell=True).rstrip("\n")
		except:
			print ("> Command Error")
			return 1
		else:
			print ("> Command Pass")
			return 0

	def UnixCmdExecWithOutputPrint(self,Cmd):
		print ("------------ UnixCmdExecWithOutputPrint -------- ")
		print (">>> "+Cmd)
		try:
			output = subprocess.check_output(Cmd, shell=True).rstrip("\n")
		except:
			print ("> Command Error")
			return 1
		else:
			print ("> Command Pass")
		print (output)
		return 0