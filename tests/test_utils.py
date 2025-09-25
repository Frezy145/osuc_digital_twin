# This module contains tests for the utils module

import os
import sys
from pathlib import Path
import pytest
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent

if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from src.utils.sensors import init_csv, fill_csv, read_csv_and_compute_mean, read_sensors, SendData, read_sensor
from src.utils.log import log_error, log_info, log_warning
from src.utils.mail import email
from src.utils.open_meteo import get_open_meteo, envoi_donnees_openmeteo_thingsboard as send_openmeteo_data
from src.utils.local_meteo import API_KEY, STATION_ID, get_meteo_locale, send_meteo_locale as send_meteo, init_csv as init_local_meteo_csv

@pytest.fixture
def setup_and_teardown():
    # Setup: Initialize CSV files
    init_csv(reinitialize=True)
    init_local_meteo_csv(reinitialize=True)

    output_csv = f"{BASE_DIR}/db/OpenMeteo_forecast.csv"

    yield
    # Teardown: Remove CSV files after tests
    try:
        os.remove(f"{BASE_DIR}/db/sensors_data.csv")
    except FileNotFoundError:
        pass

    try:
        os.remove(f"{BASE_DIR}/db/local_meteo_data.csv")
    except FileNotFoundError:
        pass

    try:
        os.remove(output_csv)
    except FileNotFoundError:
        pass

def test_init_csv(setup_and_teardown):
    assert os.path.exists(f"{BASE_DIR}/db/sensors_data.csv")
    with open(f"{BASE_DIR}/db/sensors_data.csv", "r", encoding="utf-8") as f:
        header = f.readline().strip()
        expected_header = "Timestamp,T_sonde1,H_sonde1,c_sonde1,pH_sonde1,T_sonde2,H_sonde2,c_sonde2,pH_sonde2,T_sonde3,H_sonde3,c_sonde3,pH_sonde3,T_sonde4,H_sonde4,c_sonde4,pH_sonde4"
        assert header == expected_header
    assert os.path.exists(f"{BASE_DIR}/db/local_meteo_data.csv")
    with open(f"{BASE_DIR}/db/local_meteo_data.csv", "r", encoding="utf-8") as f:
        header = f.readline().strip()
        expected_header = "solarRadiation,epoch,winddir,humidity,metric_temp,metric_windSpeed,metric_windGust,metric_pressure,metric_precipRate,metric_precipTotal"
        assert header == expected_header

def test_fill_csv_and_read_mean(setup_and_teardown):    
    fill_csv(20.5, 55, 1.2, 7.0, 21.0, 60, 1.3, 7.1, 19.5, 50, 1.1, 6.9, 22.0, 65, 1.4, 7.2)
    fill_csv(22.5, 65, 1.5, 7.3, 23.0, 70, 1.6, 7.4, 21.5, 60, 1.3, 7.1, 24.0, 75, 1.7, 7.5)
    mean_values = read_csv_and_compute_mean()
    assert mean_values is not None
    assert round(mean_values["T_sonde1"], 2) == 21.5
    assert round(mean_values["H_sonde1"], 2) == 60.0
    assert round(mean_values["c_sonde1"], 2) == 1.35
    assert round(mean_values["pH_sonde1"], 2) == 7.15
    assert round(mean_values["T_sonde2"], 2) == 22.0
    assert round(mean_values["H_sonde2"], 2) == 65.0
    assert round(mean_values["c_sonde2"], 2) == 1.45
    assert round(mean_values["pH_sonde2"], 2) == 7.25
    assert round(mean_values["T_sonde3"], 2) == 20.5
    assert round(mean_values["H_sonde3"], 2) == 55.0
    assert round(mean_values["c_sonde3"], 2) == 1.2
    assert round(mean_values["pH_sonde3"], 2) == 7.0
    assert round(mean_values["T_sonde4"], 2) == 23.0
    assert round(mean_values["H_sonde4"], 2) == 70.0    
    assert round(mean_values["c_sonde4"], 2) == 1.55
    assert round(mean_values["pH_sonde4"], 2) == 7.35

def test_read_sensors():
    # get system 
    system = sys.platform
    if system.startswith("linux"):
        try:
            read_sensors()
        except Exception as e:
            pytest.fail(f"read_sensors() raised an exception: {e}")
        # Check if data was written to CSV
        assert os.path.exists(f"{BASE_DIR}/db/sensors_data.csv")
        with open(f"{BASE_DIR}/db/sensors_data.csv", "r", encoding="utf-8") as f:
            lines = f.readlines()
            assert len(lines) >= 2  # Header + at least one data line
    else:
        pytest.skip("Skipping read_sensors test on non-Linux systems")

