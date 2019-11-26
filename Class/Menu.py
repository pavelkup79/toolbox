'''
Created on Sep 13, 2018

@author: pavelkup
'''
import logging
import os
import sys
from SystemHandling import SystemHandler,subproc_popen
from  UnixCmdBuilder import build_kill_cmd,bcolors
logger = logging.getLogger("AutoToolBox")

# Menu Class handle print menu, exit ,back and destructor
#print_menu_items- get/print list of dicts { "option" :"function"} and Menu Name , then call the function with "option" as parameter 

class Menu(object):
    def __init__(self):
        self.MenuName=""
        self.menuItems =[]
        self.IsMenuActive=True
    def activate_menu(self,f_input=None):  
        self.IsMenuActive=True
        os.system('clear')    
        while self.IsMenuActive ==True:
                self.print_menu_items(self.menuItems,self.MenuName) 
            
                        
    def print_menu_items(self,menuItems=[], menuName=""):
        """print_menu_items- get/print list of dicts { "option" :"menu function"} and Menu Name 
        , then call the " menu function" with "option" as parameter. If its needed implement dictionary {"option":"parameter"}
         for function inside of called "Menu function"
        """
        print "-----------------------------------------------------------------------"
        if(menuName):
            print bcolors.WARNING +  str(menuName) +bcolors.ENDC
        print ""
        if menuItems==[]:
           menuItems=[     {"Back": self.activate_menu},
            {"Exit": self.exit_menu} ]
        if menuItems:
            for item in menuItems:
                item.keys()
                print bcolors.WARNING + "[" + str(int(menuItems.index(item))+1) + "] " + item.keys()[0] +bcolors.ENDC
            choice = raw_input(">> ")
            try:
                if int(choice) < 1 or int(choice)> len(menuItems)+1  : raise ValueError
                menuItems[int(choice)-1].values()[0]( menuItems[int(choice)-1].keys()[0])
            except (ValueError, IndexError):
                print ""
                print ""
                print "Please select one of " +str(len(menuItems))+" options"    
                self.print_menu_items(menuItems , menuName)
    
    def back_menu(self, option):
        os.system('clear')
        logger.debug( "------------Exiting "  + self.MenuName + "   --------------------")
        self.IsMenuActive=False
        #self.__del__() 
        
    def exit_menu(self, option):
        print "------------Exiting "  + self.MenuName + "   --------------------"
        self.IsMenuActive=False
        sys.exit()
        #subproc_popen (build_kill_cmd ("N",'MainMenu.py'))   
        self.__del__()

    
    def __del__(self):   
        logger.info("Closing " +self.MenuName )

   
   
        
    
if __name__ == "__main__":
    menu = Menu()
    menu.activate_menu()
    
    
