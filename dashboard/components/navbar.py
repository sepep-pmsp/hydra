from typing import Any
import dash_bootstrap_components as dbc
from dash import html, dcc

class NavBar:

    def __init__(self) -> None:
        self.class_names = 'navbar_div'
        self.brand = "Hydra"
        self.brand_href = "#"
        self.color = 'dark'
        
        
    def generate_filter_column_select(self, colunas: list[str] = [''], coluna_selecionada: str = None)-> dbc.DropdownMenu:
        coluna_selecionada = coluna_selecionada if coluna_selecionada else colunas[0]
        opcoes_de_colunas = []
        
        for coluna in colunas:
                opcoes_de_colunas.append(dbc.DropdownMenuItem(coluna))
        
        opcoes_de_colunas.append(dbc.DropdownMenuItem(coluna_selecionada, active=True))
                
        filtro_coluna = dbc.DropdownMenu(children=[*opcoes_de_colunas],
        id='filtro_coluna',
        className='filtro_selecionar_coluna'
    )
        return filtro_coluna
        
        
    def generate_filter_type(self)->dbc.RadioItems:
        
        filter_type = dbc.RadioItems(
        ['Básico', 'Avançado'], 'Básico',
        id='filtro_tipo',
        class_name='filtros_tipo_div'
    )
        return filter_type
    
    def generate_filter_operation(self,active_operation:str = ">")-> dbc.DropdownMenu:
        
        filter_operation = dbc.DropdownMenu([
            dbc.DropdownMenuItem("<"),
            dbc.DropdownMenuItem("<="),
            dbc.DropdownMenuItem('!='),
            dbc.DropdownMenuItem("==", ),
            dbc.DropdownMenuItem(">=",),
            dbc.DropdownMenuItem(">", ),
            dbc.DropdownMenuItem('>', active=True),
            dbc.DropdownMenuItem(divider=True),

            html.P(
                "Selecione o operador desejado para filtrar.",
                className="text-muted px-4 mt-4",
            ),
        ],
        label=active_operation,
        id= 'filtro_operacao',
        class_name='filtro_operacao',
        in_navbar=True,
        )
        
        return filter_operation
            
        

    def generate_navbar(self, filter_type, filter_operation,filter_columns) -> html.Div :
        navbar = dbc.NavbarSimple(
            children=[
            filter_columns,
            filter_operation,
            dbc.NavItem(dbc.NavLink("Page 1", href="#")),
            dbc.DropdownMenu(
                children=[
                    dbc.DropdownMenuItem("Como filtrar?", header=True),
                    filter_type
                ],
                nav=True,
                in_navbar=True,
                label="Filtros",),
        ],
        brand=self.brand,
        brand_href=self.brand_href,
        color=self.color, 
        dark=True
    )
        
        navbar_div = html.Div(children=[navbar], className=self.class_names)

        return navbar_div
    
    def pipeline(self) -> html.Div:
        filter_type_component = self.generate_filter_type()
        filter_operation_component = self.generate_filter_operation()
        filter_columns_component = self.generate_filter_column_select(['indicador Número 1', 'indicador Número 2'])
        
        navbar_div = self.generate_navbar(filter_type_component,filter_operation_component,filter_columns_component)

        return navbar_div
    
    def __call__(self) -> Any:
        
        return self.pipeline()