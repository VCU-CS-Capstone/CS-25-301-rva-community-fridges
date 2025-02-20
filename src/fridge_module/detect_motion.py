import RPi.GPIO as GPIO
import time

PIN = 18

GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN, GPIO.IN)

print("Motion Sensor Ready...")

motion = False

time.sleep(2)

try:
    while True:
        if GPIO.input(PIN):
            if not motion: # notify change of state
                print("Motion Detected")
            motion = True
        else:
            if motion: # notify change of state
                print("No motion")
            motion = False
            time.sleep(0.01)
except KeyboardInterrupt:
    print("Exiting...")
    GPIO.cleanup()
