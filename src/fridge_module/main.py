import yaml # pip install pyyaml
from dotenv import load_dotenv # pip install python-dotenv
import requests # pip install requests 
# if testing on a non-Pi device, comment out this line and replace the door sensor data with a test value
import RPi.GPIO as GPIO # pip install rpio-lgpio
from datetime import datetime
import time, sys, json, glob, signal, os, threading
import logging


# configure the temperature sensor
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')
# Unsure if this logic will need to change if the door sensor is added. 
try:
    device_folder = device_folder[0]
    hasTemp = True
except IndexError:
    device_folder = ""
    hasTemp = False
device_file = device_folder + '/w1_slave'

door_count = 0  # Shared variable for door open count
door_lock = threading.Lock()  # Ensures thread safety when updating door_count

def timestamp():
    return f"[{datetime.now().strftime('%m-%d-%y %H:%M')}]"

def printerr(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def read_temp_raw():
    with open(device_file, 'r') as f:
        return f.readlines()

def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0

        return temp_c * 9.0 / 5.0 + 32.0 # convert to F
    return None # no temperature sensor

def door_callback(channel):
    """ Callback function for door sensor. """
    global door_count
    with door_lock:
        if GPIO.input(channel):  # Door opened
            door_count += 1
            print(f"{timestamp()} Door opened {door_count} times since last transmission.")
        else:
            print(f"{timestamp()} Door closed.")

def monitor_temperature(interval, data):
    logging.basicConfig(filename = 'temperature_log.log', level=logging.INFO)
    """ Thread function to read temperature at a fixed interval. """
    alert_lock = True 
    while True:
        data['t'] = read_temp() if hasTemp else None
        #logging.info(data['t'])
        if data['t'] > 86.0 and alert_lock:
            alert_lock = False
            res = requests.get(url='https://al6mmf5bsd.execute-api.us-east-1.amazonaws.com/prod/api/sendAlert',
                     headers= {'content-type':'application/json'}
                    )
            if res.status_code == 200:
                print(f"{timestamp()} Response: {res.status_code}\n\n{res.text}") 
            else :
                print(res.text)
        elif data['t'] <= 86.0 and not alert_lock:
            alert_lock = True
        time.sleep(.2)

def main():
    global door_count
		
    CONFIG = config_yaml()

    # setup door sensor
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(CONFIG['door_sensor_pin'], GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(CONFIG['door_sensor_pin'], GPIO.BOTH, callback=door_callback, bouncetime=300)

    data = {
        'p': 14,  # Fridge ID
        'd': 0,  # Door count
        't': None  # Temperature
    }

    # Start a thread to monitor temperature
    # door['t'] is set in this method
    temp_thread = threading.Thread(target=monitor_temperature, args=(CONFIG['interval_seconds'], data), daemon=True)
    temp_thread.start()

    print(f"{timestamp()} Monitoring fridge...")

	# Start the module loop
    transmit_data = False
    while True:
        # PACKAGE SENSOR DATA FOR SENDING
        
        # ONLY SEND DATA IF FRIDGE DOOR HAS BEEN OPEN 
        
            
        with door_lock:
            if door_count != 0:
                data['d'] = door_count # number of times the door was opened since the last request.
                door_count = 0
                transmit_data = True 
 
        if transmit_data:

<<<<<<< Updated upstream
        # SEND THE DATA
        # WILL ONLY SEND IF DOOR HAS BEEN OPEN
        if door_count > 0 :
=======
            # SEND THE DATA
>>>>>>> Stashed changes
            print(f"{timestamp()} Sending: {data}")
            res = requests.post(CONFIG['server'],json=data)
            if res.status_code >= 400:
                print(f"{timestamp()} Error sending data: {data}")
<<<<<<< Updated upstream
    
            # PRINT RESPONSE
            print(f"{timestamp()} Response: {res.status_code}\n\n{res.text}")
    
            # wait until the next interval
        time.sleep(CONFIG['interval_seconds'])
=======
     
            # PRINT RESPONSE
            print(f"{timestamp()} Response: {res.status_code}\n\n{res.text}") 
            
            transmit_data = False
            # wait until the next interval
            time.sleep(1)
>>>>>>> Stashed changes

def config_yaml():
    # load module configuration parameters
    try: # load defaults from default.yaml
        with open('default.yaml', 'r') as def_config_file: 
            config = yaml.safe_load(def_config_file)
    except Exception as e:
        print(f"{timestamp()} An error occurred while opening the default configuration file: {e}")
        print(f"{timestamp()} Unable to start refrigerator module without default parameters. Exiting...")
        sys.exit(1)
    try: # override any defaults found in config.yaml
        with open('config.yaml', 'r') as config_file:
            new_params = yaml.safe_load(config_file)
            for key, value in new_params.items():
                config[key] = value
    except Exception as e:
        print(f"{timestamp()} An error occurred while opening the configuration file: {e}")
        print(f"{timestamp()} Running with default parameters.")

    # make sure that we have all the necessary parameters
    necessary_params = ['interval_seconds', 'server']
    missing_params = False
    for param in necessary_params:
        if param not in config:
            missing_params = True
            print(f"{timestamp()} Missing Configuration Parameter: {param}")
    if missing_params:
        print(f"{timestamp()} Paramters are missing from the default configuratiion file. Module will not run until these parameters are set.")
        print(f"{timestamp()} Exiting...")
        sys.exit(1)
    print(f"{timestamp()} Module Configuration: \n{config}")
    return config

<<<<<<< Updated upstream
=======


>>>>>>> Stashed changes
if __name__ == "__main__":
    main()
