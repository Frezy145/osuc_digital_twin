# -*- coding: utf-8 -*-
"""
Created on Tue Sep 16 16:08:47 2025

@author: hp
"""

from meteofrance_api import MeteoFranceClient
import requests
from datetime import datetime
import pandas as pd

# -------------------------------
# Coordonnées GPS
latitude = 47.83403
longitude = 1.94308

# -------------------------------
# 1) Prévisions Météo-France
client = MeteoFranceClient()
forecast_mf = client.get_forecast(latitude, longitude).forecast

data_mf = []
for prevision in forecast_mf:
    dt = datetime.fromtimestamp(prevision['dt'], tz=None)  # datetime standard
    temp = prevision['T']['value']
    hum = prevision['humidity']
    pres = prevision['sea_level']
    rain = next(iter(prevision['rain'].values())) if "rain" in prevision and prevision["rain"] else 0
    wind = prevision['wind']['speed']  # vent moyen en km/h
    data_mf.append([dt, temp, hum, pres, rain, wind])

df_mf = pd.DataFrame(data_mf, columns=["time", "temp", "humidity", "pressure", "rain", "wind"])
df_mf.set_index("time", inplace=True)

# -------------------------------
# 2) Prévisions Open-Meteo
url = (
    "https://api.open-meteo.com/v1/forecast?"
    f"latitude={latitude}&longitude={longitude}"
    "&hourly=temperature_2m,relative_humidity_2m,pressure_msl,precipitation,wind_speed_10m"
    "&forecast_days=7&timezone=auto"
)
response = requests.get(url).json()

data_om = []
for t, temp, hum, pres, rain, wind in zip(
    response["hourly"]["time"],
    response["hourly"]["temperature_2m"],
    response["hourly"]["relative_humidity_2m"],
    response["hourly"]["pressure_msl"],
    response["hourly"]["precipitation"],
    response["hourly"]["wind_speed_10m"]
):
    dt = datetime.fromisoformat(t)
    data_om.append([dt, temp, hum, pres, rain, wind * 3.6])  # m/s -> km/h

df_om = pd.DataFrame(data_om, columns=["time", "temp", "humidity", "pressure", "rain", "wind"])
df_om.set_index("time", inplace=True)

# -------------------------------
# 3) Aligner les deux sources sur une grille horaire commune
df_mf = df_mf.resample("h").interpolate()
df_om = df_om.resample("h").interpolate()

common_index = df_mf.index.intersection(df_om.index)
df_mf = df_mf.loc[common_index]
df_om = df_om.loc[common_index]

# -------------------------------
# 4) Statistiques
diffs = df_mf - df_om
mean_diffs = diffs.mean()
corrs = df_mf.corrwith(df_om)
print("📊 Moyenne des écarts (Météo-France - Open-Meteo) :")
print(mean_diffs)
print("\n🔗 Corrélation entre les deux sources :")
print(corrs)

# # -------------------------------
# # 5) Tracer les comparaisons
# fig, axs = plt.subplots(5, 1, figsize=(14, 24))

variables = ["temp", "humidity", "pressure", "rain", "wind"]
titles = ["Température (°C)", "Humidité (%)", "Pression (hPa)", "Précipitations (mm)", "Vent (km/h)"]
colors_mf = ["red", "blue", "green", "purple", "orange"]
colors_om = ["orange", "cyan", "lime", "magenta", "brown"]

# for i, var in enumerate(variables):
#     axs[i].plot(df_mf.index, df_mf[var], label="Météo-France", color=colors_mf[i])
#     axs[i].plot(df_om.index, df_om[var], label="Open-Meteo", color=colors_om[i], linestyle="--")
#     axs[i].set_title(f"{titles[i]} — Corrélation : {corrs[var]:.2f}")
#     axs[i].legend()
#     axs[i].grid(True)

