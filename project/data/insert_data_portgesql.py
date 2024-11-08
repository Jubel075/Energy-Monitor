import psycopg2
import random
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection details from the .env file
PGHOST = os.getenv("PGHOST")
PGDATABASE = os.getenv("PGDATABASE")
PGUSER = os.getenv("PGUSER")
PGPASSWORD = os.getenv("PGPASSWORD")

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

# Function to generate and insert random data
def generate_random_data():
    # Connect to the PostgreSQL database
    conn = psycopg2.connect(
        host=PGHOST,
        database=PGDATABASE,
        user=PGUSER,
        password=PGPASSWORD
    )
    cursor = conn.cursor()

    # Set the initial datetime for the first entry
    current_time = datetime(2024, 10, 30, 12, 0, 0)  # Starting from 2024-10-30 12:00:00

    # Generate 5 random data entries (you can modify the range for more data)
    for i in range(100):
        # Random values for Irms, Energy_Usage, and kWh
        Irms = round(random.uniform(10.5, 10.8), 2)  # Random value between 10.5 and 10.8
        Energy_Usage = round(random.uniform(13450, 13600), 2)  # Random value between 13450 and 13600
        kWh = round(random.uniform(0, 0.05), 2)  # Random value between 0 and 0.05

        # Insert the generated data into the database
        query = """
        INSERT INTO EnergyData (Date, Irms, Energy_Usage, kWh)
        VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (current_time, Irms, Energy_Usage, kWh))

        # Increment the current time by 10 seconds for the next entry
        current_time += timedelta(seconds=10)

    # Commit the transaction and close the connection
    conn.commit()
    cursor.close()
    conn.close()

    print("Random data has been inserted into the database.")

# Run the functions to create the table and insert data
if __name__ == "__main__":
    create_table()  # Ensure the table exists
    generate_random_data()  # Insert random data
