from config import config

class AppManager:

    def __init__(self):
        self.cfg = config('config.yml')
        self.app_count = self.cfg.getAppsCount()
        self.cur_app = 0
    
    def getCurrentApp(self):
        return self.cfg.apps[self.cur_app]

    def getNextApp(self):
        self.cur_app = self.cur_app+1
        if self.cur_app >= self.app_count:
            self.cur_app=0
        return self.getCurrentApp()
    
    def getNextCmd(self):
        app = self.getCurrentApp()
        return app.getNextCmd()
    
    def getCurrentCmd(self):
        app = self.getCurrentApp()
        return app.getCurrentCmd()

# Basic Test:
# am = AppManager()
# app = am.getCurrentApp()
# print(am.getCurrentCmd().command)

# Tests navigation Apps/Commands:
# app = am.getNextApp()
# print(app)
# app = am.getNextApp()
# print(app)
# app = am.getNextApp()
# print(app)
# cmd = am.getNextCmd()
# print(cmd.command)
# cmd = am.getNextCmd()
# print(cmd.command)
# cmd = am.getNextCmd()
# print(cmd.command)




