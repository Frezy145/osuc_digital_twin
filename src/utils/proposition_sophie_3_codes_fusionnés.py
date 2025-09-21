# -*- coding: utf-8 -*-
"""
Created on Fri Sep 19 14:51:34 2025

@author: sophi
"""
import time
import requests
import csv
import json
from pymodbus.client import ModbusSerialClient
from datetime import datetime
import pandas as pd  # pour filtrer les colonnes
import openmeteo_requests
import requests_cache
from retry_requests import retry

#0. Définition des fonctions pour récupérer les données
#définir une focntion pour sauver les données dans un csv:
def save_to_csv(filename, data):
    """Sauvegarde les données des sondes dans un fichier CSV avec horodatage."""
    file_exists = False
    try:
        with open(filename, "r", encoding="utf-8"):
            file_exists = True
    except FileNotFoundError:
        file_exists = False

    with open(filename, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["timestamp"] + list(data.keys()))
        if not file_exists:
            writer.writeheader()
        row = {"timestamp": datetime.now().isoformat(), **data}
        writer.writerow(row)


# =============================================================================
# # Données issues des sondes:
# =============================================================================
 # Configuration du client Modbus pour Raspberry Pi
port = 'token'   # adapte selon ton branchement (ttyUSB0, ttyUSB1 ou ttyAMA0)
baudrate = 9600
timeout = 1

# Fonction pour lire les données d'une sonde donnée
def lire_sonde(client, slave_id, label=""):
    response = client.read_holding_registers(address=0, count=8, slave=slave_id)
    if response.isError():
        print(f"Erreur de lecture Modbus (sonde {label}):", response)
        return None
    else:
        humidity = response.registers[0] / 10.0
        temperature = response.registers[1] / 10.0
        conductivity = response.registers[2] / 10.0
        ph = response.registers[3] / 10.0

        return humidity,temperature,conductivity,ph
      
       
# =============================================================================
# def SendData(T1, H1, C1, pH1, T2, H2, C2, pH2, T3, H3, C3, pH3, T4, H4, C4, pH4):
#     data = {
#         "T_sonde1": T1,
#         "H_sonde1": H1,
#         "c_sonde1": C1,
#         "pH_sonde1": pH1,
#         "T_sonde2": T2,
#         "H_sonde2": H2,
#         "c_sonde2": C2,
#         "pH_sonde2": pH2,
#         "T_sonde3": T3,
#         "H_sonde3": H3,
#         "c_sonde3": C3,
#         "pH_sonde3": pH3,
#         "T_sonde4": T4,
#         "H_sonde4": H4,
#         "c_sonde4": C4,
#         "pH_sonde4": pH4
#     }
#     requests.post(url, headers=headers, data=json.dumps(data))
# =============================================================================
         
client = ModbusSerialClient(port=port, baudrate=baudrate, timeout=timeout)   



# =============================================================================
# # Données issues de la station locale
# =============================================================================
 
filename = "données_station_IORLAN50.csv"

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
  
        
# =============================================================================
# #données de prévisions issues de open météo
# =============================================================================



def get_open_meteo(lat, lon, days_forecast=10, output_csv="OpenMeteo_forecast.csv"):
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


    
 
# 1 Fonction pour Lecture de la dernière ligne des CSV:
    
# Lecture adaptée pour le CSV des sondes

