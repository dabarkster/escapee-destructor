import RPi.GPIO as GPIO
import time
import sys
import signal 
# Set Broadcom mode so we can address GPIO pins by number.
GPIO.setmode(GPIO.BCM) 
# This is the GPIO pin number we have one of the door sensor
# wires attached to, the other should be attached to a ground pin. 
YELLOW = 5
BLUE   = 6
GREEN  = 13
WHITE  = 19

GPIO.setup(YELLOW, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(BLUE, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(GREEN, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(WHITE, GPIO.IN, pull_up_down = GPIO.PUD_UP)

def check_wires():
	
	yellow_state = GPIO.input(YELLOW)
	blue_state = GPIO.input(BLUE)
	green_state = GPIO.input(GREEN)
	white_state = GPIO.input(WHITE)

	print(str(yellow_state) + " " + str(blue_state) + " " + str(green_state) + " " + str(white_state))

while True:
	check_wires()