import csv
import requests
import time
from datetime import datetime

# Configuración ThingsBoard
# THINGSBOARD_URL = "https://eu.thingsboard.cloud/api/v1" # Jorge et Nicolas
THINGSBOARD_URL = "https://thingsboard.cloud/api/v1" # Cours
# ACCESS_TOKEN = "yE1hdypygpWk7SoP7trC"  # Jorge
# ACCESS_TOKEN = "TYO7UGAFQAKZrtPb773x"  # Nicolas
ACCESS_TOKEN = "jaIwPnJ4jzsjS4v6uXvz"  # Cours

# Endpoint para telemetría
url = f"{THINGSBOARD_URL}/{ACCESS_TOKEN}/telemetry"

# Leer CSV y enviar datos
with open("OpenMeteo_forecast.csv", "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        # Convertir fecha a timestamp (milisegundos)
        ts = int(datetime.fromisoformat(row["date"].replace("Z", "+00:00")).timestamp() * 1000)

        values = {}
        for key in ["temperature_om", "humidity_om", "pressure_om", "wind_speed_om", "wind_direction_om",
                    "precipitation_om", "soil_temperature_6cm_om", "soil_temperature_18cm_om", "soil_temperature_54cm_om"]:
            val = row.get(key, "")
            if val.strip():  # si no está vacío
                values[key] = float(val)

        payload = {"ts": ts, "values": values}

        # Enviar a ThingsBoard
        r = requests.post(url, json=payload)
        if r.status_code != 200:
            print("Error:", r.text)
        else:
            print("Dato enviado:", payload)

        # Opcional: evitar saturar el servidor
        time.sleep(0.1)
