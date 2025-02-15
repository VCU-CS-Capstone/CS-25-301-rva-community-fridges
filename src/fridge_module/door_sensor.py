import RPi.GPIO as GPIO
import time, sys, signal

DOOR_SENSOR_PIN=23

GPIO.setmode(GPIO.BCM)

GPIO.setup(DOOR_SENSOR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def door_callback(channel):
    if GPIO.input(DOOR_SENSOR_PIN):
        print("Opened")
    else: 
        print("Closed")
# 'bouncetime' is used to prevent switch bouncing, which is when 
# a mechanical switch (like a door sensor) rapidly toggles between 
# states due to vibrations or imperfections in the contact surfaces.
GPIO.add_event_detect(DOOR_SENSOR_PIN, GPIO.BOTH, callback=door_callback, bouncetime=300)

try:
    print("Monitoring door sensor...")
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Exiting...")
    GPIO.cleanup()


