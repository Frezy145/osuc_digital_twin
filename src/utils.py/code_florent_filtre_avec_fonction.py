# -*- coding: utf-8 -*-
"""
Created on Wed Sep 17 11:24:25 2025

@author: sophi
"""

import csv
import requests
import json
import time
from datetime import datetime
import pandas as pd  # pour filtrer les colonnes

   

API_KEY = "aea516e0e7de4ce6a516e0e7de3ce666"
STATION_ID = "IORLAN50"

url = (
    f"https://api.weather.com/v2/pws/observations/current"
    f"?stationId={STATION_ID}&format=json&units=m&apiKey={API_KEY}")

filename = "données_station_IORLAN50.csv"



# Colonnes à conserver
colonnes_a_garder = [
    "stationID",
    "obsTimeLocal",
    "solarRadiation",
    "epoch",
    "winddir",
    "humidity",
    "metric_temp",
    "metric_windSpeed",
    "metric_windGust",
    "metric_pressure",
    "metric_precipRate",
    "metric_precipTotal",
    "collected_at"  # j’ai ajouté ta colonne de timestamp locale
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

def get_meteo_locale(url:str):
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

            # Affichage terminal
            print(json.dumps(obs_filtre, indent=4, ensure_ascii=False))

            # Init CSV avec les bons headers
            init_csv(colonnes_a_garder)

            # Ajoute une ligne filtrée dans le CSV
            with open(filename, mode="a", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=colonnes_a_garder)
                writer.writerow(obs_filtre)

            print(f"✅ Données ajoutées dans {filename}")
        else:
            print("⚠️ Aucune observation disponible.")
    else:
        print(f"❌ Erreur API : {resp.status_code} - {resp.text}")


    