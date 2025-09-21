# -*- coding: utf-8 -*-
"""
Created on Thu Sep 18 11:21:42 2025

@author: sophi
"""

import csv
import requests
import json
from datetime import datetime

API_KEY = "aea516e0e7de4ce6a516e0e7de3ce666"  # Clé Weather.com

STATION_ID = "IORLAN50"

# ⚠️ Mets ton token ThingsBoard ici :
THINGSBOARD_TOKEN = "jaIwPnJ4jzsjS4v6uXvz"
THINGSBOARD_URL = f"http://thingsboard.cloud/api/v1/{THINGSBOARD_TOKEN}/telemetry"

url = (
    f"https://api.weather.com/v2/pws/observations/current"
    f"?stationId={STATION_ID}&format=json&units=m&apiKey={API_KEY}"
)

filename = "données_station_IORLAN50_v2.csv"

# Colonnes à conserver
colonnes_a_garder = [
    "solarRadiation",
    "winddir",
    "humidity",
    "metric_temp",
    "metric_windSpeed",
    "metric_windGust",
    "metric_pressure",
    "metric_precipRate",
    "metric_precipTotal",
   
]

# Vérifie si le fichier existe déjà (sinon, crée avec en-têtes)
def init_csv(headers):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            pass
    except FileNotFoundError:
        with open(filename, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=colonnes_a_garder)
            writer.writeheader()

def get_meteo_locale():
    resp = requests.get(url)

    if resp.status_code == 200:
        data = resp.json()
        if "observations" in data and len(data["observations"]) > 0:
            obs = data["observations"][0]

            # Ajoute un champ de date/heure locale
            obs["collected_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Extraire la partie "metric" et la fusionner avec obs
            if "metric" in obs:
                metrics = obs.pop("metric")  # enlève "metric"
                for k, v in metrics.items():
                    obs[f"metric_{k}"] = v  # ajoute comme colonne séparée

            # Filtrer uniquement les colonnes voulues
            obs_filtre = {c: obs.get(c, None) for c in colonnes_a_garder}

            # --- Envoi à ThingsBoard ---
            try:
                tb_resp = requests.post(
                    THINGSBOARD_URL,
                    headers={"Content-Type": "application/json"},
                    data=json.dumps(obs_filtre)
                )
                if tb_resp.status_code == 200:
                    print("📡 Données envoyées à ThingsBoard avec succès")
                else:
                    print(f"⚠️ Erreur ThingsBoard {tb_resp.status_code}: {tb_resp.text}")
            except Exception as e:
                print(f"❌ Erreur envoi ThingsBoard: {e}")

            # Init CSV avec les bons headers
            init_csv(colonnes_a_garder)

            # Ajoute une ligne filtrée dans le CSV
            with open(filename, mode="a", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=colonnes_a_garder)
                writer.writerow(obs_filtre)
        else:
            print("⚠️ Aucune observation disponible.")
    else:
        print(f"❌ Erreur API Weather : {resp.status_code} - {resp.text}")