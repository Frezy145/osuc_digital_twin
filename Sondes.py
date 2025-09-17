from pymodbus.client import ModbusSerialClient
import time
import requests
import json
import csv
from datetime import datetime


url = "http://thingsboard.cloud/api/v1/mGNBV4UUcYjdzXqC9lMZ/telemetry"
headers = {"Content-Type": "application/json"}

# Configuration du client Modbus pour Raspberry Pi
port = '/dev/ttyUSB0'   # adapte selon ton branchement (ttyUSB0, ttyUSB1 ou ttyAMA0)
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
        conductivity = response.registers[2]
        ph = response.registers[3] / 10.0

        return humidity,temperature,conductivity,ph
        
        
        
def SendData(T1, H1, C1, pH1, T2, H2, C2, pH2, T3, H3, C3, pH3):
    data = {
        "T_sonde1": T1,
        "H_sonde1": H1,
        "c_sonde1": C1,
        "pH_sonde1": pH1,
        "T_sonde2": T2,
        "H_sonde2": H2,
        "c_sonde2": C2,
        "pH_sonde2": pH2,
        "T_sonde3": T3,
        "H_sonde3": H3,
        "c_sonde3": C3,
        "pH_sonde3": pH3
    }
    requests.post(url, headers=headers, data=json.dumps(data))
        
client = ModbusSerialClient(port=port, baudrate=baudrate, timeout=timeout)
while True: 
    time.sleep(5)  # une mesure toutes les 10 s
   
    H1,T1,C1,pH1=lire_sonde(client, 0x01, "1")
    H2,T2,C2,pH2=lire_sonde(client, 0x02, "2")
    H3,T3,C3,pH3=lire_sonde(client, 0x03, "3")
    
    SendData(T1, H1, C1, pH1, T2, H2, C2, pH2, T3, H3, C3, pH3)
    
    # print("sonde 1 :")
    # print(H1)
    # print(T1)
    # print(C1)
    # print(pH1)
    # print("********************")
    # print("sonde 2 :")
    # print(H2)
    # print(T2)
    # print(C2)
    # print(pH2)
    # print("********************")
    # print("sonde 3 :")
    # print(H3)
    # print(T3)
    # print(C3)
    # print(pH3)
    # print("********************")
    
    
    
    
    
client.close()
