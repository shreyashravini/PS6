import json

geojson_path = "C:/Users/Shreya Work/OneDrive/Documents/GitHub/student30538/problem_sets/ps6/top_alerts_map/basic-app/Boundaries - Neighborhoods.geojson"
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

# Load the GeoJSON data
geojson_path = "C:/Users/Shreya Work/OneDrive/Documents/GitHub/student30538/problem_sets/ps6/top_alerts_map/basic-app/Boundaries - Neighborhoods.geojson"
with open(geojson_path, 'r') as f:
    chicago_geojson = json.load(f)

# Load the alerts data
file_path = 'C:/Users/Shreya Work/OneDrive/Documents/GitHub/student30538/problem_sets/ps6/top_alerts_map/top_alerts_map.csv'
df = pd.read_csv(file_path)

# Create type-subtype combinations
df['type_subtype'] = df['type'] + ' - ' + df['subtype']

# Get unique combinations
unique_combinations = df['type_subtype'].unique().tolist()

# Create the UI
app_ui = ui.page_fluid(
    ui.h1("Top 10 Alert Locations in Chicago"),
    ui.input_select(
        "type_subtype",
        "Select Alert Type and Subtype",
        choices=unique_combinations
    ),
    ui.output_image("map")  

)

# Define the server function
def server(input, output, session):
    @render.image
    def map():
        selected_type_subtype = input.type_subtype()
        type, subtype = selected_type_subtype.split(' - ')
        filtered_df = df[(df['type'] == type) & (df['subtype'] == subtype)].nlargest(10, 'count')

   
        base_map = alt.Chart(alt.Data(values=chicago_geojson['features'])).mark_geoshape(
            fill='lightgray',
            stroke='white'
        ).properties(
            width=600,
            height=400
        )

        points = alt.Chart(filtered_df).mark_circle().encode(
            longitude='binned_lon:Q',
            latitude='binned_lat:Q',
            size=alt.Size('count:Q', title='Number of Alerts', scale=alt.Scale(range=[100, 1000])),
            color=alt.value('teal'),
            tooltip=['binned_lon', 'binned_lat', 'count']
        )

        final_chart = (base_map + points).properties(
            title=f'Top 10 Locations for {selected_type_subtype} Alerts in Chicago'
        ).project(
            type='mercator',
            scale=80000,
            center=[-87.65, 41.88]  # Approximate center of Chicago
        )
        
        # Save the chart as a PNG file
        image_path = 'chart.png'
        final_chart.save(image_path)

         # Return a dictionary with the 'src' key
        return {'src': image_path, 'contentType': 'image/png'}       

# Create the Shiny app
app = App(app_ui, server)

# Run the app
if __name__ == "__main__":
    print(f"Total type x subtype combinations: {len(unique_combinations)}")
    app.run()