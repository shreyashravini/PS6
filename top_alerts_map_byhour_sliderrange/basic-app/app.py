from shiny import App, ui, render
import pandas as pd
import altair as alt
import json

# Load the hourly data
df = pd.read_csv('C:/Users/Shreya Work/OneDrive/Documents/GitHub/student30538/problem_sets/ps6/top_alerts_map_byhour_sliderrange/basic-app/top_alerts_map_byhour.csv')

# Create type-subtype combinations
df['type_subtype'] = df['type'] + ' - ' + df['subtype']
unique_combinations = df['type_subtype'].unique().tolist()

# Load GeoJSON data
geojson_path = 'C:/Users/Shreya Work/OneDrive/Documents/GitHub/student30538/problem_sets/ps6/top_alerts_map_byhour_sliderrange/basic-app/Boundaries - Neighborhoods.geojson'
with open(geojson_path, 'r') as f:
    chicago_geojson = json.load(f)

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
            ui.input_switch(
                "switch_button",
                "Toggle to switch to range of hours",
                value=False
            ),
            ui.panel_conditional(
                "input.switch_button",  # When switch is ON
                ui.input_slider(
                    "hour_range",
                    "Select Hour Range",
                    min=0,
                    max=23,
                    value=[6, 9]
                )
            ),
            ui.panel_conditional(
                "!input.switch_button",  # When switch is OFF
                ui.input_slider(
                    "single_hour",
                    "Select Single Hour",
                    min=0,
                    max=23,
                    value=6
                )
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
        type, subtype = selected_type_subtype.split(' - ')
        
        if input.switch_button():
            # Range mode
            hour_start = input.hour_range()[0]
            hour_end = input.hour_range()[1]
            hours = [f"{h:02d}:00" for h in range(hour_start, hour_end + 1)]
            title_time = f"between {hour_start:02d}:00-{hour_end:02d}:00"
        else:
            # Single hour mode
            hour = input.single_hour()
            hours = [f"{hour:02d}:00"]
            title_time = f"at {hour:02d}:00"
        
        # Filter data
        filtered_df = df[
            (df['type'] == type) & 
            (df['subtype'] == subtype) & 
            (df['hour'].isin(hours))
        ].groupby(['binned_lat', 'binned_lon'])['count'].sum().reset_index()
        
        top_10_locations = filtered_df.nlargest(10, 'count')
        
        # Create base map
        base_map = alt.Chart(alt.Data(values=chicago_geojson['features'])).mark_geoshape(
            fill='lightgray',
            stroke='white'
        ).properties(
            width=600,
            height=400
        )
        
        # Add points
        points = alt.Chart(top_10_locations).mark_circle().encode(
            longitude='binned_lon:Q',
            latitude='binned_lat:Q',
            size=alt.Size('count:Q', title='Number of Alerts', scale=alt.Scale(range=[100, 1000])),
            color=alt.value('teal'),
            tooltip=['binned_lon', 'binned_lat', 'count']
        )
        
        # Combine layers
        final_chart = (base_map + points).properties(
            title=f'Top 10 Locations for {selected_type_subtype} Alerts {title_time}'
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