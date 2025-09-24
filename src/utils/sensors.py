from pymodbus.client import ModbusSerialClient
import time
import requests
import json
import csv
from datetime import datetime
from pathlib import Path
import sys
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent.parent

if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from utils.log import log_error, log_info, log_warning

# init cv file to store data
filename = f"{BASE_DIR}/db/données_sondes.csv"

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
                "Timestamp", 
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
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            T1, H1, C1, pH1,
            T2, H2, C2, pH2,
            T3, H3, C3, pH3,
            T4, H4, C4, pH4
        ])

# read data from csv comput mean and return a dict
# Consider number of data could vary
def read_csv_and_compute_mean():
    try:
        df = pd.read_csv(filename, parse_dates=["Timestamp"])
        if df.empty:
            log_warning("Le fichier CSV est vide.")
            return None
        mean_values = df.mean(numeric_only=True).to_dict()
        init_csv(reinitialize=True)
        return mean_values
    except FileNotFoundError:
        log_error(f"Le fichier {filename} n'existe pas.")
        return None


# Fonction pour lire les données d'une sonde donnée
def read_sensor(client, slave_id, label=""):
    response = client.read_holding_registers(address=0, count=8, device_id=slave_id)
    if response.isError():
        log_error(f"Erreur de lecture Modbus (sonde {label}): {response}")
        return None
    else:
        humidity = response.registers[0] / 10.0
        temperature = response.registers[1] / 10.0
        conductivity = response.registers[2] /10.0
        ph = response.registers[3] / 10.0

        return humidity,temperature,conductivity,ph
        
        
        
def SendData():

    url = "https://thingsboard.cloud/dashboard/8feb3a50-9306-11f0-a1aa-d709ca5e32a7?publicId=b0676a50-9474-11f0-82a5-3b714d9b93ee/jaIwPnJ4jzsjS4v6uXvz/telemetry"
    headers = {"Content-Type": "application/json"}

    data = read_csv_and_compute_mean()

    if data == None:
        log_warning("Aucune donnée à envoyer.")
        return

    try:

        response = requests.post(url, headers=headers, data=json.dumps(data))

        if response.status_code == 200:
<<<<<<< HEAD
            log_info("Donnees envoyees avec succes.")
        else:
            log_error(f"Erreur lors de l'envoi des donnees des sondes: {response.status_code} - {response.text}")
            return

    except Exception as e:
        log_error(f"Exception lors de l'envoi des donnees des sondes: {e}")
=======
            log_info("Données envoyées avec succès.")
        else:
            log_error(f"Erreur lors de l'envoi des données: {response.status_code} - {response.text}")
            return

    except Exception as e:
        log_error(f"Exception lors de l'envoi des données: {e}")
>>>>>>> 9a6aa26072f5fcfe6824ef7da869e07148ea02ce
        return
        


def read_sensors():

    port = '/dev/ttyUSB0'
    baudrate = 9600
    timeout = 1

    try:
        client = ModbusSerialClient(port=port, baudrate=baudrate, timeout=timeout)
        if not client.connect():
            log_warning(f"Impossible de se connecter au port {port}. Verifie le branchement.")
            return
            
    except Exception as e:
        log_error(f"Exception lors de la connexion Modbus: {e}")
        return
       
    attempt = 0
    while attempt < 3:
        try:

            H1,T1,C1,pH1=read_sensor(client, 0x01, "1")
            H2,T2,C2,pH2=read_sensor(client, 0x02, "2")
            H3,T3,C3,pH3=read_sensor(client, 0x03, "3")
            H4,T4,C4,pH4=read_sensor(client, 0x04, "4")

            fill_csv(T1, H1, C1, pH1, T2, H2, C2, pH2, T3, H3, C3, pH3, T4, H4, C4, pH4)

            break

        except Exception as e:
            attempt += 1
            log_error(f"Exception lors de la lecture des sondes: {e}")
            log_warning(f"Erreur lors de la lecture des sondes. Nouvelle tentative dans 10 secondes... (tentative {attempt}/3)")
            time.sleep(10)
