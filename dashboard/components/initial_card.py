from typing import Any
import dash_bootstrap_components as dbc
from dash import html
import dash_daq as daq




class initialCard:

    def __init__(self) -> None:
        

        
        self.class_names = {"inital_card" : "initial_card p-5 text-white bg-dark rounded-3 ",
                            "" : "",
                            "":"",
                            "":"",
                            "" : ""}
        
        
        self.ids = {"inital_card_div": "inital_card_div",
                    "":""}
        
        self.placeholder_text_title = "Instruções básicas"
        self.placeholder_text = "Minim officia enim ipsum elit cillum dolore. Cillum dolor officia consequat ullamco aute elit ex est magna magna eiusmod ad. Non qui amet pariatur laboris amet cillum amet aute ipsum in nostrud minim. Sint dolor duis eu veniam sit do aute in tempor id ex velit. Consequat eiusmod nulla ex qui elit quis elit laborum non ipsum nisi in tempor. Aliquip id laborum excepteur laborum cupidatat non consectetur consectetur mollit ut labore ea."
                
        
            
        

    def generate_initial_card(self) -> dbc.Card :
        card = dbc.CardBody(
        [
            html.H3(self.placeholder_text_title),
            html.P(self.placeholder_text),

        ],
        
    )
        
        return dbc.Card([card,dbc.CardFooter(dbc.Button("Documentação", color="primary"))], id=self.ids.get("inital_card_div"), )
        
            
    
    def pipeline(self) -> Any:

        card = self.generate_initial_card()
        
        return card
    
    def __call__(self) -> Any:
        
        return self.pipeline()