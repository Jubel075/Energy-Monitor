# Energy Monitoring System

This project involves an energy monitoring system using an Arduino to measure current, calculate energy consumption, and log the data into a PostgreSQL database hosted on Neon. The data is read through the Arduino's serial output and stored in a table for further analysis. Additionally, the data is displayed on a web app built using Flask and Dash, allowing users to visualize the data.

## Project Overview

The energy monitor system consists of two main components:
1. **Arduino Code**: Measures current, calculates power and energy usage, and sends data in CSV format over the serial port.
2. **Python Script**: Reads the serial output from the Arduino, parses the data, and logs it into a PostgreSQL database. It also serves a web dashboard for data visualization.

### Components
- **Hardware**: Arduino, CT Sensor, resistors, and connecting wires.
- **Libraries**: [EmonLib](https://github.com/openenergymonitor/EmonLib) for current and voltage monitoring on the Arduino.
- **Software**: Python, SQLite (local database for testing), PostgreSQL (live cloud database via Neon), Flask, and Dash for web visualization.

## Setup

### 1. Hardware Setup
   - Connect the CT sensor to the Arduino according to the [EmonLib setup instructions](https://github.com/openenergymonitor/EmonLib).
   - Configure the Arduino pins in the code as needed.

### 2. Software Installation
   - **Arduino IDE**: Download and install the Arduino IDE for uploading the code to the Arduino.
   - **Python**: Ensure Python 3.x is installed.
   - **SQLite**: Pre-installed with Python, but verify its presence.
   - **PostgreSQL**: For live cloud database access (Neon), ensure the credentials and connection details are configured in the Python script.

### 3. Python Libraries
Install the necessary libraries for serial communication and database connection if they’re not installed yet:
   ```bash
   pip install pyserial psycopg2 flask dash
   ```

### 4. Upload Arduino Code
   - Copy the `EnergyMonitor` code provided in `EnergyMonitor.ino` into the Arduino IDE.
   - Set the correct COM port and upload the code to your Arduino.

### 5. Configure Python Script
   - Update the `arduino_port` variable in `data_logger.py` to match your Arduino's COM port.
   - Update the `db_host`, `db_name`, `db_user`, and `db_password` variables to connect to your PostgreSQL cloud database on Neon.
   - If using SQLite for local testing, update the `db_path` variable to the desired file path for your SQLite database.

## Running the Project

1. **Run the Python Script**:
   ```bash
   python data_logger.py
   ```
   - The script will create a table called `EnergyData` in the specified database file (or PostgreSQL cloud database) if it doesn’t already exist.

2. **Data Collection**:
   - The Arduino sends data every 10 seconds in the format: `Date, Irms, Energy_Usage, kWh`.
   - The Python script listens on the serial port, logs the data into the database, and outputs it to the console.

3. **Web Dashboard**:
   - You can view the collected data using the web app. The Flask and Dash app is served locally or can be deployed to the cloud for remote access.
   - The dashboard allows users to select a year and month for data visualization and includes trendline charts for monthly data and hourly breakdowns for daily data.

4. **Stopping the Script**:
   - Press `Ctrl+C` in the terminal to stop data collection.
   - The script will automatically close the serial and database connections.

## Database Schema

The PostgreSQL database logs data into the `EnergyData` table with the following columns:

| Column Name   | Data Type   | Description                        |
|---------------|-------------|------------------------------------|
| `id`          | SERIAL      | Auto-incremented primary key.      |
| `Date`        | TEXT        | Date and time of the measurement.  |
| `Irms`        | REAL        | Root mean square of current (A).   |
| `Energy_Usage`| REAL        | Energy used over the interval (Wh).|
| `kWh`         | REAL        | Cumulative energy consumption (kWh).|

## Notes

- Ensure the serial connection to the Arduino is stable. Disconnecting or reconnecting the Arduino may require restarting the Python script.
- Data is logged every 10 seconds. This interval can be adjusted in the Arduino code by changing the `MEASURE_INTERVAL` constant.
- Adjust the voltage and current calibration values in the Arduino code as necessary for accurate readings.

## Example Output

Upon successful execution, the console output will look like:

```plaintext
Listening to Arduino and storing data in the database...
Inserted: 2024-10-30 12:00:10, Irms: 0.85, Energy Usage: 1.02, kWh: 0.0001
Inserted: 2024-10-30 12:00:20, Irms: 0.87, Energy Usage: 1.04, kWh: 0.0002
...
```

## Troubleshooting

- **Serial Port Errors**: Verify the correct COM port in the Python script.
- **Database Connection Errors**: Ensure your PostgreSQL credentials and connection details are correct. For SQLite, ensure the `db_path` directory exists and is accessible.
- **Data Parsing Errors**: Confirm the Arduino outputs in the expected format, especially the date and time string.

## License

This project is licensed under Vanguard Community College.
```

Let me know if you need any further adjustments!
