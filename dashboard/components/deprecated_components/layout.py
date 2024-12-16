from dash.html import Div, Span

from dashboard.components.deprecated_components.details_card import DetailsCard
from dashboard.components.deprecated_components.filter import Filter
from dashboard.components.deprecated_components.map import Map
from dashboard.components.deprecated_components.table import Table

class Layout:
    INITIAL_LOAD_SPAN_ID='initial_load_span'

    @staticmethod
    def get_layout():
        return Div([
        # Span para detectar o carregamento inicial da página
        Span(id=Layout.INITIAL_LOAD_SPAN_ID, style={'display': 'none'}),
        # Mapa no painel esquerdo
        Map.get_component(),
        # Filtro e detalhes no painel direito
        Div([
            Filter.get_component(),
            Table.get_component(),
            DetailsCard.get_component(),
        ],
            id="info_panel",
            className='p-3'),
    ],
        id="wrapper",
        className='m-3'
    )