from typing import Any
import dash_bootstrap_components as dbc
from dash import html
from .initial_card import initialCard




class Tab:

    def __init__(self) -> None:
        

        
        self.class_names = {"tab" : " tab",
                            "" : "",
                            "":"",
                            "":"",
                            "" : ""}
        
        self.initial_card_constructor = initialCard()
        self.initial_card = self.initial_card_constructor()
        
        
        self.ids = {"": "",
                    "":""}
        
                
        
            
        

    def generate_tabs_content(self) -> Any :
        first_tab = self.initial_card
        
        second_tab = dbc.Card(
            dbc.CardBody(
                [
                    html.P("This is tab 2!", className="card-text"),
                    dbc.Button("Click here", color="success"),
                ]
            ),
            className="mt-3",
        )
        
        
        tab_content = [first_tab,second_tab]
        
        return tab_content
        
        
    def generate_tab(self, tab_content) -> dbc.Tabs:
        
        tabs = dbc.Tabs(
    [
        dbc.Tab(tab_content[0], label="Detalhes do setor"),
        dbc.Tab(tab_content[1], label="Dados do filtro"),
    ],
    class_name= self.class_names.get("tab") ,
)
          
        return tabs
        
            
    
    def pipeline(self) -> Any:

        tab_content = self.generate_tabs_content()
        print(tab_content)
        tab = self.generate_tab(tab_content)
        
        return tab
    
    def __call__(self) -> Any:
        
        return self.pipeline()