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
        status = subprocess.check_output(gui.getAppStatusCmd(), shell=True).decode("utf-8")
        print(gui.am.getCurrentApp().name+' status: '+status)
        gui.am.getCurrentApp().status=status
        dsp.showStatus(status)

def runAction():
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
            updateAppStatus()
             
        except:
            dsp.showString('exec fail')
    else:
        dsp.showString(msg)
        dsp.showStatus(gui.getAppStatus())

def systemStatsThread():
    global onSystemStatsTask
    # skip if display is off (power consumption improvement)
    if not dsp.disp.power:
        onSystemStatsTask = False
        return
    
    # Shell scripts for system monitoring from here:
    # https://unix.stackexchange.com/questions/119126/command-to-display-memory-usage-disk-usage-and-cpu-load
    cmd = "hostname -I | cut -d' ' -f1"
    IP = subprocess.check_output(cmd, shell=True).decode("utf-8")
    cmd = 'cut -f 1 -d " " /proc/loadavg'
    CPU = subprocess.check_output(cmd, shell=True).decode("utf-8")
    cmd = "free -m | awk 'NR==2{printf \"Mem: %s/%s MB  %.2f%%\", $3,$2,$3*100/$2 }'"
    MemUsage = subprocess.check_output(cmd, shell=True).decode("utf-8")
    cmd = 'df -h | awk \'$NF=="/"{printf "Disk: %d/%d GB  %s", $3,$2,$5}\''
    Disk = subprocess.check_output(cmd, shell=True).decode("utf-8")

    # Write four lines of text.
    dsp.showFourLines("IP: " + IP, "CPU load: " + CPU, MemUsage, Disk)
    time.sleep(2)
    onSystemStatsTask = False

def startSystemStatsTask():
    global onSystemStatsTask
    onSystemStatsTask = True
    # Launch app status refresh thread
    thr = threading.Thread(target=systemStatsThread)
    thr.start()

def appStatusThread():
    global onAppStatusTask
    if not dsp.disp.power:
        onAppStatusTask = False
        return
    app = gui.am.getNextPendingApp()
    if app != None:
        try:
            status = subprocess.check_output(app.sta_cmd, shell=True).decode("utf-8")
            app.status = status
            print(app.name+' status: '+status)
            if app.name != gui.am.getCurrentApp().name:
                updateAppStatus()
            time.sleep(10)
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

        isBtnRgtPresed = False

# GPIO buttons setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(BTNLFT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BTNRGT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(BTNLFT, GPIO.BOTH, callback=btn_left_cb, bouncetime=10)
GPIO.add_event_detect(BTNRGT, GPIO.BOTH, callback=btn_right_cb, bouncetime=10)

# Show initial app
showMain()
updateAppStatus()

# Main loop:
while True:
    
    if onStats and not onSystemStatsTask:
        startSystemStatsTask()
    if not onStats and not onAppStatusTask:
        startAppStatusTask()
        
    if cfg.auto_screen_off:
        dsp.powerOffTimerLoop(cfg.screen_time_off)

    time.sleep(1)
