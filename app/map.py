from shiny import ui, module, Session, render
from ipyleaflet import Map, GeoJSON, Popup, Choropleth
from shinywidgets import output_widget, render_widget
from ipywidgets import HTML
from data_util import DataModel, CountryModel
from map_util import GeoJTransformer
from branca.colormap import linear

# Loading data with the DataModel and CountryModel classes.
dm = DataModel()
cm = CountryModel()

cancer_types = sorted(dm.get_cancer_types())
units = dm.get_units()
years = dm.get_years()[:-1] # removed the last year as data was not complete enough for representation on map.
data_dictionary = dm.get_data_dictionary()
data = dm.get_data()

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
        text = f"This map is showing the {input.units_map()} for {input.cancer_type_map()} in {input.year_map()}. (Non-clickable countries have no corresponding data)"
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
        
        geo_obj = GeoJTransformer()
        geo_data = geo_obj.get_geo_data()
        
        geo_json_layer = GeoJSON(
            data=geo_data,
            style={
                "color": "grey",
                "opacity": 1.0,
                "fillOpacity": 0.1,
                "weight": 1,
            },
        )
        
        def get_data_column():
            if input.units_map() == "Total Number":
                return str(data.columns[data.columns.str.contains('_n') & data.columns.str.contains(str.lower(input.cancer_type_map().split(' ')[0]))][0])
            else:
                return str(data.columns[data.columns.str.contains('_incidence') & data.columns.str.contains(str.lower(input.cancer_type_map().split(' ')[0]))][0])
        
        col = get_data_column()
        choro_data = geo_obj.get_choro_data()
        data_y = choro_data[(choro_data["year"] == int(input.year_map())) | (choro_data["year"] == 0)]
        choro_filtered = dict(zip(data_y["id"], data_y[col]))        
        
        choro = Choropleth(
            geo_data=geo_data,
            choro_data=choro_filtered, 
            colormap=linear.Purples_04,
            border_color='black',
            hover_style={"fillColor": "#45B08C", "dashArray": "0", "fillOpacity": 0.5},
            style={'fillOpacity': 0.7, 'dashArray': '5, 5'})
        
        def on_click(event, feature, **kwargs):
            country_name = feature["properties"]["name"]
            pos = cm.get_centroid(country_name)
            mask = (data["year"] == int(input.year_map())) & (data["country"] == country_name)
            pop_html = HTML()
            pop_html.value = f"""
                <h5>{country_name}</h5>
                <p>The {str.lower(str(input.units_map()))} for {str.lower(str(input.cancer_type_map()))} was <b>{data[mask][col].values[0]}</b> in {country_name}.</p>
                """
            current_popup = Popup(
                location = pos,
                child = pop_html,
                keep_in_view = True,
                auto_close = True,
            )

            m.add(current_popup)
        
        
        m.add_layer(geo_json_layer)
        m.add_layer(choro)
        choro.on_click(on_click)
        
        return m
