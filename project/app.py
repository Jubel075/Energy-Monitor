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
    
    # Filter data based on the selected month or day
    if selected_month:
        df = df[df['month'] == selected_month]
    
    if selected_day and selected_day != 'None':
        df = df[df['day'] == int(selected_day)]
    
    # Group data by day or hour, and aggregate
    if group_by == 'day':
        df = df.groupby(['year', 'month', 'day']).agg({tab: 'sum'}).reset_index()
    elif group_by == 'hour':
        df = df.groupby(['year', 'month', 'day', 'hour']).agg({tab: 'sum'}).reset_index()

    return df


# Route for getting day options based on the selected month
@app.route('/days', methods=['GET'])
def get_days():
    selected_month = request.args.get('month')
    df = get_data(tab='irms', selected_month=selected_month)
    days = df['day'].unique().tolist()
    return jsonify(days)

# Route to render the homepage with Plotly graph
@app.route('/', methods=['GET'])
def index():
    selected_month = request.args.get('month')
    selected_day = request.args.get('day')
    selected_tab = request.args.get('tab', 'irms')  # Default to 'irms' tab if none is selected

    if not selected_month and not selected_day:
        df = get_data(tab=selected_tab)
    else:
        group_by = 'hour' if selected_day else 'day'
        df = get_data(tab=selected_tab, group_by=group_by, selected_month=selected_month, selected_day=selected_day)

    # Create a Plotly figure based on the selected tab and filters
    fig = go.Figure()

    if selected_day:
        fig.add_trace(go.Bar(
            x=df['hour'], 
            y=df[selected_tab], 
            name=selected_tab,
            text=df[selected_tab], 
            textposition='auto'
        ))
        fig.update_layout(title=f"Accumulated {selected_tab} for {selected_day} - {selected_month}")
    elif selected_month:
        fig.add_trace(go.Bar(
            x=df['day'], 
            y=df[selected_tab], 
            name=selected_tab,
            text=df[selected_tab], 
            textposition='auto'
        ))
        fig.update_layout(title=f"Accumulated {selected_tab} for {selected_month}")
    else:
        fig.add_trace(go.Scatter(
            x=df['date'], 
            y=df[selected_tab], 
            mode='lines', 
            name=selected_tab,
            text=df[selected_tab],  
            textposition='top center'
        ))
        fig.update_layout(title=f"Raw {selected_tab} Data")

    fig.update_layout(width=1150, height=600)
    graph_html = fig.to_html(full_html=False)
    
    # Generate month options
    df_all = get_data(tab='irms')
    month_options = [{"label": month, "value": month} for month in df_all['month'].unique()]
    
    return render_template('index.html', graph_html=graph_html, month_options=month_options, selected_month=selected_month, selected_day=selected_day, selected_tab=selected_tab)

if __name__ == '__main__':
    app.run(debug=True)
