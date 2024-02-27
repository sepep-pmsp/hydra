from typing import Any
from dash import html, dcc
import dash_bootstrap_components as dbc

class BasicFilter:
    TYPE_SELECT_ID='filtros_tipo'
    COLUMN_SELECT_ID='filtro_coluna'
    OPERATOR_SELECT_ID='filtro_operacao'
    BASIC_VALUE_TEXT_ID='filtro_basico_valor'
    ADVANCED_VALUE_TEXT_ID='filtro_avancado_valor'
    ADVANCED_FILTER_COLLAPSE_ID='filtro_avancado_collapse'
    BASIC_FILTER_COLLAPPSE_ID='filtro_basico_collapse'




    
    def __init__(self, 
                 columns: list[str] = [""], 
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
            'filter_column_select' : BasicFilter.COLUMN_SELECT_ID,
            'filter_operation_select' : BasicFilter.OPERATOR_SELECT_ID,
            'filter_type_select' : BasicFilter.TYPE_SELECT_ID,
            'filter_basic_value' : BasicFilter.BASIC_VALUE_TEXT_ID,
            'filter_advanced_value' : BasicFilter.ADVANCED_VALUE_TEXT_ID,
            'advanced_filter_collapse' : BasicFilter.ADVANCED_FILTER_COLLAPSE_ID,
            'basic_filter_collapse' : BasicFilter.BASIC_FILTER_COLLAPPSE_ID
            

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
    
    def generate_basic_filter_collapse(self,filter_column,filter_operation,filter_basic_value):
        return dbc.Collapse(
            html.Div(
                [
                    filter_column,
                    filter_operation,
                    filter_basic_value
                ],
                className='d-md-flex'
            ),
            id=self.ids.get("basic_filter_collapse"),
            is_open=False
        )
    
    
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
    
    def generate_advanced_filter(self):
        return dbc.Input(
            type='text',
            id=self.ids.get('filter_advanced_value'),
            value='qtd_domicilios_esgotamento_rio > 0'
        )
        
    def generate_advanced_filter_collapse(self,advanced_filter):
        return dbc.Collapse(
            [
                advanced_filter
            ],
            id=self.ids.get('advanced_filter_collapse'),
            is_open=True
        )
        
    
    
    def generate_filter_div(self,advanced_filter_collapse,basic_filter_collapse) -> html.Div:
        return html.Div([advanced_filter_collapse,
                        basic_filter_collapse], 
                        className=self.class_names.get('filter_div'))
        
        
    
 
        
    def pipeline(self):
        
        column_select = self.generate_filter_column_select()
        filter_operation_select = self.generate_filter_operation()
        filter_value = self.generate_filter_value()
        
        advanced_filter = self.generate_advanced_filter()
        
        filter_type_select = self.generate_filter_type()
        
        filter_type_dropdown = self.generate_dropdown_filtering_options(filter_type_select) 
        
        filter_basic_collapse = self.generate_basic_filter_collapse(column_select,filter_operation_select,filter_value)
        filter_advanced_collapse = self.generate_advanced_filter_collapse(advanced_filter)
        
        filter_div = self.generate_filter_div(filter_basic_collapse,filter_advanced_collapse)
        
        
        return [filter_div, filter_type_dropdown]
        
    def __call__(self) -> Any:
        
        return self.pipeline()