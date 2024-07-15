from shiny import ui, module, reactive, Session, render
from shinywidgets import output_widget, register_widget
from data_util import DataModel
import pandas as pd

dm = DataModel()

@module.ui
def data_table_ui():
    container = (
        ui.card(
            ui.card_header("Placeholder 3"),
            ui.layout_sidebar(
                ui.sidebar(
                    ui.input_slider(id="year_table",
                                    min = dm.get_years()[0],
                                    max = dm.get_years()[-1],
                                    value = [dm.get_years()[0], dm.get_years()[-1]],
                                    label="Year Selection:"),
                    ui.input_selectize(id = "types_table", 
                                    label = "Select Columns",
                                    choices= list(dm.get_data().columns)[2:],
                                    multiple = True),
                    ui.input_selectize(id = "countries_table", 
                                    label = "Select Countries",
                                    choices= dm.get_countries(),
                                    multiple = True),
                    title="Table Filters", 
                    bg="#ffffff"),
                ui.output_data_frame("total_df")
            ),
            full_screen= True,
        ),
    )
    return container


@module.server
def data_table_server(input, output, session: Session):
    @render.data_frame  
    def total_df():
        df = dm.get_data()
        return render.DataTable(df)
