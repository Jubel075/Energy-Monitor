import serial
import time
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Set up Google Sheets API
scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('energy-monitor-439602-64c11abdcf90.json', scope)  # Replace with your JSON file
client = gspread.authorize(creds)
sheet = client.open("Energy Monitor Database").sheet1                                                        # Replace with the name of your Google Sheet

# Set up Arduino serial communication
ser = serial.Serial('COM3', 9600)  # Replace 'COM3' with your Arduino port

# Wait for the serial connection to initialize
time.sleep(2)

while True:
    try:
        data = ser.readline().decode('utf-8').strip()  # Read data from Arduino
        if data.startswith("DATA"):  # Check if the line starts with "DATA"
            # Split the incoming data by comma
            values = data.split(",")[1:]  # Skip "DATA," and take the rest
            # Append data to Google Sheet
            sheet.append_row(values)  # Append the data as a new row in the sheet
            print("Data added to Google Sheets:", values)  # Print the values added
    except Exception as e:
        print("Error:", e)  # Print any errors that occur
