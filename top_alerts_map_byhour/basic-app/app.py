import json

geojson_path = "C:/Users/Shreya Work/OneDrive/Documents/GitHub/student30538/problem_sets/ps6/top_alerts_map_byhour/basic-app/Boundaries - Neighborhoods.geojson"
with open(geojson_path, 'r') as f:
    content = f.read()
    print("File content type:", type(content))
    print("First 500 characters:", content[:500])

try:
    chicago_geojson = json.loads(content)
    print("Successfully parsed JSON")
except json.JSONDecodeError as e:
    print(f"Error parsing JSON: {e}")
    
if isinstance(chicago_geojson, dict):
    print("Keys in chicago_geojson:", chicago_geojson.keys())
elif isinstance(chicago_geojson, list):
    print("Number of items in chicago_geojson:", len(chicago_geojson))
else:
    print("Unexpected type for chicago_geojson:", type(chicago_geojson))
    
from shiny import App, ui, render
import pandas as pd
import altair as alt
import json

# Load the collapsed dataset
df = pd.read_csv('C:/Users/Shreya Work/OneDrive/Documents/GitHub/student30538/problem_sets/ps6/top_alerts_map_byhour/top_alerts_map_byhour.csv')

# Create type-subtype combinations
df['type_subtype'] = df['type'] + ' - ' + df['subtype']
unique_combinations = df['type_subtype'].unique().tolist()

# Get unique hours for the slider
hours = sorted(df['hour'].unique().tolist())

# Load and parse GeoJSON data
geojson_path = "C:/Users/Shreya Work/OneDrive/Documents/GitHub/student30538/problem_sets/ps6/top_alerts_map_byhour/basic-app/Boundaries - Neighborhoods.geojson"
with open(geojson_path, 'r') as f:
    chicago_geojson = json.loads(f.read())

# Create the UI
app_ui = ui.page_fluid(
    ui.h1("Top 10 Alert Locations in Chicago"),
    ui.page_sidebar(
        ui.sidebar(
            ui.input_select(
                "type_subtype",
                "Select Alert Type and Subtype",
                choices=unique_combinations
            ),
            ui.input_slider(
                "hour",
                "Select Hour of Day",
                min=0,
                max=23,
                value=12,
                step=1
            )
        ),
        ui.output_image("map")
    )
)

# Define server logic
def server(input, output, session):
    @render.image
    def map():
        # Get selected values
        selected_type_subtype = input.type_subtype()
        selected_hour = f"{input.hour():02d}:00"
        type, subtype = selected_type_subtype.split(' - ')
        
        # Filter data
        filtered_df = df[
            (df['type'] == type) & 
            (df['subtype'] == subtype) & 
            (df['hour'] == selected_hour)
        ].nlargest(10, 'count')
        
        # Create base map using parsed GeoJSON
        base_map = alt.Chart(alt.Data(values=chicago_geojson['features'])).mark_geoshape(
            fill='lightgray',
            stroke='white'
        ).properties(
            width=600,
            height=400
        )
        
        # Add points
        points = alt.Chart(filtered_df).mark_circle().encode(
            longitude='binned_lon:Q',
            latitude='binned_lat:Q',
            size=alt.Size('count:Q', title='Number of Alerts', scale=alt.Scale(range=[100, 1000])),
            color=alt.value('teal'),
            tooltip=['binned_lon', 'binned_lat', 'count']
        )
        
        # Combine layers
        final_chart = (base_map + points).properties(
            title=f'Top 10 Locations for {selected_type_subtype} Alerts at {selected_hour}'
        ).project(
            type='mercator',
            scale=80000,
            center=[-87.65, 41.88]
        )
        
        # Save and return the chart
        image_path = 'chart.png'
        final_chart.save(image_path)
        return {'src': image_path}

# Create and run the app
app = App(app_ui, server)

if __name__ == "__main__":
    app.run()