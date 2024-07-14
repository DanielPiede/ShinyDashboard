from shiny import App, Inputs, Outputs, Session, render, ui, reactive
import map, plot, data_table
import shinyswatch


# Defining the header for the dashboard UI.
header = ui.panel_title(title="OECD Cancer Statistics Dashboard: Incidence Rates, Screening Coverage, and Key Numbers")

# Defining the body for the dashboard UI. Each of the three components is defined as a module for readability.
body = ui.navset_pill(
    ui.nav_panel(
        "OECD Map",
        ui.tags.p(),
        map.map_ui("map"),
    ),
    ui.nav_panel(
        "Incidence vs. Screening",
        ui.tags.p(),
        plot.plot_ui("plot"),
    ),
    ui.nav_panel(
        "Data Table",
        ui.tags.p(),
        data_table.data_table_ui("data_table"),
    )
)

app_ui = ui.page_fluid(
    shinyswatch.theme.minty, 
    header, 
    body,
    )


def server(input: Inputs, output: Outputs, session: Session):
    map.map_server("map")


app = App(app_ui, server)
