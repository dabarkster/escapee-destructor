#!/usr/bin/python

import time
import datetime
import pygame
import paho.mqtt.client as mqtt #import the client1
from gpiozero import LED
from gpiozero import Button
from Adafruit_LED_Backpack import SevenSegment

pygame.init()

add10 = False
start = False
runit = True
x = 100

topic        = "escapee/destructor"
topicAll     = topic + "/#"
topicStatus  = topic + "/status"
topicCommand = topic + "/command"
topicTimer   = topic + "/timer"
broker_address="192.168.56.220" 
client = mqtt.Client("client") #create new instance

photo_path = '/home/pi/Pictures'
sfx_path   = '/home/pi/Music'
sfx_file = sfx_path + "/beep.wav"
sfx_beep = pygame.mixer.Sound(sfx_file)
#led = LED(17)
#print(led.value)


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

    while runit == True:
        if start == False:
            #butt = Button(17)
            #print(led)
            #if (led.value == 1):
            #    print ("Pressed")
            #    start = True
            time.sleep(1)
        else:
            client.publish(topicStatus,"Running")
            while x >= 0:
                segment.set_colon(1)
                segment.write_display()
                time.sleep(0.5) #used to blink colon
                strTime = formatTime(x)
                client.publish(topicTimer,strTime)
                displayTime(x)
                sfx_beep.play()
                if add10 == True:
                    x = x + 10
                    add10 = False #add only once
                    #print(x)
                
                if start == False:
                    break
                x -= 1
                
    client.loop_stop()
    client.disconnect()

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
    
    msg.payload = msg.payload.decode("utf-8")

    if "add" in msg.payload:
        client.publish(topicStatus,"Adding Time")  # can use node to write this?
        #add10 = True
        
    if "go" in msg.payload:
        client.publish(topicStatus,"Running")
        start = True
    
    if "reset" in msg.payload:
        runit = True
        start = False
        x = 100
        client.publish(topicStatus,"Resetting")
        strTime = formatTime(x)
        client.publish(topicTimer,strTime)
        client.publish(topicStatus,"Waiting")
    
    if "end" in msg.payload:
        client.publish(topicStatus,"Done")
        runit = False
        start = False
    
    print("Payload: " + msg.payload)


if __name__ == "__main__":
    main()
