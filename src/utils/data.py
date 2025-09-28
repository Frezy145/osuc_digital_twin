
import pandas as pd
from pathlib import Path
import os
import shutil
import sys
import glob
from datetime import datetime
from datetime import timezone

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from src.utils.log import log_error, log_info, log_warning

if not os.path.exists(f"{BASE_DIR}/db"):
    os.makedirs(f"{BASE_DIR}/db")

output_csv = f"{BASE_DIR}/db/data.csv"
archive_dir = f"{BASE_DIR}/db/archive"
archive_pattern = f"{archive_dir}/data_*.csv"

if not os.path.exists(archive_dir):
    os.makedirs(archive_dir)

def init_csv(return_df=True, reinitialize=False):
    # Initialiser le CSV avec les en-têtes si le fichier n'existe pas
    if not os.path.isfile(output_csv) or reinitialize:
        df = pd.DataFrame(columns=[
            "date", 
            "temperature_om", "humidity_om", "pressure_om",
            "wind_speed_om", "wind_direction_om", "precipitation_om",
            "soil_temperature_6cm_om", "soil_temperature_18cm_om", "soil_temperature_54cm_om",

            "solarRadiation", "epoch", "winddir", "humidity", "metric_temp", "metric_windSpeed",
            "metric_windGust", "metric_pressure", "metric_precipRate", "metric_precipTotal",

            "T_sonde1", "H_sonde1", "c_sonde1", "pH_sonde1",
            "T_sonde2", "H_sonde2", "c_sonde2", "pH_sonde2",
            "T_sonde3", "H_sonde3", "c_sonde3", "pH_sonde3",
            "T_sonde4", "H_sonde4", "c_sonde4", "pH_sonde4",

        ])
        df.to_csv(output_csv, index=False)

    if return_df:
        return pd.read_csv(output_csv)  

def archive(keep=3):
    try:
        if os.path.isfile(output_csv):
            date_str = datetime.now(tz=timezone.utc).strftime("%Y_%m_%d")
            archive_file = f"{archive_dir}/data_{date_str}.csv"
            shutil.copy2(output_csv, archive_file)
            log_info(f"--DATA-- Archived data to {archive_file}")
            cleanup_old_archives(keep=keep)
            init_csv(reinitialize=True)  # Reinitialize main CSV
        else:
            log_warning(f"--DATA-- No data file {output_csv} to archive.")
    except Exception as e:
        log_error(f"--DATA-- Error during archiving: {e}")

def cleanup_old_archives(keep=3):

    try:
        archives = glob.glob(archive_pattern)
        if len(archives) <= keep:
            return
        archives.sort(key=os.path.getmtime, reverse=True)
        for old_file in archives[keep:]:
            os.remove(old_file) 
        
    except Exception as e:
       log_error(f"--DATA-- Error during cleanup_old_archives: {e}")

def save_cell(date, column, value, df=None, save=True):
    if df is None:
        df = init_csv()

    if date in df['date'].values:
        df.loc[df['date'] == date, column] = value
    else:
        new_index = len(df)
        df.loc[new_index] = None
        df.at[new_index, 'date'] = date
        df.at[new_index, column] = value

    if save:
        df.to_csv(output_csv, index=False)
    else:
        return df

def save_hourly_data(data_dict, time=None, df=None, save=True):

    if df is None:
        old_df = init_csv()
    else:
        old_df = df

    df = old_df.copy()

    if time is None:
        time = datetime.now(tz=timezone.utc).replace(minute=0, second=0, microsecond=0).strftime("%Y-%m-%d %H:%M:%S")
    else: # Ensure time is in correct format
        if isinstance(time, (int, float)):  # If epoch time
            time = datetime.fromtimestamp(time, tz=timezone.utc).replace(minute=0, second=0, microsecond=0).strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(time, str):  # If string format
            time = datetime.fromisoformat(time).replace(minute=0, second=0, microsecond=0).strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(time, datetime):
            time = time.astimezone(timezone.utc).replace(minute=0, second=0, microsecond=0).strftime("%Y-%m-%d %H:%M:%S")

    for column, value in data_dict.items():
        df = save_cell(time, column, value, df=df, save=False)

    # if df is updated, save it
    if save:
        if not df.equals(old_df):
            df.to_csv(output_csv, index=False)
    else:
        return df

def save_dataframe(df):
    old_df = init_csv()
    new_df = old_df.copy()

    for _, row in df.iterrows():
        time = row['date']
        data_dict = row.drop(labels=['date']).to_dict()
        new_df = save_hourly_data(data_dict, time=time, df=new_df, save=False)

    if not new_df.equals(old_df):   
        new_df.to_csv(output_csv, index=False)
