'''
Created on Sep 13, 2018

@author: pavelkup
'''
import logging
import os
from Menu import Menu
from TCDaemons import TCDaemonsMenu
from ABPDaemons import ABPDaemonsMenu
from CleanFileSystem import cleanFileSystemMenu
from CycleHandling import CycleHandlerMenu

logger = logging.getLogger("AutoToolBox")

class MainMenu(Menu):  
    def __init__(self):
        self.MenuName="AutotoolBox Menu"
        self.IsMenuActive=True
        self.menuItems= [ 
            {"Clean File System": cleanFileSystemMenu().activate_menu},
            {"TC daemons": TCDaemonsMenu().activate_menu },
            {"ABP daemons": ABPDaemonsMenu().activate_menu },
            {"Cycle Menu":CycleHandlerMenu().activate_menu},
            {"Back": self.activate_menu},
            {"Exit": self.exit_menu}
            ]

    
if __name__ == "__main__":
    Menu= MainMenu()
    Menu.activate_menu()
    