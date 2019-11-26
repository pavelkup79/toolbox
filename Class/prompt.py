'''
Created on Sep 13, 2018

@author: pavelkup
'''
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import cmd
import os
import platform
from  CleanFileSystem import FileSystemCleaner


class Cli(cmd.Cmd):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        cmd.Cmd.__init__(self)
        self.prompt = "> "
        self.intro  = "System Handling Menu, type 'help' to get available options "
        self.doc_header ="Available options ( to get more info about specific option type'help _command_'"
        self.platform = self.check_platform()
        
    def do_show_cpu(self):
        """show_cpu - CPU status"""
        os.system("sar 2")

    def do_show_mem(self, args):
        """show_mem - RAM usage"""
        os.system("free")

    def do_show_disk(self, args):
        """show_disk - free space on the disk"""
        os.system("df . -k")

    def do_delete_logs(self, *args):
        """delete_logs - get Number of Days as parameter and clean all logs with *.log* format """
        print args
        FileSystemCleaner().delete_logs( )
        

    def do_show_log(self, args):
        """show_log - system logs"""
        pass
    
        
    def emptyline(self):
        pass
    
    def check_platform(self):
           return platform.system()
    
    def default(self, line):
            print "No such command"
        
if __name__ == "__main__":
    
    cli = Cli()
    print "Running on " + cli.check_platform() +" System"
    
    try:
        cli.cmdloop()
    except KeyboardInterrupt:
        print "Exiting ..."
        
    