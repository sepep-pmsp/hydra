from typing import Any
from components import (ThemeSwitch, Map, NavBar, LayersOffCanvas, Tab)

from dash import html


class BaseLayout:
    INITIAL_LOAD_SPAN_ID = 'initial_load_span'
    
    def __init__(self) -> None:
        
        self. ThemeSwitch = ThemeSwitch()
        self. Map = Map()
        self. NavBar = NavBar()
        self. LayerOffCanvas = LayersOffCanvas()
        self. Tab = Tab()
        
        
    def generate_layout(self) -> html.Div:
        
        theme_switch_div = self. ThemeSwitch()
        map_div = self. Map()
        navbar_div = self. NavBar()
        layer_off_canvas_div = self. LayerOffCanvas()
        tab_div = self. Tab()
        
        
        html.Div([html.Span(id=BaseLayout.INITIAL_LOAD_SPAN_ID, style={'display': 'none'}),theme_switch_div, map_div,navbar_div,layer_off_canvas_div, tab_div])
        
        
    @staticmethod    
    def pipeline(self) -> html.Div:
        
        layout = self.generate_layout()
        
        return layout
    
    def __call__(self) -> html.Div:
        return self. pipeline