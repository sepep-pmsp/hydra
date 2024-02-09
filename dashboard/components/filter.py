from typing import Any
from dash import html, dcc
import dash_bootstrap_components as dbc

class BasicFilter:
    
    def __init__(self, 
                 columns: list[str] = ['Indicador Número 1', 'Indicador Número 2', 'Indicador Número 3', 'Indicador Número 4'], 
                 selected_columns: str = None, 
                 active_operation:str = ">") -> None:
        
        self.active_operation = active_operation
        self.columns = columns              
        self.selected_columns = selected_columns
        
        self.type_filter_options = ['Básico', 'Avançado']
        self.filter_operation_option = ['<', '<=', '==', '>=', '>', '!=']
        
        self.class_names = {
            'filter_column_select' : 'filtro_selecionar_coluna form-control btn btn-primary',
            'filter_type_select' : 'filtros_tipo_div',
            'filter_operation_select' : 'filtro_operacao form-control  btn btn-primary',
            'filter_basic_value' : 'filtro_valor form-control',
            'filter_div' : 'filter' 
            }

        self.ids = {
            'filter_column_select' : 'filtro_coluna',
            'filter_operation_select' : 'filtro_operacao',
            'filter_type_select' : 'filtros_tipo',
            'filter_basic_value' : 'filtro_basico_valor'
            

        }
    
    def generate_filter_column_select(self)-> dcc.Dropdown:
        selected_columns = self.selected_columns if self.selected_columns else self.columns[0]
        filter_column = dcc.Dropdown(
                    self.columns, selected_columns,
                    className= self.class_names.get('filter_column_select'),
                    id= self.ids.get('filter_column_select')
                )
        return filter_column
    
    def generate_filter_operation(self,)-> dbc.DropdownMenu:
        
        filter_operation = dcc.Dropdown(
                self.filter_operation_option, self.active_operation,
                id=self.ids.get('filter_operation_select'),
                className=self.class_names.get('filter_operation_select')
            )
        
        return filter_operation
    
    def generate_filter_value(self) -> dbc.Input:
        filter_basic_value = dbc.Input(
        type='text',
        value='0',
        id=self.ids.get('filter_basic_value'),
        className=self.class_names.get('filter_basic_value')
        )
        
        return filter_basic_value
    
    
    def generate_filter_type(self)->dbc.RadioItems:
        
        filter_type = dbc.RadioItems(
        self.type_filter_options, 'Básico',
        id=self.ids.get('filter_type_select'),
        class_name=self.class_names.get('filter_type_select')
    )
        return filter_type
    
    
    def generate_dropdown_filtering_options(self,filter_type) -> dbc.DropdownMenu:
        dropdown = dbc.DropdownMenu(
                children=[
                    dbc.DropdownMenuItem("Como filtrar?", header=True),
                    filter_type
                ],
                nav=True,
                in_navbar=True,
                label="Filtros",)
        
        return dropdown
        
        
    
    
    def generate_filter_div(self,column_select,filter_operation_select,filter_value) -> html.Div:
        return html.Div([column_select,
                        filter_operation_select,
                        filter_value,], className=self.class_names.get('filter_div'))
        
        
    
 
        
    def pipeline(self):
        
        column_select = self.generate_filter_column_select()
        filter_operation_select = self.generate_filter_operation()
        filter_value = self.generate_filter_value()
        
        filter_type_select = self.generate_filter_type()
        
        filter_type_dropdown = self.generate_dropdown_filtering_options(filter_type_select) 
        
        filter_div = self.generate_filter_div(column_select,filter_operation_select,filter_value)
        
        
        return [filter_div, filter_type_dropdown]
        
    def __call__(self) -> Any:
        
        return self.pipeline()