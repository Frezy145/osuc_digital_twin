from pathlib import Path
import time
import sys

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from src.utils.log import log_error, log_warning
from src.utils.open_meteo import get_open_meteo
from src.utils.open_meteo import envoi_donnees_openmeteo_thingsboard as send_openmeteo_data
from src.utils.local_meteo import get_meteo_locale
from src.utils.local_meteo import send_meteo_locale as send_meteo
from src.utils.sensors import read_sensors
from src.utils.sensors import SendData as send_sensors_data
from src.utils.mail import send_data_email_to_many
from src.utils.mail import send_error_email

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
                if min_sensors_attempts == 3:
                    send_error_email(
                        f"Erreur lors de la lecture des sondes: {e}", 
                        subject="Lecture des sondes échouée", 
                        to="larazounak@gmail.com", 
                        recipient_name="Larazouna"
                    )
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
                if min_local_meteo_attempts == 3:
                    send_error_email(
                        f"Erreur lors de la recuperation de la meteo locale: {e}", 
                        subject="Meteo locale échouée", 
                        to="larazounak@gmail.com", 
                        recipient_name="Larazouna"
                    )
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
                if sensors_attempts == 3:
                    send_error_email(
                        f"Erreur envoi donnees sondes: {e}", 
                        subject="Envoi des données des sondes échoué", 
                        to="larazounak@gmail.com", 
                        recipient_name="Larazouna"
                    )
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
                if local_meteo_attempts == 3:
                    send_error_email(
                        f"Erreur recuperation meteo locale: {e}", 
                        subject="Meteo locale échouée", 
                        to="larazounak@gmail.com", 
                        recipient_name="Larazouna"
                    )
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
                if day_attempts == 3:
                    send_error_email(
                        f"Erreur recuperation previsions Open-Meteo: {e}", 
                        subject="Récupération Open-Meteo échouée", 
                        to="larazounak@gmail.com", 
                        recipient_name="Larazouna"
                    )
                time.sleep(5)  # Attendre avant de réessayer

        openmeteo_attempts = 0
        while openmeteo_attempts < 3:
            try:
                send_openmeteo_data()
                break  # Sortir de la boucle si réussi
            except Exception as e:
                openmeteo_attempts += 1
                log_warning(f"--MAIN-- Erreur envoi donnees open meteo (tentative {openmeteo_attempts})")
                log_error(f"--MAIN-- Erreur envoi donnees open meteo: {e}")
                if openmeteo_attempts == 3:
                    send_error_email(
                        f"Erreur envoi donnees open meteo: {e}", 
                        subject="Envoi Open-Meteo échoué", 
                        to="larazounak@gmail.com", 
                        recipient_name="Larazouna"
                    )
                time.sleep(5)  # Attendre avant de réessayer
    
    elif task == "1w":
        email_attempts = 0
        while email_attempts < 3:
            try:
                send_data_email_to_many()
                break  # Sortir de la boucle si réussi
            except Exception as e:
                email_attempts += 1
                log_warning(f"--MAIN-- Erreur envoi email (tentative {email_attempts})")
                log_error(f"--MAIN-- Erreur envoi email: {e}")
                if email_attempts == 3:
                    send_error_email(
                        f"Erreur envoi email: {e}", 
                        subject="Envoi des emails échoué", 
                        to="larazounak@gmail.com", 
                        recipient_name="Larazouna"
                    )
                time.sleep(5)  # Attendre avant de réessayer

    else:
        log_warning("Usage: python main.py [6min|1h|1d]")
        log_warning("  6min : Collecte des donnees des sondes toutes les 6 minutes")
        log_warning("  1h   : Envoi des donnees meteo locales sur ThingsBoard toutes les heures")
        log_warning("  1d   : Récupération des previsions Open-Meteo une fois par jour")
        log_warning("  1w   : Envoi des donnees par email aux destinataires une fois par semaine")
        send_error_email(
            "Usage: python main.py [6min|1h|1d|1w]", 
            subject="Erreur de tâche principale", 
            to="larazounak@gmail.com", 
            recipient_name="Larazouna"
        )
