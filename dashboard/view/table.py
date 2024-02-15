from dash.dcc import Loading
from dash.dash_table import DataTable
from dash_ag_grid import AgGrid

class Table:
    columnDefs = [
        {'field': 'codigo_setor'},
        {'field': 'qtd_domicilios'},
        {'field': 'qtd_domicilios_rede_geral'},
        {'field': 'qtd_domicilios_fossa_rudimentar'},
        {'field': 'qtd_domicilios_esgotamento_rio'},
    ]

    @staticmethod
    def get_columns(columns:list[str], table_type:str='AgGrid'):
        cols = []

        if table_type == 'DataTable':
            cols = [{'id': col, 'name': col}
                    for col in columns if col != 'id']
        if table_type == 'AgGrid':
            cols = [{'field': col}
                    for col in columns if col != 'id']

        return cols

    @staticmethod
    def data_table_component():
        return DataTable(
                id='dados_setores',
                page_action="native",
                page_current=0,
                page_size=10,
                style_header={
                    'fontFamily': 'var(--bs-body-font-family)',
                    'fontSize': 'var(--bs-body-font-size)',
                    'fontWeight': 'var(--bs-body-font-weight)',
                    'lineHeight': 'var(--bs-body-line-height)'
                }
            )
    
    @staticmethod
    def ag_grid_component():
        return AgGrid(
            id='dados_setores',
            dashGridOptions={
                'pagination':True,
                'rowSelection': 'single'},
        )

    @staticmethod
    def get_component():
        return Loading(
            Table.ag_grid_component()
        )