from shiny import ui, module, reactive, Session, render
from shinywidgets import output_widget, register_widget
from data_model import DataModel


@module.ui
def data_table_ui():
    container = (
        ui.card(
            ui.card_header("Placeholder 3"),
            ui.layout_sidebar(
                ui.sidebar("Sidebar", bg="#ffffff"),
                "Card content",
            ),
        ),
    )
    return container


@module.server
def data_table_server(input, output, session: Session):
    pass
