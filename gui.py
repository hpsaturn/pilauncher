from apps import AppManager

class GuiManager():
    def __init__(self):
        self.am = AppManager()
        self.wlevel = 0
        self.showApp()

    def showApp(self):
        if self.wlevel == 0:
            print(self.am.getCurrentApp().name)
            return self.am.getCurrentApp().name
        else:
            print(self.am.getCurrentCmd().name)
            return self.am.getCurrentCmd().name

    def showNextApp(self):
        if self.wlevel == 0:
            self.am.getNextApp()
        else:
            self.am.getNextCmd()
        return self.showApp()
    
    def getAppStatusCmd(self):
        if self.wlevel == 0:
            return self.am.getCurrentApp().sta_cmd
        else:
            return None
    
    def getAppStatus(self):
        if self.wlevel == 0:
            return self.am.getCurrentApp().status
        else:
            return ''
    
    def runBack(self):
        self.wlevel=0
        self.am.reset()
        return self.showApp()
    
    def runAction(self):
        if self.wlevel==0:
            self.wlevel=1
            return self.showApp()
        else:
            command = self.am.getCurrentCmd().command
            if command == 'back':
                return self.runBack()
            else:
                return 'exec::'+command
            
    def getConfig(self):
        return self.am.cfg
            
# gm = GuiManager()
# gm.showNextApp()
# gm.runAction()
# gm.showNextApp()
# gm.showNextApp()
# gm.runAction()
# gm.runAction()

