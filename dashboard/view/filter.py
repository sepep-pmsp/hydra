from dash.dcc import Dropdown
from dash.html import Div, H4, P
from dash_bootstrap_components import RadioItems, Collapse, Button, Card, Input

class Filter:
    FILTER_BUTTON_ID='filtro_botao'
    TYPE_SELECT_ID='filtro_tipo'
    COLUMN_SELECT_ID='filtro_coluna'
    OPERATOR_SELECT_ID='filtro_operacao'
    BASIC_VALUE_TEXT_ID='filtro_basico_valor'
    ADVANCED_VALUE_TEXT_ID='filtro_avancado_valor'
    MESSAGE_TEXT_ID='message'
    ADVANCED_FILTER_COLLAPSE_ID='filtro_avancado_collapse'
    BASIC_FILTER_COLLAPPSE_ID='filtro_basico_collapse'


    @staticmethod
    def componente_filtro(colunas: list[str] = [''], coluna_selecionada: str = None) -> list:
        filtro_tipo = RadioItems(
            ['Básico', 'Avançado'], 'Básico',
            id=Filter.TYPE_SELECT_ID
        )

        coluna_selecionada = coluna_selecionada if coluna_selecionada else colunas[0]
        filtro_coluna = Dropdown(
            colunas, coluna_selecionada,
            id=Filter.COLUMN_SELECT_ID,
            className='form-control'
        )

        filtro_operacao = Dropdown(
            ['<', '<=', '==', '>=', '>', '!='], '>',
            id=Filter.OPERATOR_SELECT_ID,
            className='form-control'
        )

        filtro_basico_valor = Input(
            type='text',
            id=Filter.BASIC_VALUE_TEXT_ID,
            value='0',
            class_name='m-2'
        )

        filtro_basico_collapse = Collapse(
            Div(
                [
                    filtro_coluna,
                    filtro_operacao,
                    filtro_basico_valor
                ],
                className='d-md-flex'
            ),
            id=Filter.BASIC_FILTER_COLLAPPSE_ID,
            is_open=False
        )

        filtro_avancado_valor = Input(
            type='text',
            id=Filter.ADVANCED_VALUE_TEXT_ID,
            value='qtd_domicilios_esgotamento_rio > 0'
        )

        filtro_avancado_collapse = Collapse(
            [
                filtro_avancado_valor
            ],
            id=Filter.ADVANCED_FILTER_COLLAPSE_ID,
            is_open=True
        )

        filtro_botao = Div(
            Button(
                'Filtrar',
                id=Filter.FILTER_BUTTON_ID,
                class_name='m-3'
            ),
            className='d-flex flex-row-reverse'
        )

        message_text = P(
            id=Filter.MESSAGE_TEXT_ID,
            className='mx-auto',
        )

        filtro_titulo = H4(
            "Filtrar setores censitários",
            className="card-title"
        )

        card = Card([
            filtro_titulo,
            filtro_tipo,
            filtro_basico_collapse,
            filtro_avancado_collapse,
            filtro_botao,
            message_text
        ],
            class_name='p-3')

        return card
    
    def get_component():
        filter_component = Div(Filter.componente_filtro(
            [
                'codigo_setor',
                'qtd_domicilios',
                'qtd_domicilios_rede_geral',
                'qtd_domicilios_fossa_rudimentar',
                'qtd_domicilios_esgotamento_rio',
            ],
            coluna_selecionada='qtd_domicilios_esgotamento_rio'
        ), id='componente_filtro')
        return filter_component
