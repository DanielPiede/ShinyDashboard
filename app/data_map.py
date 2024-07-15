from shiny import ui, module, Session, render
from ipyleaflet import Map, GeoJSON, Popup, Choropleth
from shinywidgets import output_widget, render_widget
from ipywidgets import HTML
from data_util import DataModel, CountryModel
from map_util import GeoJTransformer
from branca.colormap import linear

#----------------------------------------------------------------
# Loading the DataModel and CountryModel objects from the data_util module. 
# This helps to separate the data transformation from the ui code.
#----------------------------------------------------------------

dm = DataModel()
cm = CountryModel()

#----------------------------------------------------------------
# Loading the dataset and related information such as parameters for filtering.
#----------------------------------------------------------------

cancer_types = sorted(dm.get_cancer_types())
units = dm.get_units() 
# removed the last year as data was not complete enough for representation on map.
years = dm.get_years()[:-1] 
data_dictionary = dm.get_data_dictionary()
data = dm.get_data()

#----------------------------------------------------------------
# Specifying the map ui, which is integrated into the ui defined in app.py.
#----------------------------------------------------------------

# module.ui decorator allows for separation of ui components into different files.
@module.ui
def map_ui():
    container = ui.card(
        ui.card_header(ui.output_text("map_header")),
        ui.layout_sidebar(
            ui.sidebar(
                ui.input_select(id="year_map", label="Year:", choices=years),
                ui.input_select(
                    id="cancer_type_map", label="Cancer Type:", choices=cancer_types
                ),
                ui.input_select(id="units_map", label="Units:", choices=units),
                title="Map Filters:",
                bg="#ffffff",
            ),
            # map output here:
            output_widget("map"),
        ),
        ui.card_footer(ui.output_text("map_footer")),
        full_screen= True,
        height="75vh",
    )
    return container

#----------------------------------------------------------------
# Server functionality for map only. This is integrated into the main server definition in app.py
#----------------------------------------------------------------

# module.server is allowing separation of server functionality into different files.
@module.server
def map_server(input, output, session: Session):
    
    # Definition of a header as a text output. Lets users see the applied filters in one sentence.
    
    @output
    @render.text
    def map_header():
        text = f"This map is showing the {input.units_map()} for {input.cancer_type_map()} in {input.year_map()}. (Non-clickable countries have no corresponding data)"
        return text

    # Definition of a footer as a text output. Lets useres see additional information about the selected filters id applicable.
    
    @output
    @render.text
    def map_footer():
        if not input.units_map() == "Total Number":
            text = data_dictionary.get(input.cancer_type_map(), "Filters are applied.")
        else:
            text = "Filters are applied."
        return text
    
    # rendering the widget (map) from the ipyleaflet library.
    
    @render_widget
    def map():
        
        # Definition of map canvas and its starting point. Zoom is possible with mousewheel.
        
        m = Map(zoom=3.5, 
                center=(50, 10), 
                scroll_wheel_zoom=True)
        
        # Retrival of geographic data (MultiPolygons) for generation of the geo layer that shows country borders. 
        
        geo_obj = GeoJTransformer()
        geo_data = geo_obj.get_geo_data()
        
        # Definition of the GeoJSON layer. This is the first layer on the map, which outlines the country borders.
        
        geo_json_layer = GeoJSON(
            data=geo_data,
            style={
                "color": "grey",
                "opacity": 1.0,
                "fillOpacity": 0.1,
                "weight": 1,
            },
        )
        
        # Helper function to get the corresponding column for selected filters "Cancer Type" and "Unit".
        # This has been done to avoid duplication of data frames with different column names. Is used for filtering data.
        
        def get_data_column():
            if input.units_map() == "Total Number":
                return str(data.columns[data.columns.str.contains('_n') & data.columns.str.contains(str.lower(input.cancer_type_map().split(' ')[0]))][0])
            else:
                return str(data.columns[data.columns.str.contains('_incidence') & data.columns.str.contains(str.lower(input.cancer_type_map().split(' ')[0]))][0])
        
        col = get_data_column()
        
        # Retrieval of choropleth data. This is another layer on top of the geoJSON layer that is tinted according to the data points for each country.
        # This behaves similar to a heatmap.
        # Data is accepted only as dictionary, therefore utilising dict and zip functions. 
        
        choro_data = geo_obj.get_choro_data()
        data_y = choro_data[(choro_data["year"] == int(input.year_map())) | (choro_data["year"] == 0)]
        choro_filtered = dict(zip(data_y["id"], data_y[col]))        
        
        # Building the choropleth layer:
        choro = Choropleth(
            geo_data=geo_data,
            choro_data=choro_filtered, 
            colormap=linear.Purples_04,
            border_color='black',
            hover_style={"fillColor": "#45B08C", "dashArray": "0", "fillOpacity": 0.5},
            style={'fillOpacity': 0.7, 'dashArray': '5, 5'})
        
        
        # On-Click Event Handler: This is an event handler that takes the callback as an input.
        # It allows users to click on highlighted countries and spawns a popup window at the countries centroid. 
        
        def on_click(event, feature, **kwargs):
            # Get country name from the callback information (feature). 
            country_name = feature["properties"]["name"]
            
            # Get country position using the in CountryModel object implemented get_centroid method.
            pos = cm.get_centroid(country_name)
            
            # Mask for dataframe to filter data on year and country.
            mask = (data["year"] == int(input.year_map())) & (data["country"] == country_name)
            
            # creating the content for the pop-up as HTML content. 
            pop_html = HTML()
            pop_html.value = f"""
                <h5>{country_name}</h5>
                <p>The {str.lower(str(input.units_map()))} for {str.lower(str(input.cancer_type_map()))} was <b>{data[mask][col].values[0]}</b> in {country_name}.</p>
                """
            # Create the pop_up, position based on the centroid information in CountryModel
            popup = Popup(
                location = pos,
                child = pop_html,
                keep_in_view = True,
                auto_close = True,
            )

            # Add the popup to the map.
            m.add(popup)
        
        
        m.add_layer(geo_json_layer) # Add first layer (geoJSON)
        m.add_layer(choro) # Add second layer (choropleth)
        choro.on_click(on_click) # Add event listener & handler (on click) with popup specified in on_click function.
        
        # Finally, return the map.
        return m
