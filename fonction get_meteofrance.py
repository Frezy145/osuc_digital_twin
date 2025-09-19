# -*- coding: utf-8 -*-
"""
Created on Thu Sep 18 21:07:29 2025

@author: sophi
"""

import pandas as pd
import openmeteo_requests
import requests_cache
from retry_requests import retry

def get_meteofrance(lat, lon, days_forecast=10, output_csv="OpenMeteo_forecast.csv"):
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
    print(f"✅ Données Open-Meteo sauvegardées dans {output_csv}")

    return df_om


#pour appeler la fonction:
#==============================================================================
# if __name__ == "__main__":
#     df = get_meteofrance(lat=47.833499, lon=1.943945, output_csv="meteo_france.csv")
#     print(df.head())  # aperçu
# =============================================================================
