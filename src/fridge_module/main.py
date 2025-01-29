import yaml # pip install pyyaml
import time, sys, json, requests
import os


def main():
		
    CONFIG = config_yaml()

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

if __name__ == "__main__":
    main()
