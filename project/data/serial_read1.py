import psycopg2
import sqlite3
import serial
import time
import os
from dotenv import load_dotenv
from urllib.parse import urlparse

# Load environment variables from .env file
load_dotenv()

# Parse PostgreSQL connection URL from the .env file
DATABASE_URL = os.getenv("DATABASE_URL")
url = urlparse(DATABASE_URL)

# Extract PostgreSQL connection details
PGHOST = url.hostname
PGDATABASE = url.path[1:]  # Remove the leading '/'
PGUSER = url.username
PGPASSWORD = url.password
PGPORT = url.port if url.port else 5432  # Default to 5432 if port is not specified

# Local SQLite database path
sqlite_db_path = r"C:\Users\user\OneDrive - Stichting Vanguard\Python\Energy Monitor\project\data\sensor_data.db"

# Arduino serial connection setup (update the port as necessary)
arduino_port = 'COM8'
baud_rate = 9600

# Function to create the EnergyData table in both databases if it doesn't exist
def create_tables():
    # Create table in PostgreSQL (Cloud)
    conn_pg = psycopg2.connect(
        host=PGHOST,
        database=PGDATABASE,
        user=PGUSER,
        password=PGPASSWORD,
        port=PGPORT
    )
    cursor_pg = conn_pg.cursor()
    create_table_pg_query = """
    CREATE TABLE IF NOT EXISTS EnergyData (
        id INTEGER PRIMARY KEY,
        Date TIMESTAMP NOT NULL,
        Irms FLOAT NOT NULL,
        Energy_Usage FLOAT NOT NULL,
        kWh FLOAT NOT NULL
    );
    """
    cursor_pg.execute(create_table_pg_query)
    conn_pg.commit()
    cursor_pg.close()
    conn_pg.close()
    print("Cloud table 'EnergyData' created if it didn't already exist.")

    # Create table in SQLite (Local)
    conn_sqlite = sqlite3.connect(sqlite_db_path)
    cursor_sqlite = conn_sqlite.cursor()
    create_table_sqlite_query = """
    CREATE TABLE IF NOT EXISTS EnergyData (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        Date TEXT NOT NULL,
        Irms REAL NOT NULL,
        Energy_Usage REAL NOT NULL,
        kWh REAL NOT NULL
    );
    """
    cursor_sqlite.execute(create_table_sqlite_query)
    conn_sqlite.commit()
    cursor_sqlite.close()
    conn_sqlite.close()
    print("Local table 'EnergyData' created if it didn't already exist.")

# Start the serial connection
ser = serial.Serial(arduino_port, baud_rate, timeout=1)

print("Listening to Arduino and storing data in both cloud and local databases...")
time.sleep(2)  # Allow time for Arduino to reset

# Create the tables in both databases
create_tables()

# Send signal to Arduino to start (e.g., send '1')
ser.write(b'1')
print("Signal sent to Arduino to start data collection...")

try:
    while True:
        # Read a line from the serial output
        line = ser.readline().decode('utf-8').strip()  # Read and decode the serial data

        if line.startswith("2024"):  # Ensure the line contains the expected date format
            # Split the data by commas
            data = line.split(", ")

            # Extract data components
            Date = data[0]
            irms = float(data[1])
            energy_usage = float(data[2])
            kwh = float(data[3])

            # Insert into PostgreSQL (Cloud)
            conn_pg = psycopg2.connect(
                host=PGHOST,
                database=PGDATABASE,
                user=PGUSER,
                password=PGPASSWORD,
                port=PGPORT
            )
            cursor_pg = conn_pg.cursor()
            cursor_pg.execute('''
            INSERT INTO EnergyData (Date, Irms, Energy_Usage, kWh)
            VALUES (%s, %s, %s, %s)
            ''', (Date, irms, energy_usage, kwh))
            conn_pg.commit()
            cursor_pg.close()
            conn_pg.close()

            # Insert into SQLite (Local)
            conn_sqlite = sqlite3.connect(sqlite_db_path)
            cursor_sqlite = conn_sqlite.cursor()
            cursor_sqlite.execute('''
            INSERT INTO EnergyData (Date, Irms, Energy_Usage, kWh)
            VALUES (?, ?, ?, ?)
            ''', (Date, irms, energy_usage, kwh))
            conn_sqlite.commit()
            cursor_sqlite.close()
            conn_sqlite.close()

            # Print the received data
            print(f"Inserted: {Date}, Irms: {irms}, Energy Usage: {energy_usage}, kWh: {kwh}")

except KeyboardInterrupt:
    print("Stopping data collection...")
finally:
    # Close the serial connection
    ser.close()
    print("Connections closed.")
