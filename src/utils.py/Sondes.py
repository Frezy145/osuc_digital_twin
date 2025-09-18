from pymodbus.client import ModbusSerialClient
import time
import requests
import json
import csv
from datetime import datetime


url = "https://eu.thingsboard.cloud/dashboard/8feb3a50-9306-11f0-a1aa-d709ca5e32a7?publicId=b0676a50-9474-11f0-82a5-3b714d9b93ee/jaIwPnJ4jzsjS4v6uXvz/telemetry"
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
        conductivity = response.registers[2] /10.0
        ph = response.registers[3] / 10.0

        return humidity,temperature,conductivity,ph
        
        
        
def SendData(T1, H1, C1, pH1, T2, H2, C2, pH2, T3, H3, C3, pH3, T4, H4, C4, pH4):
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
        "pH_sonde3": pH3,
        "T_sonde4": T4,
        "H_sonde4": H4,
        "c_sonde4": C4,
        "pH_sonde4": pH4
    }
    requests.post(url, headers=headers, data=json.dumps(data))
        
client = ModbusSerialClient(port=port, baudrate=baudrate, timeout=timeout)
while True: 
    time.sleep(5)  # une mesure toutes les 10 s
   
    H1,T1,C1,pH1=lire_sonde(client, 0x01, "1")
    H2,T2,C2,pH2=lire_sonde(client, 0x02, "2")
    H3,T3,C3,pH3=lire_sonde(client, 0x03, "3")
    H4,T4,C4,pH4=lire_sonde(client, 0x04, "4")
    
    SendData(T1, H1, C1, pH1, T2, H2, C2, pH2, T3, H3, C3, pH3, T4, H4, C4, pH4)
    
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
    # print("sonde 4 :")
    # print(H4)
    # print(T4)
    # print(C4)
    # print(pH4)
    # print("********************")
    
    
    
    
    
client.close()
