
#!/bin/bash
set -e
cd ~/actions-runner/_work/osuc_digital_twin/osuc_digital_twin
cp -r src /home/$USER/app

# Répertoire où est ton projet
APP_DIR="/home/$USER/app/src"
PYTHON_BIN="/home/$USER/app/venv/bin/python3"

# Vérifie que main.py existe
if [ ! -f "$APP_DIR/main.py" ]; then
  echo "Erreur: $APP_DIR/main.py introuvable"
  exit 1
fi

# Création des fichiers systemd
echo "Création des services systemd..."

# --- Service pour 6 minutes ---
cat <<EOF | sudo tee /etc/systemd/system/osuc_6min.service > /dev/null
[Unit]
Description=Collecte des sondes et meteo locale toutes les 6 minutes
After=network.target

[Service]
Type=oneshot
WorkingDirectory=$APP_DIR
ExecStart=$PYTHON_BIN $APP_DIR/main.py 6min

[Install]
WantedBy=multi-user.target
EOF

cat <<EOF | sudo tee /etc/systemd/system/osuc_6min.timer > /dev/null
[Unit]
Description=Timer pour osuc_6min.service

[Timer]
OnCalendar=*-*-* *:0/6:00 UTC
Persistent=true
Unit=osuc_6min.service

[Install]
WantedBy=timers.target
EOF

# --- Service pour 1 heure ---
cat <<EOF | sudo tee /etc/systemd/system/osuc_1h.service > /dev/null
[Unit]
Description=Envoi des données chaque heure
After=network.target

[Service]
Type=oneshot
WorkingDirectory=$APP_DIR
ExecStart=$PYTHON_BIN $APP_DIR/main.py 1h

[Install]
WantedBy=multi-user.target
EOF

cat <<EOF | sudo tee /etc/systemd/system/osuc_1h.timer > /dev/null
[Unit]
Description=Timer pour osuc_1h.service

[Timer]
OnCalendar= *:56:00 UTC
Persistent=true
Unit=osuc_1h.service

[Install]
WantedBy=timers.target
EOF

# --- Service pour 1 jour ---
cat <<EOF | sudo tee /etc/systemd/system/osuc_1d.service > /dev/null
[Unit]
Description=Récupération quotidienne des prévisions météo
After=network.target

[Service]
Type=oneshot
WorkingDirectory=$APP_DIR
ExecStart=$PYTHON_BIN $APP_DIR/main.py 1d

[Install]
WantedBy=multi-user.target
EOF

cat <<EOF | sudo tee /etc/systemd/system/osuc_1d.timer > /dev/null
[Unit]
Description=Timer pour osuc_1d.service

[Timer]
OnCalendar=*-*-* 00:03:00 UTC
Persistent=true
Unit=osuc_1d.service

[Install]
WantedBy=timers.target
EOF

# --- Weekly service ---
cat <<EOF | sudo tee /etc/systemd/system/osuc_weekly.service > /dev/null
[Unit]
Description=Mail hebdomadaire avec les données archivees
After=network.target

[Service]
Type=oneshot
WorkingDirectory=$APP_DIR
ExecStart=$PYTHON_BIN $APP_DIR/main.py 1w

[Install]
WantedBy=multi-user.target
EOF
cat <<EOF | sudo tee /etc/systemd/system/osuc_weekly.timer > /dev/null
[Unit]
Description=Timer pour osuc_weekly.service

[Timer]
OnCalendar=Mon *-*-* 00:00:00 UTC
Persistent=true
Unit=osuc_weekly.service

[Install]
WantedBy=timers.target
EOF

# Recharger systemd
echo "Activation des timers..."
sudo systemctl daemon-reload
sudo systemctl restart osuc_6min.timer
sudo systemctl restart osuc_1h.timer
sudo systemctl restart osuc_1d.timer
sudo systemctl restart osuc_weekly.timer
sudo systemctl enable --now osuc_6min.timer
sudo systemctl enable --now osuc_1h.timer
sudo systemctl enable --now osuc_1d.timer
sudo systemctl enable --now osuc_weekly.timer

echo "✅ Tous les services et timers ont été installés et activés."
