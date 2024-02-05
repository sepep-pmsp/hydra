from dash import Dash, html
from components import ThemeSwitch

dbc_css = ("https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates@V1.0.1/dbc.min.css")

theme_switch_constructor = ThemeSwitch()
theme_switch_div = theme_switch_constructor.pipeline()


app = Dash(external_stylesheets=[dbc_css])


app.layout = html.Div([theme_switch_div])

if __name__ == '__main__':
    app.run(debug=True)