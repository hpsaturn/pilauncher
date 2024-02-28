import time
import subprocess
import threading

from gui import GuiManager
from display import Display

import RPi.GPIO as GPIO

BTNLFT = 23
BTNRGT = 6

onAppStatusTask = False
onSystemStatsTask = False
isBtnRgtPresed = False
isBtnLftPresed = False
onStats = False

# GUI Apps Manager
gui = GuiManager()
cfg = gui.getConfig()
dsp = Display()

def showMain():
    dsp.showString(gui.showApp())

def updateAppStatus():
    if gui.getAppStatusCmd() != None:
        dsp.showStatus(gui.am.getCurrentApp().status)

def runAction():
    global isBtnRgtPresed
    msg=gui.runAction()
    if 'exec::' in msg:
        cmd=msg.lstrip('exec::')
        print("exec: "+cmd)
        if cmd == 'stats':
            dsp.showStatus("loading..")
            global onStats
            onStats = True
            gui.runBack()
            return
        try:
            dsp.showStatus("loading..")
            cmdmsg = subprocess.check_output(cmd, shell=True).decode("utf-8")
            print("exec_msg: "+cmdmsg)
            dsp.showString(gui.runBack())
        except:
            dsp.showString('exec fail')
    else:
        dsp.showString(msg)
        dsp.showStatus(gui.getAppStatus())
    isBtnRgtPresed = False

def systemStatsThread():
    global onSystemStatsTask
    global isBtnRgtPresed
    # skip if display is off (power consumption improvement)
    if not dsp.disp.power:
        onSystemStatsTask = False
        isBtnRgtPresed = False
        return
    
    app = gui.am.getCurrentApp()
    lines = []
    for info_cmd in app.info_cmds:
        lines.append(str(subprocess.check_output(info_cmd, shell=True).decode("utf-8")))
    dsp.showInfoLines(lines)

    time.sleep(cfg.info_refresh_rate)
    onSystemStatsTask = False
    isBtnRgtPresed = False

def startSystemStatsTask():
    global onSystemStatsTask
    onSystemStatsTask = True
    # Launch app status refresh thread
    thr = threading.Thread(target=systemStatsThread)
    thr.start()

def appStatusThread():
    global onAppStatusTask
    if not dsp.disp.power and gui.am.getAppsStatusCount() > 0:
        onAppStatusTask = False
        return
    try:
        for app in gui.am.getAppsStatusList():
            status = str(subprocess.check_output(app.sta_cmd, shell=True).decode("utf-8"))
            print(app.name+' new status: '+status)
            app.status=status
        updateAppStatus()
        time.sleep(cfg.status_refresh_rate)
    except:
        print("status refresh fails!")
    onAppStatusTask = False

def startAppStatusTask():
    global onAppStatusTask
    onAppStatusTask = True
    # Launch app status refresh thread
    thr = threading.Thread(target=appStatusThread)
    thr.start()

def btn_left_cb(button):
    global isBtnLftPresed
    if not isBtnLftPresed and GPIO.input(button) == GPIO.LOW:
        isBtnLftPresed = True 
        print("Button LEFT pressed.")
        if not dsp.disp.power:
            dsp.powerOffTimerReset()
            isBtnLftPresed = False
            return
        global onStats
        onStats = False
        dsp.showString(gui.showNextApp())
        dsp.showStatus(gui.getAppStatus())
        dsp.powerOffTimerReset()
        isBtnLftPresed = False

def btn_right_cb(button):
    global isBtnRgtPresed
    if not isBtnRgtPresed and GPIO.input(button) == GPIO.LOW:
        isBtnRgtPresed = True
        print("Button RIGHT pressed.")
        if not dsp.disp.power:
            dsp.powerOffTimerReset()
            isBtnRgtPresed = False
            return
        global onStats
        onStats = False
        runAction()
        dsp.powerOffTimerReset()

if __name__ == '__main__':
    # GPIO buttons setup
    print('Starting Raspi App Launcher ...')
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BTNLFT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(BTNRGT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(BTNLFT, GPIO.BOTH, callback=btn_left_cb, bouncetime=10)
    GPIO.add_event_detect(BTNRGT, GPIO.BOTH, callback=btn_right_cb, bouncetime=10)

    # Show initial app
    showMain()
    print('Startup complete')

    # Main loop:
    while True:
        
        if onStats and not onSystemStatsTask:
            startSystemStatsTask()
        if not onStats and not onAppStatusTask:
            startAppStatusTask()
            
        if cfg.auto_screen_off:
            dsp.powerOffTimerLoop(cfg.screen_time_off)

        time.sleep(1)
 
