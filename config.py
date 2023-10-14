import yaml

class app:
    def __init__(self,name):
        self.name = name
        self.cmds = []
        self.cur_cmd = 0

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
        out = self.name+':'
        for cmd in self.cmds:
            out=out+'\r\n'+cmd.name+' -> '+cmd.command
        return f"{out}"
    

class config:
    def __init__(self,config):
        self.apps = []
        with open(config, 'r') as file:
            docs = yaml.safe_load_all(file)
            for doc in docs:
                # self.app_count = self.app_count+1
                self.laod_app(doc)

    def laod_app(self, doc):
        for name in dict.fromkeys(doc):
            # print(name)
            ap = app(name)
            for cmds in dict.fromkeys(doc[name]):
                # print(' '+cmds+' -> '+doc[name][cmds]['cmd'])
                cmd = app(cmds)
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
