from shiny import ui, module, Session, render
from data_util import DataModel

#----------------------------------------------------------------
# Loading the DataModel from the data_util module. 
# This helps to separate the data transformation from the ui code.
#----------------------------------------------------------------

dm = DataModel()

#----------------------------------------------------------------
# module.ui decorator allows for separation of ui components into different files.
# using three inputs slider and two multi selectize for filtering the data.
#----------------------------------------------------------------

@module.ui
def data_table_ui():
    container = (
        ui.card(
            ui.card_header(ui.output_text("table_header")),
            ui.layout_sidebar(
                ui.sidebar(
                    ui.input_slider(id="year_table",
                                    min = dm.get_years()[0],
                                    max = dm.get_years()[-1],
                                    value = [dm.get_years()[0], dm.get_years()[-1]],
                                    label="Year Selection:"),
                    ui.input_selectize(id = "columns_table", 
                                    label = "Select Columns",
                                    choices= list(dm.get_data().columns)[2:],
                                    selected = list(dm.get_data().columns)[-7:-5],
                                    multiple = True),
                    ui.input_selectize(id = "countries_table", 
                                    label = "Select Countries",
                                    choices= dm.get_countries(),
                                    selected = dm.get_countries()[:3],
                                    multiple = True),
                    title="Table Filters", 
                    bg="#ffffff"),
                ui.output_data_frame("total_df"), 
            ),
            full_screen= True,
        ),
    )
    return container

#----------------------------------------------------------------
# Building the server for the dataframe functionality.
# This contains the filtering according to the input specified in the ui.
#----------------------------------------------------------------

# module.server is allowing separation of server functionality into different files.
@module.server
def data_table_server(input, output, session: Session):
    
    # Rendering the header that indicated the current selection to the user.
    @output
    @render.text
    def table_header():
        text = f"Showing data for {len(input.columns_table())} type(s) and {len(input.countries_table())} location(s)."
        return text
    
    # Rendering the data frame.
    @render.data_frame  
    def total_df():
        
        # Get the data using the DataModel.
        df = dm.get_data()
        
        # Create Masks for years and coutries.
        year_mask = (df["year"].isin([*range(*input.year_table()),input.year_table()[-1]]))
        country_mask = (df["country"].isin(input.countries_table()))
        
        # Get columns to filter on.
        columns = input.columns_table()
        
        # Applying the filters on the dataset.
        df = df[year_mask & country_mask][["year", "country", *columns]]
        
        # Prettier columns for presenting the data.
        df.columns = df.columns.str.replace('_', ' ').str.title()
        
        # Returning the rendered datatable.
        return render.DataTable(df)
