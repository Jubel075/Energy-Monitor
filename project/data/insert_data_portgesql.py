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

# Function to generate and insert random data every 10 days for 4 months
def generate_random_data():
    # Connect to the PostgreSQL database
    conn = psycopg2.connect(
        host=PGHOST,
        database=PGDATABASE,
        user=PGUSER,
        password=PGPASSWORD
    )
    cursor = conn.cursor()

    # Set the initial datetime for the first entry (January 1, 2024)
    current_date = datetime(2024, 1, 1)  # Starting from 2024-01-01

    # Set the end date to April 30, 2024 (4 months later)
    end_date = datetime(2024, 4, 30)

    # Generate random data every 10 days within the specified time range
    while current_date <= end_date:
        # Generate a random time (hour, minute, second) for the current_date
        random_time = current_date.replace(
            hour=random.randint(0, 23),
            minute=random.randint(0, 59),
            second=random.randint(0, 59)
        )

        # Random values for Irms, Energy_Usage, and kWh
        Irms = round(random.uniform(10.5, 10.8), 2)  # Random value between 10.5 and 10.8
        Energy_Usage = round(random.uniform(13450, 13600), 2)  # Random value between 13450 and 13600
        kWh = round(random.uniform(0, 0.05), 2)  # Random value between 0 and 0.05

        # Insert the generated data into the database
        query = """
        INSERT INTO EnergyData (Date, Irms, Energy_Usage, kWh)
        VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (random_time, Irms, Energy_Usage, kWh))

        # Increment the current date by 10 days for the next entry
        current_date += timedelta(days=10)

    # Commit the transaction and close the connection
    conn.commit()
    cursor.close()
    conn.close()

    print("Random data for January to April 2024 has been inserted into the database every 10 days.")

# Run the functions to create the table and insert data
if __name__ == "__main__":
    create_table()  # Ensure the table exists
    generate_random_data()  # Insert random data
