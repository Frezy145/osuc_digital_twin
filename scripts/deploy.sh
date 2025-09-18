# Here is the deployment script for the OSUC Digital Twin Project

# Create a daemon service to run python script on startup

# import pro-setup.sh as needed
source pro-setup.sh

# Setup systemd service
SERVICE_FILE="/etc/systemd/system/osuc_digital_twin.service"
echo "⚙️ Setting up systemd service..."
sudo bash -c "cat > $SERVICE_FILE" <<EOL
[Unit]
Description=OSUC Digital Twin Service
After=network.target

[Service]
User=$USER
WorkingDirectory=$(pwd)
ExecStart=$(pwd)/venv/bin/python $(pwd)/app.py
Restart=always

[Install]
WantedBy=multi-user.target
EOL
sudo systemctl daemon-reload
sudo systemctl enable osuc_digital_twin.service
sudo systemctl start osuc_digital_twin.service  