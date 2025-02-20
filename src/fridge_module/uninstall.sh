#!/bin/bash

SERVICE_NAME="fridge_module"
INSTALL_DIR="/opt/fridge_module"
SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME.service"

echo "Uninstalling $SERVICE_NAME..."

# disable the systemd service
sudo systemctl disable "$SERVICE_NAME"
# remove the service file
sudo rm "$SERVICE_FILE"
sudo systemctl daemon-reload

# UNINSTALL THE PACKAGE IN /OPT
sudo rm -rf "$INSTALL_DIR"

echo "$SERVICE_NAME uninstalled"
