import yaml # pip install pyyaml
import time, sys, json, requests
from dotenv import load_dotenv 
import os

CHANNEL_ID = None 
DISCORD_TOKEN = None 
DISCORD_URL = 'https://discord.com/api/v10'

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
        data['test'] = 5

        # SEND THE DATA
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
            raise AttributeError("Error: either the channel id or discord token in missing")

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
