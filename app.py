from shiny import App, Inputs, Outputs, Session, render, ui
import shinyswatch

header = ui.navset_bar(
                    ui.nav_spacer(),
                    ui.nav_menu(title="Resources", align="right"),
                    title = 'Overview',
        )

body = ui.layout_columns(
    ui.card(
        ui.card_header("Disease Selection"),
        ui.p("Enter"),
        ui.input_slider("slider", None, 0,10,0)
    ),
    ui.card(
        ui.card_header("Time Selection"),
        ui.p("Enter"),
        ui.input_slider("slider2", None, 0,10,0)
    ),
        ui.card(
        ui.card_header("Location Selection"),
        ui.p("Enter"),
        ui.input_slider("slider3", None, 0,10,0)
    )
)

footer = None

app_ui = ui.page_fluid(
    shinyswatch.theme.minty,
    header,
    body,
    footer
)


def server(input: Inputs, output: Outputs, session: Session):
    @output
    @render.text
    def slider_val():
        return f"{input.num()}"


app = App(app_ui, server)