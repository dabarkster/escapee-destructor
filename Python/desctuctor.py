#!/usr/bin/python

import time
import datetime
import pygame
import paho.mqtt.client as mqtt #import the client1
from gpiozero import LED
from gpiozero import Button
from Adafruit_LED_Backpack import SevenSegment
import RPi.GPIO as GPIO


GPIO.setmode(GPIO.BCM) 
# This is the GPIO pin number we have one of the door sensor
# wires attached to, the other should be attached to a ground pin. 
WHITE   = 5
BLUE    = 6
GREEN   = 13
YELLOW  = 19

GPIO.setup(YELLOW, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(BLUE, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(GREEN, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(WHITE, GPIO.IN, pull_up_down = GPIO.PUD_UP)

wire_state = 0
phase = 0



pygame.init()

add10 = False
start = False
runit = True
starttime = 3600
x = starttime

topic        = "escapee/destructor"
topicAll     = topic + "/#"
topicStatus  = topic + "/status"
topicCommand = topic + "/command"
topicTimer   = topic + "/timer"
topicWarning = topic + "/warning"
topicPhase   = topic + "/phase"

broker_address="192.168.56.220" 
client = mqtt.Client("client") #create new instance

#led = LED(17)
#print(led.value)

broker = "192.168.56.220"
port=1883

photo_path = '/home/pi/Pictures/'
font_path  = "/home/pi/escapee-destructor/Fonts/"
sound_path = "/home/pi/escapee-destructor/Sounds/"
music_path = "/home/pi/escapee-destructor/Music/"
photo_path = '/home/pi/Pictures'
#sound_file = sound_path + "/beep.wav"
#sfx_beep = pygame.mixer.Sound(sound_file)

segment = SevenSegment.SevenSegment(address=0x71)
# Initialize the display. Must be called once before using the display.
segment.begin()
segment.set_colon(1)             

def main():
    global add10
    global start
    global runit
    global x

    client.on_connect = on_connect
    client.message_callback_add(topicCommand, on_message_command)
    client.on_message = on_message
    client.connect(broker_address, 1883, 60) #connect to broker
    client.loop_start()
    client.publish(topicStatus,"Starting")#publish
    time.sleep(1) #slight delay to show starting status
    client.publish(topicStatus,"Waiting")
    while True:

        print("runit?")
        time.sleep(1)
        while runit == True:
            print("start?")
            if start == False:
                #butt = Button(17)
                #print(led)
                #if (led.value == 1):
                #    print ("Pressed")
                #    start = True
                time.sleep(1)
                print("sleeping")
            else:
                client.publish(topicStatus,"Running")
                while x >= 0:
                    phase = check_wires()
                    if phase == -1:
                        runit = False
                        start = False
                        print("BOOM")
                        client.publish(topicStatus,"BOOM")
                    elif phase == 4:
                        client.publish(topicStatus,"Winner")

                    segment.set_colon(1)
                    segment.write_display()
                    time.sleep(0.5) #used to blink colon
                    strTime = formatTime(x)
                    client.publish(topicTimer,strTime)
                    displayTime(x)
                    play_mp3("beep")
                    if add10 == True:
                        x = x + 10
                        add10 = False #add only once
                        #print(x)
                    
                    if start == False:
                        break

                    if x == 80:
                        client.publish(topicWarning,"Started")
                    elif x == 45:
                        client.publish(topicWarning,"45")

                    x -= 1
                    if x == 0:
                        client.publish(topicStatus,"BOOM")

                print("while end")
                runit = False

    print("end")
    client.loop_stop()
    client.disconnect()

def check_wires():
    global phase
    global wire_state

    yellow_state = GPIO.input(YELLOW)
    blue_state = GPIO.input(BLUE)
    green_state = GPIO.input(GREEN)
    white_state = GPIO.input(WHITE)
    
    wire_state = 1*int(blue_state) + 2*int(green_state) + 4*int(yellow_state) + 8*int(white_state)
    #print(wire_state)

    if blue_state:
        if wire_state != 1 and phase == 0:
            phase = -1
        else:
            phase = 1

    if green_state:
        if wire_state != 3 and phase != 1:
            phase = -1
        else:
            phase = 2

    if yellow_state:
        if wire_state != 7 and phase != 2:
            phase = -1
        else:
            phase = 3

    if white_state:
        if wire_state != 15 and phase != 3:
            phase = -1
        else:
            phase = 4
 
    client.publish(topicPhase, phase)
    return phase

    #print(str(blue_state) + " " + str(green_state) + " " +str(yellow_state) + " " +  str(white_state))

def play_mp3(file):
    #name = sound_path + "bio" + kid + ".mp3"
    name = sound_path + "/" + file + ".mp3"
    pygame.mixer.music.load(name)
    pygame.mixer.music.play()

def formatTime(x):
    minutes, seconds_rem = divmod(x, 60)
    # use string formatting with C type % specifiers
    # %02d means integer field of 2 left padded with zero if needed
    return "%02d:%02d" % (minutes, seconds_rem)

def displayTime(x):
    minute, second = divmod(x, 60)

    segment.clear()
    # Set hours
    segment.set_digit(0, int(minute / 10))     # Tens
    segment.set_digit(1, minute % 10)          # Ones
    # Set minutes
    segment.set_digit(2, int(second / 10))   # Tens
    segment.set_digit(3, second % 10)        # Ones
    # Toggle colon
    segment.set_colon(0) 
    # Write the display buffer to the hardware.  This must be called to
    # update the actual display LEDs.
    segment.write_display()
 
    # Wait a half second (less than 1 second to prevent colon blinking getting$
    time.sleep(0.5)

def add():
    pass

def daEnd():
    runit = False
    start = False

def on_connect(client, userdata, flags, rc):
  print("Connected with result code " + str(rc))
  client.subscribe(topicAll)

def on_message(client, userdata, msg):
    pass

def on_message_command(client, userdata, msg):
    global add10
    global start
    global runit
    global x
    global phase
    
    msg.payload = msg.payload.decode("utf-8")

    if "add" in msg.payload:
        client.publish(topicStatus,"Adding Time")  # can use node to write this?
        x += 600
        print(x)
        
    if "go" in msg.payload:
        client.publish(topicStatus,"Running")
        start = True
    
    if "pause" in msg.payload:
        client.publish(topicStatus,"Pause")
        runit = True
        if start == True:
            start = False
        else:
             start = True

    if "reset" in msg.payload:
        runit = True
        start = False
        x = starttime
        phase = 0

        client.publish(topicStatus,"Resetting")
        strTime = formatTime(x)
        client.publish(topicTimer,strTime)
        client.publish(topicStatus,"Waiting")
        client.publish(topicPhase, 0)
    
    if "end" in msg.payload:
        client.publish(topicStatus,"Done")
        runit = False
        start = False
    

    print("Payload: " + msg.payload)


if __name__ == "__main__":
    main()
