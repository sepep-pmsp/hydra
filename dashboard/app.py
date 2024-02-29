from dash import Dash
from components import (BaseLayout)

import controller




layout = BaseLayout()
def servir_layout():
    return layout()


app = Dash(external_stylesheets=BaseLayout.get_style_sheets())
app.layout = servir_layout()
