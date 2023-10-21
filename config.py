import yaml

class app:
    def __init__(self,name):
        self.name = name
        self.cmds = []
        self.sta_cmd = ''
        self.status = ''
        self.cur_cmd = 0

        self.info_cmd_l1 = ''
        self.info_cmd_l2 = ''
        self.info_cmd_l3 = ''
        self.info_cmd_l4 = ''
    
    def get_name(self):
        return self.name
    
    def add_cmd(self, cmd):
        self.cmds.append(cmd)

    def getCurrentCmd(self):
        return self.cmds[self.cur_cmd]
    
    def getNextCmd(self):
        self.cur_cmd=self.cur_cmd+1
        if self.cur_cmd >= len(self.cmds):
            self.cur_cmd = 0
        return self.getCurrentCmd()
    
    def reset(self):
        self.cur_cmd=0
    
    def __str__(self):
        out = self.name+':\r\n'+'status cmd: '+self.sta_cmd
        for cmd in self.cmds:
            out=out+'\r\n'+cmd.name+' -> '+cmd.command
        return f"{out}"
    

class config:
    def __init__(self,config, settings):
        self.apps = []
        self.status_reg = []
        with open(config, 'r') as file:
            docs = yaml.safe_load_all(file)
            for doc in docs:
                # self.app_count = self.app_count+1
                self.laod_app(doc)
        
        # settings: 
        try:
            with open(settings, 'r') as file:
                presets = yaml.safe_load(file)
                self.screen_time_off = presets['screen_time_off']
                self.auto_screen_off = presets['auto_screen_off']
                self.info_refresh_rate = presets['info_refresh_rate']
                self.status_refresh_rate = presets['status_refresh_rate']
        except:
            print("bad settings file, load defaults..")
            self.screen_time_off = 30
            self.auto_screen_off = True
            self.info_refresh_rate = 3
            self.status_refresh_rate = 5
        
        print("settings:")
        print('screen_time_off: '+str(self.screen_time_off))
        print('auto_screen_off: '+str(self.auto_screen_off))
        print('info_refresh_rate: '+str(self.info_refresh_rate))

    def laod_app(self, doc):
        for name in dict.fromkeys(doc):
            # print(name)
            ap = app(name)
            for cmds in dict.fromkeys(doc[name]):
                # print(' '+cmds+' -> '+doc[name][cmds]['cmd'])
                cmd = app(cmds)
                # check if app contains status command and register it
                if cmds == 'Status':
                    ap.sta_cmd=doc[name][cmds]['cmd']
                    self.status_reg.append(ap)
                # check if app contains info or stats section and register it
                elif cmds == 'Stats' or cmds == 'Info':
                    ap.info_cmd_l1=doc[name][cmds]['l1']
                    ap.info_cmd_l2=doc[name][cmds]['l2']
                    ap.info_cmd_l3=doc[name][cmds]['l3']
                    ap.info_cmd_l4=doc[name][cmds]['l4']
                    cmd.command = 'stats'
                    ap.add_cmd(cmd)
                else:
                    cmd.command = doc[name][cmds]['cmd']
                    ap.add_cmd(cmd)
            
            self.apps.append(ap)

    def getAppsCount(self):
        return len(self.apps)
    
    def __str__(self):
        out = ''
        for app in self.apps:
            out=out+str(app)+'\r\n'
        return f"{out}"


# ac = config('config.yml')
# print(ac)

# print(ac.apps[0])
# print(ac.apps[1])
# print(ac.apps[0].cmds[0].name)
# print(ac.apps[0].cmds[1].name)
# print(ac.apps[1].cmds[0].name)
# print(ac.apps[1].cmds[1].name)
