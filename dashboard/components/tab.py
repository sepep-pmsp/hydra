from typing import Any
import dash_bootstrap_components as dbc
from dash import html
from .initial_card import initialCardFactory
from .table import Table
from.details_card import DetailsCard




class Tab:
    MESSAGE_TEXT_ID='message'
    DOWNLOAD_CSV_BUTTON_ID= 'csv-button'


    def __init__(self) -> None:
        

        
        self.class_names = {"tab" : " tab",
                            "tab_div" : "tab_div",
                            "":"",
                            "":"",
                            "" : ""}
        
        create_initial_card = initialCardFactory()
        self.initial_card = create_initial_card()

        self.table = Table.get_component()
        
        
        
        
        
        self.ids = {"": "",
                    "":""}
        
                
        
            
        

    def generate_tabs_content(self) -> Any :
        first_tab = self.initial_card
        
        second_tab = dbc.Card([dbc.CardBody(self.table),dbc.CardFooter(dbc.Button("Download CSV", id=Tab.DOWNLOAD_CSV_BUTTON_ID, n_clicks=0))])
        
        third_tab = dbc.Card([dbc.CardBody([DetailsCard.get_component(), dbc.CardFooter(html.P(
        id=Tab.MESSAGE_TEXT_ID,
        className='mx-auto',
    ))])])
        
        
        tab_content = [first_tab,second_tab,third_tab]
        
        return tab_content
        
        
    def generate_tab(self, tab_content) -> dbc.Tabs:
        
        tabs = dbc.Tabs(
    [
        dbc.Tab(tab_content[0], label="Detalhes do uso"),
        dbc.Tab(tab_content[1], label="Dados do filtro"),
        dbc.Tab(tab_content[2], label="Dados do Setor"),
    ],
    class_name= self.class_names.get("tab") ,
)
          
        return tabs
        
            
    
    def pipeline(self) -> Any:

        tab_content = self.generate_tabs_content()
        tab = self.generate_tab(tab_content)
        
        return html.Div(tab, className=self.class_names.get("tab_div"))
    
    def __call__(self) -> Any:
        
        return self.pipeline()