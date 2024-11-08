from flask import Flask, render_template, jsonify, request
import pandas as pd
import plotly.graph_objects as go
from dotenv import load_dotenv
import os
import psycopg2

app = Flask(__name__)

# Load environment variables from the .env file
load_dotenv()

# Get the database connection details from environment variables
PGHOST = os.getenv("PGHOST")
PGDATABASE = os.getenv("PGDATABASE")
PGUSER = os.getenv("PGUSER")
PGPASSWORD = os.getenv("PGPASSWORD")

# Function to fetch and format data from the PostgreSQL database
def get_data(tab, group_by=None, selected_month=None, selected_day=None):
    # Connect to the PostgreSQL database
    conn = psycopg2.connect(
        host=PGHOST,
        database=PGDATABASE,
        user=PGUSER,
        password=PGPASSWORD
    )
    
    # Define the query to fetch data from the database
    query = "SELECT date, irms, energy_usage, kwh FROM energydata"  # Adjusted column names

    # Read the data from the database
    df = pd.read_sql_query(query, conn)
    conn.close()

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
    
    if selected_day and selected_day != 'None':  # Check if selected_day is not 'None'
        df = df[df['day'] == int(selected_day)]
    
    # Group data by day or hour, and aggregate (sum for Irms, Energy Usage, and kWh)
    if group_by == 'day':
        df = df.groupby(['year', 'month', 'day']).agg({tab: 'sum'}).reset_index()
    elif group_by == 'hour':
        df = df.groupby(['year', 'month', 'day', 'hour']).agg({tab: 'sum'}).reset_index()

    return df


# Route for getting day options based on the selected month
@app.route('/days', methods=['GET'])
def get_days():
    selected_month = request.args.get('month')
    df = get_data(tab='irms', selected_month=selected_month)  # Get data filtered by the selected month
    days = df['day'].unique().tolist()
    return jsonify(days)

# Route to render the homepage with Plotly graph
@app.route('/', methods=['GET'])
def index():
    selected_month = request.args.get('month')  # Get the selected month from query parameters
    selected_day = request.args.get('day')  # Get the selected day from query parameters
    selected_tab = request.args.get('tab', 'irms')  # Default to 'irms' tab if none is selected

    # If no month or day is selected, show raw data (i.e., no grouping)
    if not selected_month and not selected_day:
        df = get_data(tab=selected_tab)  # Fetch raw data for the selected tab
    else:
        # Otherwise, fetch the data (grouped by day or hour) based on the selection
        group_by = 'hour' if selected_day else 'day'  # Group by hour if a specific day is selected
        df = get_data(tab=selected_tab, group_by=group_by, selected_month=selected_month, selected_day=selected_day)

    # Create a Plotly figure based on the selected tab and filters
    fig = go.Figure()

    if selected_day:
        # Plot accumulated data by hour if a specific day is selected (bar chart)
        fig.add_trace(go.Bar(
            x=df['hour'], 
            y=df[selected_tab], 
            name=selected_tab,
            text=df[selected_tab],  # Add data labels
            textposition='auto'  # Automatically position labels (inside or outside bars)
        ))
        fig.update_layout(title=f"Accumulated {selected_tab} for {selected_day} - {selected_month}")
    elif selected_month:
        # Plot accumulated data by day if a month is selected (bar chart)
        fig.add_trace(go.Bar(
            x=df['day'], 
            y=df[selected_tab], 
            name=selected_tab,
            text=df[selected_tab],  # Add data labels
            textposition='auto'  # Automatically position labels (inside or outside bars)
        ))
        fig.update_layout(title=f"Accumulated {selected_tab} for {selected_month}")
    else:
        # Plot raw data (no grouping) (line chart)
        fig.add_trace(go.Scatter(
            x=df['date'], 
            y=df[selected_tab], 
            mode='lines', 
            name=selected_tab,
            text=df[selected_tab],  # Add data labels
            textposition='top center'  # Position data labels at the top center
        ))
        fig.update_layout(title=f"Raw {selected_tab} Data")

    # Update layout for the graph
    fig.update_layout(
        width=1150,
        height=600,
    )
    graph_html = fig.to_html(full_html=False)
    
    # Generate month options
    df_all = get_data(tab='irms')  # Fetch all data to generate month options
    month_options = [{"label": month, "value": month} for month in df_all['month'].unique()]
    
    return render_template('index.html', graph_html=graph_html, month_options=month_options, selected_month=selected_month, selected_day=selected_day, selected_tab=selected_tab)

if __name__ == '__main__':
    app.run(debug=True)
