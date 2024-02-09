from typing import Any
import dash_bootstrap_components as dbc
from dash import html, dcc

class NavBar:

    def __init__(self) -> None:
        self.class_names = 'navbar_div'
        self.brand = html.Img(src='../assets/images/logo_hydra.png', height= '90', width= '110')
        self.brand_href = "#"
        self.color = 'dark'
        
        
    def generate_filter_column_select(self, colunas: list[str] = [''], coluna_selecionada: str = None)-> dcc.Dropdown:
        coluna_selecionada = coluna_selecionada if coluna_selecionada else colunas[0]
        filtro_coluna = dcc.Dropdown(
                colunas, coluna_selecionada,
                id='filtro_coluna',
                className='filtro_selecionar_coluna form-control btn btn-primary'
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
        
        filter_operation = dcc.Dropdown(
                ['<', '<=', '==', '>=', '>', '!='], active_operation,
                id='filtro_operacao',
                className='filtro_operacao form-control  btn btn-primary'
            )
        
        return filter_operation
    
    def generate_filter_value(self):
        filtro_basico_valor = dbc.Input(
        type='text',
        id='filtro_basico_valor',
        value='0',
        class_name='filtro_valor form-control'
        )
        
        return filtro_basico_valor
            
        

    def generate_navbar(self, filter_type, filter_operation,filter_columns, filtro_basico_valor) -> html.Div :
        navbar = dbc.NavbarSimple(
            children=[
            
            html.Div([filter_columns,
            filter_operation,
            filtro_basico_valor,], className='filter'),
            
            dbc.NavItem(dbc.Button("Filtrar", href="#", id='filtro_botao')),
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
        dark=True,
        style={'padding': '0!important'}
    )
        
        navbar_div = html.Div(children=[navbar], className=self.class_names)

        return navbar_div
    
    def pipeline(self) -> html.Div:
        filter_type_component = self.generate_filter_type()
        filter_operation_component = self.generate_filter_operation()
        filter_columns_component = self.generate_filter_column_select(['Indicador Número 1', 'Indicador Número 2', 'Indicador Número 3', 'Indicador Número 4'])
        filter_basic_value = self.generate_filter_value()
        
        navbar_div = self.generate_navbar(filter_type_component,filter_operation_component,filter_columns_component, filter_basic_value)

        return navbar_div
    
    def __call__(self) -> Any:
        
        return self.pipeline()