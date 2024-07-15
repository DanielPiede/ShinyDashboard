from shiny import App, Inputs, Outputs, Session, ui
import data_map
import data_table
import shinyswatch

#----------------------------------------------------------------
# Header for the User Interface Shell (Using HTML tags)
#----------------------------------------------------------------

header = ui.panel_title(
    ui.div(
        ui.p(),
        ui.h3("OECD Cancer Statistics Dashboard:"),
        ui.h5("Incidence Rates and Number of Cases"),
        ui.hr(),
        ),
)

#----------------------------------------------------------------
# Defining the body which will contain the Map and the DataFrame. 
# Both components are defined as a module for better readability.
#----------------------------------------------------------------

body = ui.navset_card_pill(
    ui.nav_panel(
        "Interactive Map",
        ui.tags.p(),
        data_map.map_ui("map"),
    ),
    ui.nav_panel(
        "Data Table",
        ui.tags.p(),
        data_table.data_table_ui("data_table"),
    )
)

#----------------------------------------------------------------
# Building the app_ui using a theme and the header and body.
#----------------------------------------------------------------


app_ui = ui.page_fluid(
    shinyswatch.theme.minty, 
    header, 
    body,
    )

#----------------------------------------------------------------
# Building the server, which constits of two server modules.
# One for each functionality, map and dataframe.
#----------------------------------------------------------------

def server(input: Inputs, output: Outputs, session: Session):
    data_map.map_server("map")
    data_table.data_table_server("data_table")

################################
# Create the App Instance:

app = App(app_ui, server)
