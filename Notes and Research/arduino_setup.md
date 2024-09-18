# Setting up the Arduino Development Environment

## Hardware and software
[LoRa Board that we used](https://www.amazon.com/dp/B076MSLFC9/ref=sspa_dk_detail_0?psc=1&pd_rd_i=B076MSLFC9&pd_rd_w=5rwFT&content-id=amzn1.sym.953c7d66-4120-4d22-a777-f19dbfa69309&pf_rd_p=953c7d66-4120-4d22-a777-f19dbfa69309&pf_rd_r=32W9SXEYE5R034EX0BZ8&pd_rd_wg=GpSNP&pd_rd_r=c83327df-7025-4040-92db-4c535a094845&s=pc&sp_csd=d2lkZ2V0TmFtZT1zcF9kZXRhaWwy)

[Download the Arduino IDE](https://www.arduino.cc/en/software)

[Download the Meshtastic Library](https://www.arduino.cc/reference/en/libraries/meshtastic/)

[Follow the Meshtastic Instructions](https://meshtastic.org/docs/getting-started/serial-drivers/esp32/)

## Driver installation

USB Driver for the linked board: [CP210X USB to UART bridge - Download](https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers)

Go to downloads, and download the drivers for your OS. 

**For MacOS**

1. unzip the file that downloaded and run the install `.app` file that downloaded.
2. Follow the wizard to install the driver
3. The extension may be automatically blocked by MacOS. To unblock, go to System Settings -> Privacy & Security
4. There should be a notice that says "Some system software requires your attention before it can be used". Click "Details..."
5. Enable "CP210xVCPDriver.app"
6. The install process should show as successful

**But wait, there's more!**

7. We need to check that the serial driver installation worked. `Apple Menu  > hold down the option key > System Information > Hardware > USB`, and `CP2102 USB to UART Bridge Controller` should be somewhere in the list

## Flashing the firmware

[Follow the instructions](https://meshtastic.org/docs/getting-started/flashing-firmware/esp32/) for flashing the device with Meshtastic firmware.

1. Visit [https://flasher.meshtastic.org](https://flasher.meshtastic.org/) in Chrome or Edge. [Link to GitHub for flasher](https://github.com/meshtastic/web-flasher).
2. Make sure the device is plugged in to your computer
3. Select the following configurations:
    - Device: Heltec V3
    - Firmware: the latest **stable** version (`2.4.2.5b45303 Beta`) at the time of writing this
    - **NOTE:** We may need to ensure that we continue to use the *same* version, but for now let's stick with always using the latest, especially during the development phase. 

**NOTE:** The steps after this point, I'm not sure if the configuration I selected was optimal/correct, but it is what worked. 

4. Click "Flash". The browser will ask you to connect to a serial port, and I selected "CP2102 USB to UART Bridge Controller (cu.usbserial-0001)".
5. Click the button by step 1 that says "1200bps Reset"
6. Baud rate: 115200
7. Turn on "Full Erase and Intall"
8. Click the big green button "Erase Flash and Install". Wait a couple of minutes for the LoRa device to turn off, and update. When I did it, it turned back on after a while. **Some instructions indicate that you need to press the physical `RST` button on the device**. 

