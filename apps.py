from config import config

class AppManager:

    def __init__(self):
        self.cfg = config('/home/pi/pihead/config.yml')
        # self.cfg = config('config.yml')
        self.app_count = self.cfg.getAppsCount()
        self.cur_app = 0
        self.app_status_count = len(self.cfg.status_reg)
        self.app_status_pending = 0
    
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
    
    def getNextPendingApp(self):
        if self.app_status_count > 0:
            self.app_status_pending = self.app_status_pending + 1
            if self.app_status_pending >= self.app_status_count:
                self.app_status_pending = 0
            return self.cfg.status_reg[self.app_status_pending]
        else:
            return None
    
    def reset(self):
        app = self.getCurrentApp()
        app.reset()
        # self.cur_app=0

# Basic Test:
# am = AppManager()
# app = am.getCurrentApp()
# print(am.getCurrentCmd().command)

# print(am.getNextPendingApp())
# print(am.getNextPendingApp())
# print(am.getNextPendingApp())
# print(am.getNextPendingApp())
# print(am.getNextPendingApp())

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




