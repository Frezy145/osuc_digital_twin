# https://open-meteo.com/en/docs

# import requests
# import json
import pandas as pd
import openmeteo_requests
import requests_cache
from retry_requests import retry
import matplotlib.pyplot as plt

# url = "https://geocoding-api.open-meteo.com/v1/search"
# params = {"name": "Saint-Cyr-en-Val", "count": 1}
# response = requests.get(url, params=params)

# if response.status_code == 200:
#     data = response.json()
#     latitude = data["results"][0]["latitude"]
#     longitude = data["results"][0]["longitude"]
#     print(f"Latitude: {latitude}, Longitude: {longitude}")
# else:
#     print(f"Erreur {response.status_code}: {response.text}")
#     exit()

# ----------------
# Requête à l'API Open-Meteo avec gestion du cache et des retries
# ----------------

# número de días de previsión
DAYS_FORECAST = 10
LAT, LON = 47.833499, 1.943945

cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

url = "https://api.open-meteo.com/v1/forecast"
params = {
    "latitude": LAT,
    "longitude": LON,
    "hourly": ["temperature_2m", "relative_humidity_2m", "pressure_msl",  "wind_speed_10m",
               "wind_direction_10m", "precipitation", "soil_temperature_0cm", "soil_temperature_54cm"],
    "forecast_days": DAYS_FORECAST,
}

responses = openmeteo.weather_api(url, params=params)
response = responses[0]

# Traitement des données horaires
hourly = response.Hourly()
dates = pd.date_range(
    start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
    end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
    freq=pd.Timedelta(seconds=hourly.Interval()),
    inclusive="left"
)

# Extraction de toutes les variables
df_om = pd.DataFrame({
    "date": dates,
    "temperature": hourly.Variables(0).ValuesAsNumpy(),
    "humidity": hourly.Variables(1).ValuesAsNumpy(),
    "pressure": hourly.Variables(2).ValuesAsNumpy(),
    "wind_speed": hourly.Variables(3).ValuesAsNumpy(),
    "wind_direction": hourly.Variables(4).ValuesAsNumpy(),
    "precipitation": hourly.Variables(5).ValuesAsNumpy(),
    "soil_temperature_0cm": hourly.Variables(6).ValuesAsNumpy(),
    "soil_temperature_54cm": hourly.Variables(7).ValuesAsNumpy()
})

# ----------------
# Tracé de chaque paramètre
# ----------------

variables = {
    "temperature": {"label": "Température (°C)", "color": "red", "unit": "°C"},
    "humidity": {"label": "Humidité relative (%)", "color": "blue", "unit": "%"},
    "pressure": {"label": "Pression atmosphérique (hPa)", "color": "green", "unit": "hPa"},
    "wind_speed": {"label": "Vitesse du vent (km/h)", "color": "cyan", "unit": "km/h"},
    "wind_direction": {"label": "Direction du vent (°)", "color": "magenta", "unit": "°"},
    "precipitation": {"label": "Précipitations (mm)", "color": "purple", "unit": "mm"},
    "soil_temperature_0cm": {"label": "Température du sol à 0 cm (°C)", "color": "orange", "unit": "°C"},
    "soil_temperature_54cm": {"label": "Température du sol à 54 cm (°C)", "color": "brown", "unit": "°C"},
}

for var, info in variables.items():
    plt.figure(figsize=(8, 4))
    # plt.scatter(hourly_dataframe["date"], hourly_dataframe[var], label=info["label"], color=info["color"])
    plt.plot(df_om["date"], df_om[var], label=info["label"], color=info["color"])
    plt.xlabel("Date et heure")
    plt.ylabel(info["label"])
    plt.title(f"{info['label']} à Saint-Cyr-en-Val (Lat: {LAT}, Lon: {LON})")
    plt.grid(True)
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

# ----------------
# Export vers CSV
# ----------------

df_om.to_csv("OpenMeteo_forecast.csv", index=False)
print("✅ CSV file exported successfully:")
print(" - OpenMeteo_forecast.csv")
