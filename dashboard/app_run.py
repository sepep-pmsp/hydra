from dash import Dash, html
from components import (ThemeSwitch, Map)


dbc_css = ("https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates@V1.0.1/dbc.min.css")
tyle_layer_theme1 = 'https://tiles.stadiamaps.com/tiles/alidade_smooth/{z}/{x}/{y}{r}.png'
tyle_layer_theme2 = 'https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/{z}/{x}/{y}{r}.png'

theme_switch_constructor = ThemeSwitch()
theme_switch_div = theme_switch_constructor.pipeline()
map_constructor = Map()
map_div = map_constructor.pipeline()


app = Dash(external_stylesheets=[dbc_css])


app.layout = html.Div([theme_switch_div, map_div])

if __name__ == '__main__':
    app.run(debug=True)