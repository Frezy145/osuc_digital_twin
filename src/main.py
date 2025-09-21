from .utils import *


if __name__ == "__main__":
    while True:

        try: 
            get_meteo_locale()
            # get_sondes_data()

            time.sleep(3600)  # 3600 secondes = 1 heure
        except Exception as e:
            time.sleep(60) # attends 60 secondes avant de recommencer
        except KeyboardInterrupt:
            print("Arrêt du programme.")
            break
     

