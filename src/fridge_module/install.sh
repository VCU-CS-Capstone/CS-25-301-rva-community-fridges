#!/bin/bash

SERVICE_NAME="fridge_module"
INSTALL_DIR="/opt/fridge_module"
SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME.service"
VENV_DIR="$INSTALL_DIR/venv"

echo "Installing $SERVICE_NAME..."

# Create the installation directory
sudo mkdir -p "$INSTALL_DIR"

# Copy files
sudo cp -r ./* "$INSTALL_DIR"
sudo chmod -R 755 "$INSTALL_DIR" #grant perms to executables in the package

# Set up the virtual environment
echo "Setting up virtual environment..."
sudo apt update
sudo apt install -y python3-venv
sudo python3 -m venv "$INSTALL_DIR/venv"

# Install dependencies
echo "Installing Python dependencies..."
sudo "$VENV_DIR/bin/pip" install --upgrade pip
if [ -f "$INSTALL_DIR/requirements.txt" ]; then
	sudo "$VENV_DIR/bin/pip" install -r "$INSTALL_DIR/requirements.txt"
fi

# Move and enable the systemd service
sudo cp "$INSTALL_DIR/$SERVICE_NAME.service" "$SERVICE_FILE"
sudo chmod 644 "$SERVICE_FILE"

sudo systemctl daemon-reload
sudo systemctl enable "$SERVICE_NAME"
sudo systemctl start "$SERVICE_NAME"

echo "$SERVICE_NAME installed and running!"

