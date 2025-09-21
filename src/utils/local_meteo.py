# -*- coding: utf-8 -*-
"""
Created on Wed Sep 17 11:24:25 2025

@author: sophi
"""

import csv
import sys
import os
import requests
from datetime import datetime
import pandas as pd  
import json
from pathlib import Path

from utils.log import log_error, log_info, log_warning

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

if not os.path.exists(f"{BASE_DIR}/db"):
    os.makedirs(f"{BASE_DIR}/db")

API_KEY = "aea516e0e7de4ce6a516e0e7de3ce666"
STATION_ID = "IORLAN50"

THINGSBOARD_TOKEN = "jaIwPnJ4jzsjS4v6uXvz"
THINGSBOARD_URL = f"http://thingsboard.cloud/api/v1/{THINGSBOARD_TOKEN}/telemetry"

url = (
    f"https://api.weather.com/v2/pws/observations/current"
    f"?stationId={STATION_ID}&format=json&units=m&apiKey={API_KEY}")

filename = f"{BASE_DIR}/db/données_station_IORLAN50.csv"

# Colonnes à conserver
colonnes_a_garder = [
    "solarRadiation",
    "epoch",
    "winddir",
    "humidity",
    "metric_temp",
    "metric_windSpeed",
    "metric_windGust",
    "metric_pressure",
    "metric_precipRate",
    "metric_precipTotal"
    ]

# Vérifie si le fichier existe déjà (sinon, crée avec en-têtes)
def init_csv():
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

            # Init CSV avec les bons headers
            init_csv()

            # Ajoute une ligne filtrée dans le CSV
            with open(filename, mode="a", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=colonnes_a_garder)
                writer.writerow(obs_filtre)
            log_info(f"Données météo locale ajoutées dans {filename}")
        else:
            log_warning("Aucune observation disponible.")
    else:
        log_error(f"Erreur API : {resp.status_code} - {resp.text}")

def read_csv_and_compute_mean():
    try:
        df = pd.read_csv(filename)
        if df.empty:
            log_warning("Le fichier CSV est vide.")
            return None
        mean_values = df.mean(numeric_only=True).to_dict()
        return mean_values
    except Exception as e:
        log_error(f"Erreur lecture CSV ou calcul moyenne : {e}")
        return None

def send_meteo_locale():
    """
    Envoie les données du CSV météo locale vers ThingsBoard via HTTP.

    Args:
        csv_file (str): chemin du fichier CSV exporté par get_meteo_locale()
        access_token (str): token d'accès ThingsBoard (Device -> Access Token)
        tb_url (str): URL du serveur ThingsBoard (par défaut thingsboard.cloud)
    """

    obs_filtre = read_csv_and_compute_mean()
    if obs_filtre is None:
        log_warning("Aucune donnée à envoyer à ThingsBoard.")
        return

    try:
        tb_resp = requests.post(
            THINGSBOARD_URL,
            headers={"Content-Type": "application/json"},
            data=json.dumps(obs_filtre)
        )
        if tb_resp.status_code == 200:
            log_info("Données envoyées à ThingsBoard avec succès")
        else:
            log_warning(f"Erreur ThingsBoard {tb_resp.status_code}: {tb_resp.text}")
    except Exception as e:
        log_error(f"Erreur envoi ThingsBoard: {e}")


    