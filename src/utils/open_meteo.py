# -*- coding: utf-8 -*-
"""
Created on Thu Sep 18 21:07:29 2025

@author: sophi
"""

import pandas as pd
import openmeteo_requests
import requests_cache
from retry_requests import retry
import csv
from datetime import datetime
import requests
import os
import sys
from pathlib import Path
import time


BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

if not os.path.exists(f"{BASE_DIR}/db"):
    os.makedirs(f"{BASE_DIR}/db")

from src.utils.log import log_error, log_warning
from src.utils.data import save_dataframe

output_csv = f"{BASE_DIR}/db/OpenMeteo_forecast.csv"

def get_open_meteo():
    """
    Récupère les données météo d'Open-Meteo et les sauvegarde dans un CSV.

    Args:
        lat (float): latitude
        lon (float): longitude
        days_forecast (int): nombre de jours de prévision
        output_csv (str): nom du fichier CSV de sortie
    """
    
    # Session avec cache et retries
    cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)

    lat=47.833499
    lon=1.943945
    days_forecast=1

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": [
            "temperature_2m", "relative_humidity_2m", "pressure_msl", "wind_speed_10m",
            "wind_direction_10m", "precipitation", "soil_temperature_6cm",
            "soil_temperature_18cm", "soil_temperature_54cm"
        ],
        "forecast_days": days_forecast,
    }

    responses = openmeteo.weather_api(url, params=params)
    response = responses[0]

    # Données horaires
    hourly = response.Hourly()

    dates = pd.date_range(
        start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
        end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
        freq=pd.Timedelta(seconds=hourly.Interval()),
        inclusive="left"
    )


    # reformat dates to ISO 8601 without "+00:00"
    dates = dates.strftime("%Y-%m-%d %H:%M:%S")

    df_om = pd.DataFrame({
        "date": dates,
        "temperature_om": hourly.Variables(0).ValuesAsNumpy(),
        "humidity_om": hourly.Variables(1).ValuesAsNumpy(),
        "pressure_om": hourly.Variables(2).ValuesAsNumpy(),
        "wind_speed_om": hourly.Variables(3).ValuesAsNumpy(),
        "wind_direction_om": hourly.Variables(4).ValuesAsNumpy(),
        "precipitation_om": hourly.Variables(5).ValuesAsNumpy(),
        "soil_temperature_6cm_om": hourly.Variables(6).ValuesAsNumpy(),
        "soil_temperature_18cm_om": hourly.Variables(7).ValuesAsNumpy(),
        "soil_temperature_54cm_om": hourly.Variables(8).ValuesAsNumpy()
    })

    # Sauvegarde dans un CSV
    df_om.to_csv(output_csv, index=False)

    save_dataframe(df_om)


def envoi_donnees_openmeteo_thingsboard():
    """
    Envoie les données du CSV Open-Meteo vers ThingsBoard via HTTP.

    Args:
        csv_file (str): chemin du fichier CSV exporté par get_meteofrance()
        access_token (str): token d'accès ThingsBoard (Device -> Access Token)
        tb_url (str): URL du serveur ThingsBoard (par défaut thingsboard.cloud)
    """

    tb_url="https://thingsboard.cloud/api/v1"
    access_token="jaIwPnJ4jzsjS4v6uXvz"
    
    url = f"{tb_url}/{access_token}/telemetry"
    csv_file = output_csv

    with open(csv_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                # Convertir la date ISO en timestamp (ms)
                ts = int(datetime.fromisoformat(row["date"].replace("Z", "+00:00")).timestamp() * 1000)

                # Préparer les valeurs
                values = {}
                for key in [
                    "temperature_om", "humidity_om", "pressure_om", "wind_speed_om", 
                    "wind_direction_om", "precipitation_om",
                    "soil_temperature_6cm_om", "soil_temperature_18cm_om", "soil_temperature_54cm_om"
                ]:
                    val = row.get(key, "")
                    if val and val.strip():  # non vide
                        values[key] = float(val)

                payload = {"ts": ts, "values": values}

                # Envoi HTTP
                r = requests.post(url, json=payload)
                if r.status_code != 200:
                    log_warning("--OPEN_METEO-- Error in sending data to ThingsBoard")
                    log_error(f"--OPEN_METEO-- {r.status_code} - {r.text}")

                # Pause pour éviter de saturer ThingsBoard
                time.sleep(1)

            except Exception as e:
                log_warning("--OPEN_METEO-- Error in sending data to ThingsBoard. Check erros.log")
                log_error(f"--OPEN_METEO-- {e}")
                
