import meshtastic, sys, json
import meshtastic.serial_interface
from pubsub import pub
import codecs

host = "/dev/ttyUSB0"
if len(sys.argv) > 1:
    host = sys.argv[1]

def onReceive(packet, interface):
    data = packet['decoded']['payload'] 
    decoded_data = packet['decoded']['payload'].decode('ascii', errors="replace")
    print(f"Message received: ", end="")
    print(data)
    print("Decoded: ", end="")
    print(decoded_data)

# Connect to the Meshtastic device
interface = meshtastic.serial_interface.SerialInterface(host)

# Subscribe to the 'meshtastic.receive' topic
pub.subscribe(onReceive, "meshtastic.receive")

# Keep the script running to listen for messages
while True:
    pass