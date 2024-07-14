from shiny import ui, module, Session, render
from ipyleaflet import Map, GeoJSON, Popup
from shinywidgets import output_widget, render_widget
from ipywidgets import HTML
from data_model import DataModel, CountryModel
import json
import urllib.request


# Loading data with the DataModel and CountryModel classes.
dm = DataModel()
cm = CountryModel()

cancer_types = sorted(dm.get_cancer_types())
units = sorted(dm.get_units())
years = sorted(dm.get_years())
data_dictionary = dm.get_data_dictionary()

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
            output_widget("map"),
        ),
        ui.card_footer(ui.output_text("map_footer")),
        full_screen= True,
        height="75vh",
    )
    return container

@module.server
def map_server(input, output, session: Session):
    @output
    @render.text
    def map_header():
        text = f"This map is showing the {input.units_map()} for {input.cancer_type_map()} in {input.year_map()}."
        return text

    @output
    @render.text
    def map_footer():
        if not input.units_map() == "Total Number":
            text = data_dictionary.get(input.cancer_type_map(), "Filters are applied.")
        else:
            text = "Filters are applied."
        return text    
    
    @render_widget
    def map():
        m = Map(zoom=3.5, 
                center=(50, 10), 
                scroll_wheel_zoom=True)
        
        with urllib.request.urlopen("https://raw.githubusercontent.com/DanielPiede/ShinyDashboard/main/raw/countries.geojson") as url:
            geo = json.load(url)
        
        geo_json_layer = GeoJSON(
            data=geo,
            style={
                "color": "grey",
                "opacity": 1.0,
                "fillOpacity": 0.5,
                "weight": 1,
            },
            hover_style={"color": "blue", "dashArray": "0", "fillOpacity": 0.5},
        )
        
        def on_click(event, feature, **kwargs):
            country_name = feature["properties"]["name"]
            pos = cm.get_centroid(country_name)
            pop_html = HTML()
            pop_html.value = f"""
                <h6>{country_name}</h6>
                <p></p>
                """
            current_popup = Popup(
                location = pos,
                child = pop_html,
                keep_in_view = True,
                auto_close = True,
                
            )
            m.add(current_popup)
        
        geo_json_layer.on_click(on_click)
        m.add_layer(geo_json_layer)
        return m
