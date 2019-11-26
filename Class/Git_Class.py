#!/usr/bin/python

import re
import subprocess

class Git:
	def __init__(self, ProjectName,GitGroup):
		self.GitGrp=GitGroup
		self.ProjName=ProjectName
		self.GitLink="https://gitlab.corp.amdocs.com"
		
	def Git_CheckFileConnection(self,FileName):
		print ("\n===============================")
		print ("Git_CheckFileConnection")
		print ("===============================")		
		GitLink = "curl -I -H 'Accept-Encoding: gzip,deflate' -k {}/{}/{}/raw/master/{}".format(self.GitLink,self.GitGrp,self.ProjName,FileName)
		print (">> "+GitLink)
		output = subprocess.check_output(GitLink, shell=True)
		matchObj = re.match( '.*200.*',output)
		if matchObj:
			print ("Git Connection Pass")
			return 0
		else:
			print ("Git Connection Failed")
			return 1

	def Git_CheckProjectConnection(self):
		print ("\n===============================")
		print ("Git_CheckProjectConnection")
		print ("===============================")		
		GitLink = "curl -I -H 'Accept-Encoding: gzip,deflate' -k {0}/{1}/{2}/-/archive/master/{2}-master.zip".format(self.GitLink,self.GitGrp,self.ProjName)
		print (">> "+GitLink)
		output = subprocess.check_output(GitLink, shell=True)
		matchObj = re.match( '.*200.*',output)
		if matchObj:
			print ("Git Connection Pass")
			return 0
		else:
			print ("Git Connection Failed")
			return 1
		
	def Git_DownloadFile(self,FileName,Location):
		print ("\n===============================")
		print ("Git_DownloadFile")
		print ("===============================")
		print ("\nDownload "+FileName+"and move to "+"~/"+Location+"\n")		
		UnixCommand = "rm -f ./{};echo $?".format(FileName)
		print (">> "+UnixCommand)
		output = subprocess.check_output(UnixCommand, shell=True).rstrip("\n")
		if output == "0":
			print ("Delete "+FileName+" Pass")
			
		UnixCommand = "rm -f ~/{}/{};echo $?".format(Location,FileName)
		print (">> "+UnixCommand)
		output = subprocess.check_output(UnixCommand, shell=True).rstrip("\n")
		if output == "0":
			print ("Delete "+FileName+" from target location "+Location+" Pass")
	
		GitLink = "curl -fOk {}/{}/{}/raw/master/{}".format(self.GitLink,self.GitGrp,self.ProjName,FileName)
		print (">> "+GitLink)
		#os.system(GitLink) 
		output = subprocess.check_output(GitLink, shell=True)
		UnixCommand = "ls -ltr {} 1>/dev/null 2>/dev/null;echo $?".format(FileName)
		print (">> "+UnixCommand)
		output = subprocess.check_output(UnixCommand, shell=True).rstrip("\n")
		if output == "0":
			print (FileName+" Downloaded Sussceefully")
		else:
			print (FileName+" Downloaded Failed")
			return 1
		UnixCommand = "mv ./{} ~/{};echo $?".format(FileName,Location)
		print (">> "+UnixCommand)
		output = subprocess.check_output(UnixCommand, shell=True).rstrip("\n")
		if output == "0":
			print ("Move "+FileName+" to "+Location+" Pass")
		else:
			print ("Move "+FileName+" to "+Location+" Failed")
			return 1
		return 0
		
	def Git_DownloadProject(self,Location):
		print ("\n===============================")
		print ("Git_DownloadProject")
		print ("===============================")
		print ("\nDownload "+self.ProjName+"\n")
		UnixCommand = "rm -rf ./{}-master*;echo $?".format(self.ProjName)
		print (">> "+UnixCommand)
		output = subprocess.check_output(UnixCommand, shell=True).rstrip("\n")
		if output == "0":
			print ("Delete "+self.ProjName+"-master*"+" Pass")

		UnixCommand = "cd ~/{};rm -rf ./{}-master*;echo $?".format(Location,self.ProjName)
		print (">> "+UnixCommand)
		output = subprocess.check_output(UnixCommand, shell=True).rstrip("\n")
		if output == "0":
			print ("Delete "+self.ProjName+"-master*"+" from "+Location+" Pass")

			
		GitLink = "curl -fOk {0}/{1}/{2}/-/archive/master/{2}-master.zip".format(self.GitLink,self.GitGrp,self.ProjName)
		print (">> "+GitLink)
		output = subprocess.check_output(GitLink, shell=True)
		UnixCommand = "ls -ltr {}-master.zip 1>/dev/null 2>/dev/null;echo $?".format(self.ProjName)
		print (">> "+UnixCommand)
		output = subprocess.check_output(UnixCommand, shell=True).rstrip("\n")
		if output == "0":
			print (self.ProjName+"-master.zip"+" Downloaded Sussceefully")
		else:
			print (self.ProjName+"-master.zip"+" Downloaded Failed")
			return 1
		
		UnixCommand = "mv {1}-master.zip ~/{0};echo $?".format(Location,self.ProjName)
		print (">> "+UnixCommand)
		output = subprocess.check_output(UnixCommand, shell=True).rstrip("\n")
		if output == "0":
			print ("mv "+self.ProjName+"-master.zip"+" to ~/"+Location+" Pass")
		else:
			print ("mv "+self.ProjName+"-master.zip"+" to ~/"+Location+" Failed")
			return 1		

		UnixCommand = "cd ~/{};unzip -o {}-master.zip 1>/dev/null 2>/dev/null;echo $?".format(Location,self.ProjName)
		print (">> "+UnixCommand)
		output = subprocess.check_output(UnixCommand, shell=True).rstrip("\n")
		if output == "0":
			print ("Unzip "+self.ProjName+"-master.zip"+" in ~/"+Location+" Pass")
		else:
			print ("Unzip "+self.ProjName+"-master.zip"+" in ~/"+Location+" Failed")
			return 1	

		UnixCommand = "cd ~/{0}/;cp -r ./{1}-master*/* ./ 1>/dev/null 2>/dev/null;echo $?".format(Location,self.ProjName)
		print (">> "+UnixCommand)
		output = subprocess.check_output(UnixCommand, shell=True).rstrip("\n")
		if output == "0":
			print ("Copy Content of "+self.ProjName+"-master"+" to ~/"+Location+" Pass")
		else:
			print ("Copy Content of "+self.ProjName+"-master"+" to ~/"+Location+" Failed")
			return 1
			
		UnixCommand = "cd ~/{};rm -rf ./{}-master*;echo $?".format(Location,self.ProjName)
		print (">> "+UnixCommand)
		output = subprocess.check_output(UnixCommand, shell=True).rstrip("\n")
		if output == "0":
			print ("Delete "+self.ProjName+"-master*"+" from "+Location+" Pass")
		return 0
		
	def Git_ExecPermissionFile(self,Location,FileName):
		print ("\n===============================")
		print ("Git_ExecPermissionFile")
		print ("===============================")		
		UnixCommand = "cd ~/{};chmod 777 ./{}".format(Location,FileName)
		print (">> "+UnixCommand)
		subprocess.check_output(UnixCommand, shell=True).rstrip("\n")		
		return 0
		
	def Git_ExecPermissionFolder(self,Location):
		print ("\n===============================")
		print ("Git_ExecPermissionFolder")
		print ("===============================")		
		UnixCommand = "chmod -R 777 ~/{}".format(Location)
		print (">> "+UnixCommand)
		subprocess.check_output(UnixCommand, shell=True).rstrip("\n")		
		return 0		