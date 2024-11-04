import dash
from dash import dcc, html, Input, Output
import folium
import pandas as pd
import base64

# Sample data for SpaceX launches
launch_data = [
    {'name': 'Cape Canaveral', 'location': [28.3922, -80.6077], 'launches': 50, 'success_rate': 0.92},
    {'name': 'Kennedy Space Center', 'location': [28.5721, -80.6480], 'launches': 45, 'success_rate': 0.95},
    {'name': 'Vandenberg Space Force Base', 'location': [34.7322, -120.6105], 'launches': 20, 'success_rate': 0.85}
]

# Convert launch data to DataFrame for easier manipulation
df = pd.DataFrame(launch_data)

# Create a Folium map
def create_map():
    map_center = [28.5721, -80.6480]  # Center of Florida
    map_ = folium.Map(location=map_center, zoom_start=6)

    # Add markers and circles to the map
    for launch in launch_data:
        folium.Marker(
            location=launch['location'],
            popup=folium.Popup(f"{launch['name']}<br>Launches: {launch['launches']}<br>Success Rate: {launch['success_rate'] * 100}%", 
                               parse_html=True),
            icon=folium.Icon(color='blue')
        ).add_to(map_)

        folium.Circle(
            location=launch['location'],
            radius=50000,  # Radius in meters
            color='blue',
            fill=True,
            fill_opacity=0.1,
            popup=f"{launch['name']} Launch Area"
        ).add_to(map_)

    return map_

# Initialize the Dash app
app = dash.Dash(__name__)

# App layout
app.layout = html.Div([
    html.H1("SpaceX Launch Dashboard", style={'text-align': 'center'}),
    
    # Dropdown for selecting launch site
    html.Div([
        html.Label("Select Launch Site:"),
        dcc.Dropdown(
            id='site-dropdown',
            options=[{'label': site['name'], 'value': site['name']} for site in launch_data],
            value='Cape Canaveral',  # Default value
            clearable=False,
            style={'width': '50%', 'margin': 'auto'}
        )
    ], style={'margin': '20px'}),
    
    # Display the Folium map
    html.Iframe(id='map', srcDoc=create_map().get_root().render(), style={'width': '100%', 'height': '600px'}),
    
    # Additional information display
    html.Div(id='info-display', style={'text-align': 'center', 'margin-top': '20px'}),
    
    # Graphs for launches and success rates
    dcc.Graph(id='launches-graph'),
    dcc.Graph(id='success-rate-graph')
])

# Callback to update information and graphs based on dropdown selection
@app.callback(
    Output('info-display', 'children'),
    Output('launches-graph', 'figure'),
    Output('success-rate-graph', 'figure'),
    Input('site-dropdown', 'value')
)
def update_info(selected_site):
    # Find the selected site's data
    site_data = df[df['name'] == selected_site].iloc[0]

    # Display info
    info = f"{site_data['name']} - Launches: {site_data['launches']}, Success Rate: {site_data['success_rate'] * 100}%"

    # Create bar graph for launches
    launches_fig = {
        'data': [
            {'x': df['name'], 'y': df['launches'], 'type': 'bar', 'name': 'Launches'},
        ],
        'layout': {
            'title': 'Total Launches by Site',
            'xaxis': {'title': 'Launch Site'},
            'yaxis': {'title': 'Number of Launches'}
        }
    }

    # Create bar graph for success rate
    success_rate_fig = {
        'data': [
            {'x': df['name'], 'y': df['success_rate'] * 100, 'type': 'bar', 'name': 'Success Rate'},
        ],
        'layout': {
            'title': 'Success Rate by Site (%)',
            'xaxis': {'title': 'Launch Site'},
            'yaxis': {'title': 'Success Rate (%)'}
        }
    }

    return info, launches_fig, success_rate_fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
