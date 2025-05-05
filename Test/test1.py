#import RPi.GPIO as GPIO
import time
from gpiozero import LED

led = LED(17)
#pin = 17
#GPIO.setmode(GPIO.BOARD)
#GPIO.setup(pin, GPIO.OUT)

xd = 10

while xd > 0:
	led.on()
	time.sleep(1)
	led.off()
	time.sleep(1)
	xd = xd - 1
#GPIO.cleanup()
