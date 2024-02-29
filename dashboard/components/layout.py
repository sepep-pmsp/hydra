from typing import Any
from components import (ThemeSwitch, Map, NavBar, LayersOffCanvas, Tab)

from dash import html


class BaseLayout:
    INITIAL_LOAD_SPAN_ID = 'initial_load_span'
    
    def __init__(self) -> None:
        
        self.ThemeSwitch = ThemeSwitch()
        self.Map = Map()
        self.NavBar = NavBar()
        self.LayerOffCanvas = LayersOffCanvas()
        self.Tab = Tab()
                
        
    def generate_layout(self) -> html.Div:
        
        theme_switch_div = self.ThemeSwitch()
        map_div = self.Map()
        navbar_div = self.NavBar()
        layer_off_canvas_div = self.LayerOffCanvas()[0]
        tab_div = self.Tab()
        load_div = html.Span(id=BaseLayout.INITIAL_LOAD_SPAN_ID, style={'display': 'none'})
        
        
        layout = html.Div([load_div, theme_switch_div, map_div,navbar_div,layer_off_canvas_div, tab_div])
        
        
        return layout
    
    
    @staticmethod
    def get_style_sheets():
        dbc_css = ("https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates@V1.0.1/dbc.min.css")
        external_stylesheets = [ dbc_css, 'https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&display=swap']
        
        return external_stylesheets
    
        
        
    def pipeline(self) -> html.Div:
        
        layout = self.generate_layout()
        
        return layout
    
    def __call__(self):
        return self.pipeline