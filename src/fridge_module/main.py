import yaml # pip install pyyaml
import time, sys, json, requests, glob
from dotenv import load_dotenv 
import os

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

def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines

def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0
        return temp_c, temp_f

def main():
		
    CONFIG = config_yaml()
    config_discordbot()
    '''Method that will send alert to discord when a door has been left open	
    send_alert_to_bot(CONFIG)
    '''
	# Start the module loop
    while True:
        data = {}
        # PACKAGE SENSOR DATA FOR SENDING

        data['p'] = CONFIG['fridge_id'] # unique id for the fridge
        data['d'] = 20 # number of times the door was opened since the last request.
        data['t'] = read_temp()[1] if hasTemp else None # current temperature of the fridge

        # SEND THE DATA
        print(data)
        res = requests.post(CONFIG['server'],json=data)
        if res.status_code >= 400:
            print(f"Error sending data: {data}")

        # PRINT RESPONSE
        print(f"Response: {res.status_code}\n\n{res.text}")

        # wait until the next interval
        time.sleep(CONFIG['interval_seconds'])

def config_yaml():
    # load module configuration parameters
    try: # load defaults from default.yaml
        with open('default.yaml', 'r') as def_config_file: 
            config = yaml.safe_load(def_config_file)
    except Exception as e:
        print(f"An error occurred while opening the default configuration file: {e}")
        print("Unable to start refrigerator module without default parameters. Exiting...")
        sys.exit(1)
    try: # override any defaults found in config.yaml
        with open('config.yaml', 'r') as config_file:
            new_params = yaml.safe_load(config_file)
            for key, value in new_params.items():
                config[key] = value
    except Exception as e:
        print(f"An error occurred while opening the configuration file: {e}")
        print("Running with default parameters.")

    # make sure that we have all the necessary parameters
    necessary_params = ['interval_seconds', 'server']
    missing_params = False
    for param in necessary_params:
        if param not in config:
            missing_params = True
            print(f"Missing Configuration Parameter: {param}")
    if missing_params:
        print("Paramters are missing from the default configuratiion file. Module will not run until these parameters are set.")
        print("Exiting...")
        sys.exit(1)
    print(f"Module Configuration: \n{config}")
    return config

def config_discordbot():
    try :
	    #Load information from .env and checks to see if .env is configured correctly for bot
        global CHANNEL_ID, DISCORD_TOKEN
        load_dotenv()
        CHANNEL_ID = os.getenv('channel_id')
        DISCORD_TOKEN = os.getenv('token')

        if CHANNEL_ID is None or DISCORD_TOKEN is None:
            raise AttributeError("Error: either the channel id or discord token is missing")

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
