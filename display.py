import time
import adafruit_ssd1306
import board
import digitalio
import threading

from PIL import Image, ImageDraw, ImageFont

class Display:

    WIDTH = 128
    HEIGHT = 32  # Change to 64 if needed

    def __init__(self):
        # Create the I2C interface.
        i2c = board.I2C()
        # Define the Reset Pin
        oled_reset = digitalio.DigitalInOut(board.D4)
        self.disp = adafruit_ssd1306.SSD1306_I2C(self.WIDTH, self.HEIGHT, i2c, addr=0x3C, reset=oled_reset)
        # timer for auto disp off
        self.timer_screen = time.time()
        # general semaphore
        self.mutex = threading.Lock()

        # Clear display.
        self.disp.fill(0)
        self.disp.show()

        # Create blank image for drawing.
        self.w = self.disp.width
        self.h = self.disp.height
        self.image = Image.new("1", (self.w, self.h))

        # Get drawing object to draw on image.
        self.draw = ImageDraw.Draw(self.image)

        # Draw a black filled box to clear the image.
        self.draw.rectangle((0, 0, self.w, self.h), outline=0, fill=0)

        #padding
        self.top = -2
        self.x = 0

        # Load default fonts
        self.fntS = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 9) 
        self.fntM = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11) 
        self.fntB = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18) 

    def showString(self, msg):
        self.mutex.acquire()
        self.draw.rectangle((0, 0, self.w, self.h), outline=0, fill=0)
        self.draw.text((self.x, self.top + 0), msg[:12], font=self.fntB, fill=255)
        self.disp.image(self.image)
        self.disp.show()
        self.mutex.release()

    def showStatus(self, msg):
        self.mutex.acquire()
        self.draw.rectangle((0, 18, self.w-1, self.h-1), outline=0, fill=0)
        self.draw.text((self.x, self.top + 22), msg[:21], font=self.fntM, fill=255)
        self.disp.image(self.image)
        self.disp.show()
        self.mutex.release()

    def showInfoLines(self, lines):
        self.mutex.acquire()
        self.draw.rectangle((0, 0, self.w, self.h), outline=0, fill=0)
        pos = 0
        for line in lines:
            self.draw.text((self.x, self.top + pos), line[:21], font=self.fntS, fill=255)
            pos = pos + 8
        self.disp.image(self.image)
        self.disp.show()
        self.mutex.release()

    def powerOffTimerReset(self):
        self.timer_screen = time.time()
        if not self.disp.power:
            self.disp.poweron()

    def powerOffTimerLoop(self, time_off):
        if not self.disp.power:
            return
        if time.time() - self.timer_screen > time_off:
            self.disp.poweroff()
