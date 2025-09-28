from pymodbus.client import ModbusSerialClient
import time
import requests
import json
import csv
from datetime import datetime, timezone
from pathlib import Path
import sys
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent.parent

if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from src.utils.log import log_error, log_info, log_warning
from src.utils.data import save_hourly_data

# init cv file to store data
filename = f"{BASE_DIR}/db/sensors_data.csv"

# Création du fichier CSV et écriture de l'en-tête si le fichier n'existe pas
def init_csv(reinitialize=False):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            if reinitialize:
                raise FileNotFoundError
    except FileNotFoundError:
        with open(filename, "w", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "date", 
                "T_sonde1", "H_sonde1", "c_sonde1", "pH_sonde1",
                "T_sonde2", "H_sonde2", "c_sonde2", "pH_sonde2",
                "T_sonde3", "H_sonde3", "c_sonde3", "pH_sonde3",
                "T_sonde4", "H_sonde4", "c_sonde4", "pH_sonde4"
            ])

def fill_csv(T1, H1, C1, pH1, T2, H2, C2, pH2, T3, H3, C3, pH3, T4, H4, C4, pH4):
    init_csv()  # Ensure CSV is initialized
    with open(filename, "a", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
            T1, H1, C1, pH1,
            T2, H2, C2, pH2,
            T3, H3, C3, pH3,
            T4, H4, C4, pH4
        ])

# read data from csv comput mean and return a dict
# Consider number of data could vary
def read_csv_and_compute_mean():
    try:
        df = pd.read_csv(filename, parse_dates=["date"])
        if df.empty:
            log_warning(f"--SENSORS-- Le fichier {filename} CSV est vide.")
            return None
        df['date'] = pd.to_datetime(df['date'], utc=True).dt.floor('h')
        df = df.resample('h', on='date').mean().reset_index()
        # back to timestamp in ms
        df['date'] = df['date'].astype("int64") // 10**6
        mean_values = df.to_dict(orient="records")
        init_csv(reinitialize=True)
        return mean_values
    except FileNotFoundError:
        log_error(f"--SENSORS-- Le fichier {filename} n'existe pas.")
        return None


# Fonction pour lire les données d'une sonde donnée
def read_sensor(client, slave_id, label=""):
    try:
        response = client.read_holding_registers(address=0, count=8, device_id=slave_id)
        if response.isError():
            error_msg = f"Modbus error reading sensor {label} (slave_id={slave_id})"
            if hasattr(response, 'exception_code'):
                error_msg += f" - Exception code: {response.exception_code}"
            log_error(f"--SENSORS-- {error_msg}")
            return None
        else:
            # Validate that we have enough registers
            if len(response.registers) < 4:
                log_error(f"--SENSORS-- Insufficient data from sensor {label} (slave_id={slave_id}): expected 4 registers, got {len(response.registers)}")
                return None
                
            humidity = response.registers[0] / 10.0
            temperature = response.registers[1] / 10.0
            conductivity = response.registers[2] / 10.0
            ph = response.registers[3] / 10.0

            return humidity, temperature, conductivity, ph
    except Exception as e:
        log_error(f"--SENSORS-- Exception reading sensor {label} (slave_id={slave_id}): {str(e)}")
        return None
        
        
        
def SendData():

    THINGSBOARD_TOKEN = "jaIwPnJ4jzsjS4v6uXvz"
    url = f"http://thingsboard.cloud/api/v1/{THINGSBOARD_TOKEN}/telemetry"
    
    headers = {"Content-Type": "application/json"}

    data = read_csv_and_compute_mean()

    if data == None:
        log_warning("--SENSORS-- Aucune donnee a envoyer.")
        return
    for obs in data:

        # Prepare data for ThingsBoard
        ts = obs.pop("date", int(datetime.now(tz=timezone.utc).timestamp() * 1000))
        tb_data = {
            "ts": ts,
            "values": obs
        }

        save_hourly_data(obs, time=ts / 1000)  # save to main CSV as well

        try:

            response = requests.post(url, headers=headers, data=json.dumps(tb_data))

            if response.status_code == 200:
                log_info("--SENSORS-- Donnees envoyees avec succes.")
            else:
                log_warning(f"--SENSORS-- Status code {response.status_code} received from ThingsBoard.")
                log_error(f"--SENSORS-- {response.status_code} - {response.text}")
                return

        except Exception as e:
            log_error(f"--SENSORS-- {e}")
            return
        
        time.sleep(1)  # Pause pour éviter de saturer le serveur


def read_sensors():

    port = '/dev/ttyUSB0'
    baudrate = 9600
    timeout = 1

    try:
        client = ModbusSerialClient(port=port, baudrate=baudrate, timeout=timeout)
        if not client.connect():
            log_warning(f"--SENSORS-- Impossible de se connecter au port {port}. Verifie le branchement.")
            return
            
    except Exception as e:
        log_error(f"--SENSORS-- {e}")
        return
       
    attempt = 0
    while attempt < 3:
        try:

            H1,T1,C1,pH1=read_sensor(client, 0x01, "1")
            H2,T2,C2,pH2=read_sensor(client, 0x02, "2")
            H3,T3,C3,pH3=read_sensor(client, 0x03, "3")
            H4,T4,C4,pH4=read_sensor(client, 0x04, "4")

            log_info(f"--SENSORS-- Sensors read successfully")

            fill_csv(T1, H1, C1, pH1, T2, H2, C2, pH2, T3, H3, C3, pH3, T4, H4, C4, pH4)

            break

        except Exception as e:
            attempt += 1
            log_error(f"--SENSORS-- {e}")
            log_warning(f"--SENSORS-- Erreur lors de la lecture des sondes. Nouvelle tentative dans 10 secondes... (tentative {attempt}/3)")
            time.sleep(10)
