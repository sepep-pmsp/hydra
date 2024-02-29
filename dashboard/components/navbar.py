from typing import Any
import dash_bootstrap_components as dbc
from dash import html, dcc

from .filter import BasicFilter
from .layers_offcanvas import LayersOffCanvas

class NavBar:
    FILTER_BUTTON_ID='filtro_botao'


    def __init__(self) -> None:
        
        self.offcanvas_constructor = LayersOffCanvas()
        self.offcanvas_button = self.offcanvas_constructor()[1]
        
        self.filter_constructor = BasicFilter(columns= [
                'codigo_setor',
                'qtd_domicilios',
                'qtd_domicilios_rede_geral',
                'qtd_domicilios_fossa_rudimentar',
                'qtd_domicilios_esgotamento_rio',
            ],
            selected_columns='qtd_domicilios_esgotamento_rio'
        )
        
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
            dbc.NavItem(dbc.Button("Filtrar", href="#", id=NavBar.FILTER_BUTTON_ID)),
            
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