import time
import subprocess
import threading
import board
import digitalio
import adafruit_ssd1306
from PIL import Image, ImageDraw, ImageFont
from gui import GuiManager

WIDTH = 128
HEIGHT = 32  # Change to 64 if needed
BORDER = 1

import RPi.GPIO as GPIO
BTNLFT = 23
BTNRGT = 6

isBtnRgtPresed = False
isBtnLftPresed = False
onStats = False
onStatusTask = False

# GUI Apps Manager
gm = GuiManager()

# Create the I2C interface.
i2c = board.I2C()
# Define the Reset Pin
oled_reset = digitalio.DigitalInOut(board.D4)
disp = adafruit_ssd1306.SSD1306_I2C(WIDTH, HEIGHT, i2c, addr=0x3C, reset=oled_reset)

# Clear display.
disp.fill(0)
disp.show()

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
width = disp.width
height = disp.height
image = Image.new("1", (width, height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0, 0, width, height), outline=0, fill=0)

# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
padding = -2
top = padding
bottom = height - padding
# Move left to right keeping track of the current x position for drawing shapes.
x = 0

# Load default font.
font = ImageFont.load_default()
fontBig = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)

def showString(msg):
    draw.rectangle((0, 0, width, height), outline=0, fill=0)
    draw.text((x, top + 0), msg, font=fontBig, fill=255)
    disp.image(image)
    disp.show()

def showStatus(msg):
    print("showing status: "+msg)
    draw.rectangle((0, 18, width, height - 1), outline=0, fill=0)
    draw.text((x, top + 25), msg, font=font, fill=255)
    disp.image(image)
    disp.show()

def showMain():
    showString(gm.showApp())

def updateAppStatus():
    if gm.getAppStatusCmd() != None:
        status = subprocess.check_output(gm.getAppStatusCmd(), shell=True).decode("utf-8")
        print(gm.am.getCurrentApp().name+' status: '+status)
        gm.am.getCurrentApp().status=status
        showStatus(status)

def runAction():
    msg=gm.runAction()
    if 'exec::' in msg:
        cmd=msg.lstrip('exec::')
        print("exec: "+cmd)
        if cmd == 'stats':
            global onStats
            onStats = True
            showString(gm.runBack())
            return
        try:
            showStatus("loading..")
            cmdmsg = subprocess.check_output(cmd, shell=True).decode("utf-8")
            print("exec_msg: "+cmdmsg)
            showString(gm.runBack())
            updateAppStatus()
             
        except:
            showString('exec fail')
    else:
        showString(msg)

def dispLftAction():
    showString(gm.showNextApp())
    showStatus(gm.getAppStatus())
    global isBtnLftPresed
    isBtnLftPresed = False

def dispRgtAction():
    runAction()
    global isBtnRgtPresed
    isBtnRgtPresed = False

def dispStatsLoop():
    # Draw a black filled box to clear the image.
    draw.rectangle((0, 0, width, height), outline=0, fill=0)

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

    draw.text((x, top + 0), "IP: " + IP, font=font, fill=255)
    draw.text((x, top + 8), "CPU load: " + CPU, font=font, fill=255)
    draw.text((x, top + 16), MemUsage, font=font, fill=255)
    draw.text((x, top + 25), Disk, font=font, fill=255)

    # Display image.
    disp.image(image)
    disp.show()

def btn_left_cb(button):
    global isBtnLftPresed
    if not isBtnLftPresed and GPIO.input(button) == GPIO.LOW:
        print("Button LEFT pressed.")
        isBtnLftPresed = True
        global onStats
        onStats = False

def btn_right_cb(button):
    global isBtnRgtPresed
    if not isBtnRgtPresed and GPIO.input(button) == GPIO.LOW:
        print("Button RIGHT pressed.")
        isBtnRgtPresed = True
        global onStats
        onStats = False

def statusThread():
    global onStatusTask
    app = gm.am.getNextPendingApp()
    if app != None:
        try:
            status = subprocess.check_output(app.sta_cmd, shell=True).decode("utf-8")
            app.status = status
            print(app.name+' status: '+status)
            updateAppStatus()
            time.sleep(10)
        except:
            print("status refresh fails!")
        onStatusTask = False

def startStatusTask():
    global onStatusTask
    onStatusTask = True
    # Launch app status refresh thread
    x = threading.Thread(target=statusThread)
    x.start()

# GPIO setup
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
    
    if isBtnLftPresed:
        dispLftAction()
    elif isBtnRgtPresed:
        dispRgtAction()

    if not onStatusTask:
        startStatusTask()

    if onStats:
        dispStatsLoop()
        time.sleep(2)
    else:
        time.sleep(0.500)
