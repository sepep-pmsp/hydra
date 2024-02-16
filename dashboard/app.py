from dash import Dash
import dash_bootstrap_components as dbc

from view import Layout
import controller

# Create example app.
app = Dash(external_stylesheets=[dbc.themes.MATERIA])

app.layout = Layout.get_layout()

server = app.server

if __name__ == '__main__':
    app.run_server(debug=True, port=7777)
