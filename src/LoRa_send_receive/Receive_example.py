import meshtastic, sys, json
import meshtastic.serial_interface
from pubsub import pub

host = "/dev/ttyUSB0"
if len(sys.argv) > 1:
    host = sys.argv[1]

def onReceive(packet, interface):
    data = packet['decoded']['payload'].decode('utf-8')
    print(f"Message received: {data}")

# Connect to the Meshtastic device
interface = meshtastic.serial_interface.SerialInterface(host)

# Subscribe to the 'meshtastic.receive' topic
pub.subscribe(onReceive, "meshtastic.receive")

# Keep the script running to listen for messages
while True:
    pass