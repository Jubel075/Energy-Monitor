import psycopg2
import time
import os
from dotenv import load_dotenv
import serial

# Load environment variables
load_dotenv()

# Database connection details from the .env file
PGHOST = os.getenv("PGHOST")
PGDATABASE = os.getenv("PGDATABASE")
PGUSER = os.getenv("PGUSER")
PGPASSWORD = os.getenv("PGPASSWORD")

# Arduino serial connection setup (update the port as necessary)
arduino_port = 'COM8'
baud_rate = 9600

# Function to create the EnergyData table if it doesn't exist
def create_table():
    # Connect to the PostgreSQL database
    conn = psycopg2.connect(
        host=PGHOST,
        database=PGDATABASE,
        user=PGUSER,
        password=PGPASSWORD
    )
    cursor = conn.cursor()

    # Create table if it doesn't exist
    create_table_query = """
    CREATE TABLE IF NOT EXISTS EnergyData (
        id SERIAL PRIMARY KEY,
        Date TIMESTAMP NOT NULL,
        Irms FLOAT NOT NULL,
        Energy_Usage FLOAT NOT NULL,
        kWh FLOAT NOT NULL
    );
    """
    cursor.execute(create_table_query)

    # Commit and close the connection
    conn.commit()
    cursor.close()
    conn.close()
    print("Table 'EnergyData' has been created if it didn't already exist.")

# Start the serial connection
ser = serial.Serial(arduino_port, baud_rate, timeout=1)

print("Listening to Arduino and storing data in the cloud database...")
time.sleep(2)  # Allow time for Arduino to reset

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

            # Connect to the PostgreSQL database
            conn = psycopg2.connect(
                host=PGHOST,
                database=PGDATABASE,
                user=PGUSER,
                password=PGPASSWORD
            )
            cursor = conn.cursor()

            # Insert the data into the EnergyData table
            cursor.execute('''
            INSERT INTO EnergyData (Date, Irms, Energy_Usage, kWh)
            VALUES (%s, %s, %s, %s)
            ''', (Date, irms, energy_usage, kwh))
            conn.commit()  # Commit the transaction

            # Print the received data
            print(f"Inserted: {Date}, Irms: {irms}, Energy Usage: {energy_usage}, kWh: {kwh}")

            # Close the connection after each insert
            cursor.close()
            conn.close()

except KeyboardInterrupt:
    print("Stopping data collection...")
finally:
    # Close the serial connection
    ser.close()
    print("Connections closed.")
