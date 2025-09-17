# -*- coding: utf-8 -*-
"""
Created on Wed Sep 17 09:42:50 2025

@author: gryma
"""

import requests
import json
import csv
import time
from datetime import datetime

API_KEY = "aea516e0e7de4ce6a516e0e7de3ce666"
STATION_ID = "IORLAN50"

url = (
    f"https://api.weather.com/v2/pws/observations/current"
    f"?stationId={STATION_ID}&format=json&units=m&apiKey={API_KEY}"
)

filename = "données_station_IORLAN50.csv"

# Vérifie si le fichier existe déjà (sinon, crée avec en-têtes)
def init_csv(headers):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            pass
    except FileNotFoundError:
        with open(filename, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()

while True:
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

            # Affichage terminal
            print(json.dumps(obs, indent=4, ensure_ascii=False))

            # Init CSV avec les bons headers
            init_csv(obs.keys())

            # Ajoute une ligne dans le CSV
            with open(filename, mode="a", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=obs.keys())
                writer.writerow(obs)

            print(f"✅ Données ajoutées dans {filename}")
        else:
            print("⚠️ Aucune observation disponible.")
    else:
        print(f"❌ Erreur API : {resp.status_code} - {resp.text}")

    # Pause 1h en seconde , mettre 10 pour tester
    time.sleep(3600)
