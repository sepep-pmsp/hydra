from typing import Any
import dash_bootstrap_components as dbc
from dash import html
import dash_daq as daq


PLACEHOLDER_TEXT = ("Minim officia enim ipsum elit cillum dolore. Cillum dolor officia "
            "consequat ullamco aute elit ex est magna magna eiusmod ad. Non qui amet "
            "pariatur laboris amet cillum amet aute ipsum in nostrud minim. Sint dolor "
            "duis eu veniam sit do aute in tempor id ex velit. Consequat eiusmod nulla "
            "ex qui elit quis elit laborum non ipsum nisi in tempor. Aliquip id laborum "
            "excepteur laborum cupidatat non consectetur consectetur mollit ut labore ea.")

INITIAL_CARD_ID = "inital_card_div"
TEXT_TITLE = "Instruções básicas"
CLASS_NAMES = {"inital_card" : "initial_card p-5 text-white bg-dark rounded-3 ",
                            "initial_card_div" : "initial_card_div",}   

class initialCardFactory:
   
    
    
    def __init__(self, card_id:str=INITIAL_CARD_ID, placeholder_text:str=PLACEHOLDER_TEXT, placeholder_text_title=TEXT_TITLE, class_names = CLASS_NAMES):
       
        self.initial_card_id = card_id
        self.placeholder_text = placeholder_text
        self.placeholder_text_title = placeholder_text_title
        self.class_names = class_names
    
    def __create_initial_card(self, initial_card_id:str=None, placeholder_text:str=None, placeholder_text_title:str=None, class_names:dict=None) -> dbc.Card:
        class_names = class_names or self.class_names
        
        initial_card_id = initial_card_id or self.initial_card_id
        placeholder_text = placeholder_text or self.placeholder_text
        placeholder_text_title = placeholder_text_title or self.placeholder_text_title
        
        card_body = dbc.CardBody(
        [
            html.H3(placeholder_text_title),
            html.P(placeholder_text),

        ],
        
    )
        card_footer = dbc.CardFooter(dbc.Button("Documentação", color="primary"))
        
        initial_card = dbc.Card([card_body,card_footer], 
                                class_name=class_names.get("initial_card_div"),
                                id=initial_card_id)
        
        
        return initial_card

    def __call__(self, initial_card_id:str=None, 
                 placeholder_text:str=None, 
                 placeholder_text_title:str=None,
                 class_names:dict=None)->dbc.Card:
        
        return self.__create_initial_card(initial_card_id, placeholder_text, placeholder_text_title,class_names)
    
    
