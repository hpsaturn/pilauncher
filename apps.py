from config import config

class AppManager:

    def __init__(self):
        # self.cfg = config('apps.yml','settings.yml')
        self.cfg = config('/home/pi/pihead/apps.yml','/home/pi/pihead/settings.yml')
        self.app_count = self.cfg.getAppsCount()
        self.cur_app = 0
        self.app_status_count = len(self.cfg.status_reg)
    
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
        
    def getAppsStatusList(self):
        return self.cfg.status_reg

    def getAppsStatusCount(self):
        return self.app_status_count
    
    def reset(self):
        app = self.getCurrentApp()
        app.reset()

# Basic Test:
# am = AppManager()
# print(am.cfg.auto_screen_off)
# print(am.cfg.screen_time_off)
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




