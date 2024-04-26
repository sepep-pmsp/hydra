from typing import Any
import dash_bootstrap_components as dbc
from dash import html
import dash_daq as daq


PLACEHOLDER_TEXT = """
Aqui você pode consultar tanto os dados básicos dos setores censitários do Censo de 2010, quanto as informações calculadas a partir dos dados georreferenciados obtidos do Geosampa.

No modo básico, basta selecionar a coluna a ser pesquisada, o operador e o valor de comparação.

No modo avançado, você pode escrever suas próprias consultas, incluindo a realização de cálculos matemáticos com cada coluna. Por exemplo, caso queira pesquisar os setores censitários onde mais de 60% dos domicílios possuam ligação à rede geral de esgotamento, pode utilizar a busca "qtd_domicilios_rede_geral/qtd_domicilios > 0.6".

A aba "Dados do filtro" exibe todos os setores censitários que atendem ao filtro desejado. Ao clicar em um dos setores na tabela, ele é destacado no mapa e seus dados são exibidos na aba "Dados do Setor".

Ao clicar em um dos setores no mapa, ele é destacado no mapa e seus dados também são exibidos na aba "Dados do Setor".
"""

TEXT_TITLE = "Instruções básicas"
CLASS_NAMES = {"inital_card" : "initial_card p-5 text-white bg-dark rounded-3 ",
                            "initial_card_div" : "initial_card_div",}   

class initialCardFactory:
    
    INITIAL_CARD_ID = "inital_card_div"

    
    
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
            html.H3(placeholder_text_title)
        ] + [
            html.P(t) for t in placeholder_text.split("\n")
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
    
    
