import yaml # pip install pyyaml
from dotenv import load_dotenv # pip install python-dotenv
import requests # pip install requests 
# if testing on a non-Pi device, comment out this line and replace the door sensor data with a test value
import RPi.GPIO as GPIO # pip install rpio-lgpio
from datetime import datetime
import time, sys, json, glob, signal, os, threading

CHANNEL_ID = None 
DISCORD_TOKEN = None 
DISCORD_URL = 'https://discord.com/api/v10'

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
    """ Thread function to read temperature at a fixed interval. """
    while True:
        data['t'] = read_temp() if hasTemp else None
        time.sleep(interval)

def main():
    global door_count
		
    CONFIG = config_yaml()

    # setup door sensor
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(CONFIG['door_sensor_pin'], GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(CONFIG['door_sensor_pin'], GPIO.BOTH, callback=door_callback, bouncetime=300)

    # setup discord bot
    config_discordbot()
    '''Method that will send alert to discord when a door has been left open	
    send_alert_to_bot(CONFIG)
    '''

    data = {
        'p': CONFIG['fridge_id'],  # Fridge ID
        'd': 0,  # Door count
        't': None  # Temperature
    }

    # Start a thread to monitor temperature
    # door['t'] is set in this method
    temp_thread = threading.Thread(target=monitor_temperature, args=(CONFIG['interval_seconds'], data), daemon=True)
    temp_thread.start()

    print(f"{timestamp()} Monitoring fridge...")

	# Start the module loop
    while True:
        # PACKAGE SENSOR DATA FOR SENDING
        with door_lock:
            data['d'] = door_count # number of times the door was opened since the last request.
            door_count = 0


        # SEND THE DATA
        print(f"{timestamp()} Sending: {data}")
        res = requests.post(CONFIG['server'],json=data)
        if res.status_code >= 400:
            print(f"{timestamp()} Error sending data: {data}")

        # PRINT RESPONSE
        print(f"{timestamp()} Response: {res.status_code}\n\n{res.text}")

        # wait until the next interval
        time.sleep(CONFIG['interval_seconds'])

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

def config_discordbot():
    try :
	    #Load information from .env and checks to see if .env is configured correctly for bot
        global CHANNEL_ID, DISCORD_TOKEN
        load_dotenv()
        CHANNEL_ID = os.getenv('channel_id')
        DISCORD_TOKEN = os.getenv('token')

        if CHANNEL_ID is None or DISCORD_TOKEN is None:
            printerr("Error: either the channel id or discord token is missing")

    except AttributeError as e:
        print(f'{e}')
        sys.exit(1)
    except Exception as e:
        print(f'An error has occured: {e}')

def send_alert_to_bot(CONFIG):
	global DISCORD_URL, CHANEEL_ID
	
	#Sends this message to discord channel
	payload = {
		'content' : 'The fridge has been left open'
		}
		
	DISCORD_URL += f'/channels/{CHANNEL_ID}/messages'
	header = CONFIG['headers']['Discord_header']
	header['User-Agent'] = header['User-Agent'].replace('${user-agent}', os.getenv('user_agent'))
	header['Authorization'] = header['Authorization'].replace('${token}', os.getenv('token'))

	try:
		response = requests.post(DISCORD_URL, headers=header, json=payload)
		if response.status_code != 200 :
			raise Exception(f'{response.status_code}\n\n{response.text}')
	except Exception as e: 
		print(f'\n{e}\n')

if __name__ == "__main__":
    main()
