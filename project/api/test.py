import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os

# Set up Google Sheets API
scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/drive']

# Update this path to point to your actual JSON file location
json_file_path = r'C:\Users\user\OneDrive\Documents\Arduino\Work Folder\Energy Monitor\API\Google Drive\energy-monitor-439602-64c11abdcf90.json' 

# Check if the JSON file exists
if not os.path.exists(json_file_path):
    print(f"Error: JSON file not found at {json_file_path}")
else:
    creds = ServiceAccountCredentials.from_json_keyfile_name(json_file_path, scope)
    client = gspread.authorize(creds)

    # Open your Google Sheet
    try:
        sheet = client.open("Energy Monitor Database").sheet1  # Replace with the name of your Google Sheet

        # Example data to write (Replace this with your actual data)
        test_data = [
            ["2024-10-23 12:03", 1.2, 127.0, 5.5, 706.0, 0.3],
            ["2024-10-23 12:04", 1.1,  127.0, 4.2, 534.0, 0.4],
            ["2024-10-23 12:05", 1.04, 127.0, 6.3, 800.1, 0.5],
        ]

        # Find the last row with data to append new data below it
        last_row = len(sheet.get_all_values()) + 1  # Get the number of rows with data
        
        # Append each row of data to the existing table
        for row in test_data:
            sheet.insert_row(row, last_row)  # Insert the new row at the last position
            last_row += 1  # Increment the last_row for the next data

        print("Data successfully written to Google Sheets:")
        for row in test_data:
            print(row)

    except gspread.SpreadsheetNotFound:
        print("Error: The specified Google Sheet was not found.")
    except Exception as e:
        print("An error occurred:", e)
