from flask import Flask, render_template, jsonify, request
import pandas as pd
import plotly.graph_objects as go
from dotenv import load_dotenv
import os
import psycopg2
from psycopg2 import OperationalError

app = Flask(__name__)

# Load environment variables from the .env file
load_dotenv()

# Get the database connection URL from environment variables
DATABASE_URL = os.getenv("DATABASE_URL")

# Function to fetch and format data from the PostgreSQL database
def get_data(tab, group_by=None, selected_month=None, selected_day=None):
    try:
        # Connect to the PostgreSQL database using the connection URL
        conn = psycopg2.connect(DATABASE_URL)
        
        # Define the query to fetch data from the database
        query = "SELECT date, irms, energy_usage, kwh FROM energydata"  # Adjusted column names

        # Read the data from the database
        df = pd.read_sql_query(query, conn)
        conn.close()
        
    except OperationalError as e:
        print("Error connecting to the database:", e)
        return pd.DataFrame()  # Return an empty DataFrame if there's a connection error

    # Handle the date column
    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month_name()
    df['day'] = df['date'].dt.day
    df['hour'] = df['date'].dt.hour
    df = df.sort_values(by='date')

    # Filter by month and day if provided
    if selected_month:
        df = df[df['month'] == selected_month]
        # Sort by day after filtering by month
        df = df.sort_values(by=['day', 'date'])
    if selected_day:
        df = df[df['day'] == int(selected_day)]
        # Sort by hour after filtering by day
        df = df.sort_values(by=['hour', 'date'])

    return df


# Route for the homepage
# Route for the homepage
@app.route('/')
def index():
    selected_month = request.args.get('month')
    selected_day = request.args.get('day')
    selected_tab = request.args.get('tab', 'irms')

    # Get the data based on the selected filters
    df = get_data(tab=selected_tab, selected_month=selected_month, selected_day=selected_day)

    # Prepare the data for the graph
    fig = go.Figure()

    # Set axis titles and graph data based on selected tab
    if selected_tab == 'irms':
        fig.add_trace(go.Scatter(x=df['date'], y=df['irms'], mode='lines', name='Irms'))
        fig.update_layout(
            title="Current (Irms)",
            xaxis_title="Date",
            yaxis_title="Current (A)"
        )
    elif selected_tab == 'energy_usage':
        fig.add_trace(go.Scatter(x=df['date'], y=df['energy_usage'], mode='lines', name='Energy Usage'))
        fig.update_layout(
            title="Energy Usage (Ws)",
            xaxis_title="Date",
            yaxis_title="Energy (Ws)"
        )
    else:  # kWh tab
        fig.add_trace(go.Scatter(x=df['date'], y=df['kwh'], mode='lines', name='kWh'))
        fig.update_layout(
            title="Energy Consumption (kWh)",
            xaxis_title="Date",
            yaxis_title="kWh"
        )

    graph_html = fig.to_html(full_html=False)

    # Prepare the month and day options for the dropdown
    month_options = [{'value': month, 'label': month} for month in df['month'].unique()]
    day_options = df['day'].unique().tolist()

    return render_template('index.html', 
                           graph_html=graph_html,
                           selected_month=selected_month, 
                           selected_day=selected_day,
                           selected_tab=selected_tab,
                           month_options=month_options,
                           day_options=day_options)


# Route to fetch available days for the selected month
@app.route('/days', methods=['GET'])
def get_days():
    selected_month = request.args.get('month')
    df = get_data(tab='irms', selected_month=selected_month)
    days = df['day'].unique().tolist()
    return jsonify(days)

if __name__ == '__main__':
    app.run(debug=True)
