from apps import AppManager

class GuiManager():
    def __init__(self):
        self.am = AppManager()
        self.wlevel = 0
        self.showApp()

    def showApp(self):
        if self.wlevel == 0:
            print(self.am.getCurrentApp().name)
        else:
            print(self.am.getCurrentCmd().name)

    def showNextApp(self):
        if self.wlevel == 0:
            self.am.getNextApp()
        else:
            self.am.getNextCmd()
        self.showApp()
    
    def runAction(self):
        if self.wlevel==0:
            self.wlevel=1
        else:
            print('execute: '+self.am.getCurrentCmd().command)
        self.showApp()


gm = GuiManager()
gm.showNextApp()
gm.showNextApp()
gm.runAction()
gm.showNextApp()
gm.runAction()
    



