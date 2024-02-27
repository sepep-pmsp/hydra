from dash import Dash, html, dcc, dash_table, Output, Input, State
from components import (BaseLayout)
from dash_bootstrap_templates import ThemeSwitchAIO
import controller


dbc_css = ("https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates@V1.0.1/dbc.min.css")
external_stylesheets = [ dbc_css, 'https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&display=swap']

layout = BaseLayout()

layout_div = layout.generate_layout()




app = Dash(external_stylesheets=external_stylesheets)



app.layout = layout




if __name__ == '__main__':
    app.run(debug=True)