def lire_sondes(fichier):
    """
    Lit la dernière ligne du fichier sondes.csv et retourne les valeurs dans un dict.
    """
    try:
        with open(fichier, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            lignes = list(reader)
            if not lignes:
                return None
            derniere = lignes[-1]

            # Conversion en float pour toutes les mesures (sauf timestamp)
            mesures = {"timestamp": derniere["timestamp"]}
            for key, val in derniere.items():
                if key != "timestamp" and val.strip():
                    try:
                        mesures[key] = float(val)
                    except ValueError:
                        mesures[key] = val  # au cas où ce n’est pas un nombre
            return mesures

    except FileNotFoundError:
        print(f"⚠️ Fichier {fichier} introuvable.")
        return None


    

# Lecture adaptée pour le CSV de la station locale


def lire_meteo_locale(fichier):
    """
    Lit la dernière ligne du fichier données_stationIOLAN50.csv
    et retourne les valeurs météo dans un dict.
    """
    try:
        with open(fichier, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            lignes = list(reader)
            if not lignes:
                return None
            derniere = lignes[-1]

            mesures = {}
            # Conversion epoch en timestamp ISO
            if "epoch" in derniere:
                try:
                    ts = int(derniere["epoch"])
                    mesures["timestamp"] = datetime.fromtimestamp(ts).isoformat()
                except ValueError:
                    mesures["timestamp"] = derniere["epoch"]

            # Conversion numérique pour les autres colonnes
            for key, val in derniere.items():
                if key != "epoch" and val.strip():
                    try:
                        mesures[key] = float(val)
                    except ValueError:
                        mesures[key] = val  # au cas où c’est une string
            return mesures

    except FileNotFoundError:
        print(f"⚠️ Fichier {fichier} introuvable.")
        return None

# Lecture adaptée pour le CSV d'Open_Météo

def lire_OpenMeteo(fichier):
    """
    Lit la dernière ligne du fichier OpenMeteo_forecast.csv
    et retourne les valeurs météo dans un dict.
    """
    try:
        with open(fichier, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            lignes = list(reader)
            if not lignes:
                return None
            derniere = lignes[-1]

            mesures = {}
            # La colonne "date" sert de timestamp
            if "date" in derniere:
                mesures["timestamp"] = derniere["date"]

            # Conversion numérique pour les autres colonnes
            for key, val in derniere.items():
                if key != "date" and val.strip():
                    try:
                        mesures[key] = float(val)
                    except ValueError:
                        mesures[key] = val
            return mesures

    except FileNotFoundError:
        print(f"⚠️ Fichier {fichier} introuvable.")
        return None

# 2 Appel des fonctions existantes pour regrouper les données

API_KEY = "TOKEN2"
STATION_ID = "IORLAN50"

url = (
    f"https://api.weather.com/v2/pws/observations/current"
    f"?stationId={STATION_ID}&format=json&units=m&apiKey={API_KEY}")
def collecter_donnees():
    # Lire les 4 sondes
    s1 = lire_sonde(client, slave_id=1, label="1")
    s2 = lire_sonde(client, slave_id=2, label="2")
    s3 = lire_sonde(client, slave_id=3, label="3")
    s4 = lire_sonde(client, slave_id=4, label="4")

    # Vérifier que toutes les sondes ont répondu
    if None in (s1, s2, s3, s4):
        print("⚠️ Une ou plusieurs sondes n'ont pas répondu.")
    else:
        # Construire un dict pour save_to_csv
        data_sondes = {
            "H_sonde1": s1[0], "T_sonde1": s1[1], "C_sonde1": s1[2], "pH_sonde1": s1[3],
            "H_sonde2": s2[0], "T_sonde2": s2[1], "C_sonde2": s2[2], "pH_sonde2": s2[3],
            "H_sonde3": s3[0], "T_sonde3": s3[1], "C_sonde3": s3[2], "pH_sonde3": s3[3],
            "H_sonde4": s4[0], "T_sonde4": s4[1], "C_sonde4": s4[2], "pH_sonde4": s4[3],
        }

        # ✅ Sauvegarde dans sondes.csv
        save_to_csv("sondes.csv", data_sondes)

    # Collecte station locale
    get_meteo_locale(url)

    # Collecte prévisions
    get_open_meteo(
        lat=47.833499,
        lon=1.943945,
        days_forecast=10,
        output_csv="OpenMeteo_forecast.csv"
    )

    # Lecture des trois fichiers CSV
    sonde = lire_sondes("sondes.csv")
    meteo_locale = lire_meteo_locale("données_station_IORLAN50.csv")
    open_meteo = lire_OpenMeteo("OpenMeteo_forecast.csv")

    # Fusion des mesures
    mesures = {**sonde, **meteo_locale, **open_meteo}
    return mesures


# 3. Envoi à ThingsBoard en HTTP
THINGSBOARD_TOKEN = "TOKEN3"


def envoyer_thingsboard(mesures):
    url = f"http://thingsboard.cloud/api/v1/{THINGSBOARD_TOKEN}/telemetry"
    headers = {"Content-Type": "application/json"}
    try:
        r = requests.post(url, headers=headers, data=json.dumps(mesures))
        if r.status_code == 200:
            print("✅ Données envoyées :", mesures)
        else:
            print("⚠️ Erreur envoi :", r.status_code, r.text)
    except Exception as e:
        print("❌ Exception lors de l’envoi :", e)

# 4. Boucle infinie (toutes les heures)
def main():
    while True:
        try:
            mesures = collecter_donnees()
            envoyer_thingsboard(mesures)
        except Exception as e:
            print("⚠️ Erreur lors de la collecte :", e)
        time.sleep(3600)  # pause d’1h

if __name__ == "__main__":
    main()