def test_get_open_meteo(setup_and_teardown):
    output_csv = f"{BASE_DIR}/db/OpenMeteo_forecast.csv"
    get_open_meteo()
    assert os.path.exists(output_csv)
    df_om = pd.read_csv(output_csv)
    expected_columns = [
        "date", "temperature_om", "humidity_om", "pressure_om", 
        "wind_speed_om", "wind_direction_om", "precipitation_om",
        "soil_temperature_6cm_om", "soil_temperature_18cm_om", "soil_temperature_54cm_om"
    ]
    for col in expected_columns:
        assert col in df_om.columns
    assert not df_om.empty
    assert len(df_om) >= 24  # At least 24 hours of data
    # Check for NaN values in critical columns
    critical_columns = [
        "temperature_om", "humidity_om", "pressure_om", 
        "wind_speed_om", "wind_direction_om", "precipitation_om"
    ]
    for col in critical_columns:
        assert df_om[col].isnull().sum() == 0, f"Column {col} contains NaN values"

def test_send_openmeteo_data(setup_and_teardown):
    get_open_meteo()  # Ensure data is available
    
    try:
        send_openmeteo_data()
    except Exception as e:
        pytest.fail(f"send_openmeteo_data() raised an exception: {e}")

def test_get_meteo_locale_and_send(setup_and_teardown):
    if not API_KEY or not STATION_ID:
        pytest.skip("API_KEY or STATION_ID not set. Skipping local meteo tests.")
    
    try:
        get_meteo_locale()
    except Exception as e:
        pytest.fail(f"get_meteo_locale() raised an exception: {e}")
    
    # Check if data was written to CSV
    assert os.path.exists(f"{BASE_DIR}/db/local_meteo_data.csv")
    with open(f"{BASE_DIR}/db/local_meteo_data.csv", "r", encoding="utf-8") as f:
        lines = f.readlines()
        assert len(lines) >= 2  # Header + at least one data line

    try:
        send_meteo()
    except Exception as e:
        pytest.fail(f"send_meteo() raised an exception: {e}")

def test_read_sensor_mocked(mocker):
    class MockResponse:
        def __init__(self, registers, error=False):
            self.registers = registers
            self._error = error
        
        def isError(self):
            return self._error

    # Mock client
    mock_client = mocker.Mock()

    # Test successful read
    mock_client.read_holding_registers.return_value = MockResponse([550, 205, 120, 70])
    result = read_sensor(mock_client, slave_id=1, label="TestSensor")
    assert result == (55.0, 20.5, 12.0, 7.0)

    # Test error in read
    mock_client.read_holding_registers.return_value = MockResponse([], error=True)
    result = read_sensor(mock_client, slave_id=1, label="TestSensor")
    assert result is None   

def test_send_data_no_exception(mocker):
    mocker.patch('pymodbus.client.ModbusSerialClient', autospec=True)
    mocker.patch('src.utils.sensors.read_csv_and_compute_mean', return_value={
        "T_sonde1": 20.5, "H_sonde1": 55, "c_sonde1": 1.2, "pH_sonde1": 7.0,
        "T_sonde2": 21.0, "H_sonde2": 60, "c_sonde2": 1.3, "pH_sonde2": 7.1,
        "T_sonde3": 19.5, "H_sonde3": 50, "c_sonde3": 1.1, "pH_sonde3": 6.9,
        "T_sonde4": 22.0, "H_sonde4": 65, "c_sonde4": 1.4, "pH_sonde4": 7.2
    })
    mock_send = mocker.patch('requests.post', autospec=True)

    try:
        SendData()
    except Exception as e:
        pytest.fail(f"SendData() raised an exception: {e}")

    assert mock_send.called 

def test_send_data_no_data(mocker):
    mocker.patch("pymodbus.client.ModbusSerialClient", autospec=True)
    mocker.patch("src.utils.sensors.read_csv_and_compute_mean", return_value=None)
    mock_send = mocker.patch("requests.post", autospec=True)

    try:
        SendData()
    except Exception as e:
        pytest.fail(f"SendData() raised an exception: {e}")

    assert not mock_send.called  # Should not attempt to send data if none is available 
    
# test email function
def test_email_no_exception(mocker):
    mock_send = mocker.patch("smtplib.SMTP", autospec=True)
    try:
        email("Test Subject", "This is a test email body.")
    except Exception as e:
        pytest.fail(f"email() raised an exception: {e}")
    assert mock_send.called

