from dash.dcc import Loading
from dash.dash_table import DataTable

class Table:
    def get_component(): 
        return Loading(
            DataTable(
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
        )