from pathlib import Path
import time
import sys

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from utils.log import log_error, log_warning
from utils.open_meteo import get_open_meteo
from utils.open_meteo import envoi_donnees_openmeteo_thingsboard as send_openmeteo_data
from utils.local_meteo import get_meteo_locale
from utils.local_meteo import send_meteo_locale as send_meteo
from utils.sensors import read_sensors
from utils.sensors import SendData as send_sensors_data


if __name__ == "__main__":

    task = sys.argv[1] if len(sys.argv) > 1 else None

    if task == "6min": 
        min_sensors_attempts = 0
        while min_sensors_attempts < 3:
            try:
                read_sensors()
                break  # Sortir de la boucle si réussi
            except Exception as e:
                min_sensors_attempts += 1
                log_warning(f"--MAIN-- Erreur lecture sondes (tentative {min_sensors_attempts})")
                log_error(f"--MAIN-- Erreur lors de la lecture des sondes: {e}")
                time.sleep(5)  # Attendre avant de réessayer
        
        min_local_meteo_attempts = 0
        while min_local_meteo_attempts < 3:
            try:
                get_meteo_locale()
                break  # Sortir de la boucle si réussi
            except Exception as e:
                min_local_meteo_attempts += 1
                log_warning(f"--MAIN-- Erreur recuperation meteo locale (tentative {min_local_meteo_attempts})")
                log_error(f"--MAIN-- Erreur lors de la recuperation de la meteo locale: {e}")
                time.sleep(5)  # Attendre avant de réessayer

    elif task == "1h": 

        sensors_attempts = 0
        while sensors_attempts < 3:
            try:
                send_sensors_data()
                break  # Sortir de la boucle si réussi
            except Exception as e:
                sensors_attempts += 1
                log_warning(f"--MAIN-- Erreur envoi donnees sondes (tentative {sensors_attempts})")
                log_error(f"--MAIN-- Erreur envoi donnees sondes: {e}")
                time.sleep(5)  # Attendre avant de réessayer
        
        local_meteo_attempts = 0
        while local_meteo_attempts < 3:
            try:
                send_meteo()
                break  # Sortir de la boucle si réussi
            except Exception as e:
                local_meteo_attempts += 1
                log_warning(f"--MAIN-- Erreur recuperation meteo locale (tentative {local_meteo_attempts})")
                log_error(f"--MAIN-- Erreur recuperation meteo locale: {e}")
                time.sleep(5)  # Attendre avant de réessayer

        openmeteo_attempts = 0
        while openmeteo_attempts < 3:
            try:
                send_openmeteo_data()
                break  # Sortir de la boucle si réussi
            except Exception as e:
                openmeteo_attempts += 1
                log_warning(f"--MAIN-- Erreur envoi donnees meteo (tentative {openmeteo_attempts})")
                log_error(f"--MAIN-- Erreur envoi donnees meteo: {e}")
                time.sleep(5)  # Attendre avant de réessayer
        
    elif task == "1d":
        day_attempts = 0
        while day_attempts < 3:
            try:
                get_open_meteo()
                break  # Sortir de la boucle si réussi
            except Exception as e:
                day_attempts += 1
                log_warning(f"--MAIN-- Erreur recuperation previsions Open-Meteo (tentative {day_attempts})")
                log_error(f"--MAIN-- Erreur recuperation previsions Open-Meteo: {e}")
                time.sleep(5)  # Attendre avant de réessayer

    else:
        log_warning("Usage: python main.py [6min|1h|1d]")
        log_warning("  6min : Collecte des donnees des sondes toutes les 6 minutes")
        log_warning("  1h   : Envoi des donnees meteo locales sur ThingsBoard toutes les heures")
        log_warning("  1d   : Récupération des previsions Open-Meteo une fois par jour")


