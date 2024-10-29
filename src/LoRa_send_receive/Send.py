import meshtastic
import meshtastic.serial_interface
import sys

host = "/dev/ttyUSB0"
if len(sys.argv) > 1:
    host = sys.argv[1]

# Connect to the Meshtastic device
interface = meshtastic.serial_interface.SerialInterface(host)  # Replace with your port

# Function to send a message
def send_message(message):
    interface.sendText(message)
    print(f"Message sent: {message}")


# Example of sending a message
try:
    message = "Quack"
    send_message(message)
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    # Close the interface when done
    interface.close()
