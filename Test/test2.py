#import RPi.GPIO as GPIO
import time
from gpiozero import Button
from signal import pause
button = Button(2)
#led = LED(17)
#pin = 17
#GPIO.setmode(GPIO.BOARD)
#GPIO.setup(pin, GPIO.OUT)

#xd = 10

def lol():
	print("XD")

def xd():
	print("LOL")


button.when_pressed = lol
button.when_released = xd
#pause()
while True:
	pass
	#time.sleep(1)
	#print("Xd")

