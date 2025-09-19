# here is the main code 

import os

import requests
from . import get_meteo_locale, init_csv, filename, colonnes_a_garder

def main():
    response = requests.get("https://api.example.com/data")
    if response.status_code == 200:
        print("Data retrieved successfully:")
        print(response.json())
    else:
        print("Failed to retrieve data.")

if __name__ == "__main__":
    main()