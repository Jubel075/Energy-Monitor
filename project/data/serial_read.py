import serial
import sqlite3
import time

# Arduino serial connection setup (update the port as necessary)
arduino_port = 'COM8' 
baud_rate = 9600

# Database file path
db_path = r'C:\Users\user\OneDrive\Documents\Arduino\Work Folder\Energy Monitor\Data\sensor_data.db'

# Connect to the SQLite database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create the EnergyData table if it doesn't exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS EnergyData (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    Date TEXT NOT NULL,
    Irms REAL,
    Energy_Usage REAL,
    kWh REAL
)
''')
conn.commit()

# Start the serial connection
ser = serial.Serial(arduino_port, baud_rate, timeout=1)

print("Listening to Arduino and storing data in the database...")
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

            # Insert the data into the EnergyData table
            cursor.execute('''
            INSERT INTO EnergyData (Date, Irms, Energy_Usage, kWh) 
            VALUES (?, ?, ?, ?)
            ''', (Date, irms, energy_usage, kwh))
            conn.commit()  # Commit the transaction
            
            # Print the received data
            print(f"Inserted: {Date}, Irms: {irms}, Energy Usage: {energy_usage}, kWh: {kwh}")

except KeyboardInterrupt:
    print("Stopping data collection...")
finally:
    # Close the serial connection and database connection
    ser.close()
    conn.close()
    print("Connections closed.")
