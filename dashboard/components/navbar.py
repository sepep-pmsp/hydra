from typing import Any
import dash_bootstrap_components as dbc
from dash import html, dcc

from .filter import BasicFilter
from .layers_offcanvas import LayersOffCanvas

class NavBar:

    def __init__(self) -> None:
        
        self.offcanvas_constructor = LayersOffCanvas()
        self.offcanvas_button = self.offcanvas_constructor()[1]
        
        self.filter_constructor = BasicFilter()
        
        self.filter = self.filter_constructor()
        
        self.class_names = 'navbar_div'
        self.brand = html.Img(src='../assets/images/logo_hydra.png', height= '90', width= '100')
        self.brand_href = "#"
        self.color = 'dark'
        self.style ={'padding': '0!important'}
                
        
            
        

    def generate_navbar(self) -> html.Div :
        navbar = dbc.NavbarSimple(
            children=[
            self.filter[0],
            self.filter[1],
            dbc.NavItem(dbc.Button("Filtrar", href="#", id='filtro_botao')),
            
            self.offcanvas_button
        ],
            
        brand=self.brand,
        brand_href=self.brand_href,
        color=self.color, 
        dark=True,
        style= self.style
    )
        
        navbar_div = html.Div(children=[navbar], className=self.class_names)

        return navbar_div
    
    def pipeline(self) -> html.Div:

        navbar_div = self.generate_navbar()

        return navbar_div
    
    def __call__(self) -> Any:
        
        return self.pipeline()