from dash import Dash, html, dcc, dash_table, Output, Input, State
from components import (ThemeSwitch, Map, NavBar)
from dash_bootstrap_templates import ThemeSwitchAIO



dbc_css = ("https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates@V1.0.1/dbc.min.css")
tyle_layer_theme1 = 'https://tiles.stadiamaps.com/tiles/alidade_smooth/{z}/{x}/{y}{r}.png'
tyle_layer_theme2 = 'https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/{z}/{x}/{y}{r}.png'


navbar_constructor = NavBar()
navbar_div = navbar_constructor.pipeline()

theme_switch_constructor = ThemeSwitch()
theme_switch_div = theme_switch_constructor.pipeline()

map_constructor = Map()
map_div = map_constructor.pipeline()


app = Dash(external_stylesheets=[dbc_css])


app.layout = html.Div([theme_switch_div, map_div,navbar_div])

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


if __name__ == '__main__':
    app.run(debug=True)