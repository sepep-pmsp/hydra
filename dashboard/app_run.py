from dash import Dash, html, dcc, dash_table, Output, Input, State
from components import (ThemeSwitch, Map, NavBar, LayersOffCanvas, initialCard, Tab)
from dash_bootstrap_templates import ThemeSwitchAIO



dbc_css = ("https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates@V1.0.1/dbc.min.css")
tyle_layer_theme1 = 'https://tiles.stadiamaps.com/tiles/alidade_smooth/{z}/{x}/{y}{r}.png'
tyle_layer_theme2 = 'https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/{z}/{x}/{y}{r}.png'

external_stylesheets = [ dbc_css, 'https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&display=swap']

tab_constructor = Tab()
tab_div = tab_constructor()

offcanvas_constructor = LayersOffCanvas()
offcanvas_div = offcanvas_constructor.pipeline()[0]

navbar_constructor = NavBar()
navbar_div = navbar_constructor.pipeline()

theme_switch_constructor = ThemeSwitch()
theme_switch_div = theme_switch_constructor.pipeline()

map_constructor = Map()
map_div = map_constructor.pipeline()


app = Dash(external_stylesheets=external_stylesheets)


app.layout = html.Div([theme_switch_div, map_div,navbar_div,offcanvas_div, tab_div])

@app.callback(
    Output('map', 'children'),
    Input('theme-store', 'data'),
    prevent_initial_call=True
)
def update_tile_layer(theme):
    tyle_layer = tyle_layer_theme1 if theme else tyle_layer_theme2
    url = tyle_layer
    attribution = '&copy; <a href="https://stadiamaps.com/">Stadia Maps</a> '

    return map_constructor.generate_map_children(url, attribution)

@app.callback(
    Output('theme-store', 'data'),
    Input(ThemeSwitchAIO.ids.switch("theme"), 'value'),
    prevent_initial_call=True
)
def update_theme(theme_value):
    
    return theme_value

@app.callback(
    Output("offcanvas-placement", "is_open"),
    Input("open-offcanvas-placement", "n_clicks"),
    [State("offcanvas-placement", "is_open")],
)
def toggle_offcanvas(n1, is_open):
    if n1:
        return not is_open
    return is_open



if __name__ == '__main__':
    app.run(debug=True)