from dash.dcc import Loading
from dash.html import(
    H2,
    H3,
    Div,
)
from dash_bootstrap_components import (
    Label,
    Input,
    Card
)

class DetailsCard:
    COMPONENT_ID='card_detalhes'

    @staticmethod
    def componente_detalhes_setor(codigo_setor, qtd_domicilios, qtd_domicilios_rede_geral, qtd_domicilios_fossa_rudimentar, qtd_domicilios_esgotamento_rio):
        titulo = H2(
            f'Detalhes do setor {str(codigo_setor)}'
        )

        campos_dict = {
            'Domicílios particulares permanentes: ': qtd_domicilios,
            'Domicílios particulares permanentes com banheiro de uso exclusivo dos moradores ou sanitário e esgotamento sanitário via rede geral de esgoto ou pluvial: ': qtd_domicilios_rede_geral,
            'Domicílios particulares permanentes com banheiro de uso exclusivo dos moradores ou sanitário e esgotamento sanitário via fossa rudimentar: ': qtd_domicilios_fossa_rudimentar,
            'Domicílios particulares permanentes, com banheiro de uso exclusivo dos moradores ou sanitário e esgotamento sanitário via rio, lago ou mar: ': qtd_domicilios_esgotamento_rio
        }

        campos = [
            Div([
                Label(label),
                Input(value=value, type='text', readonly='readonly'),
            ], className='d-flex') for label, value in campos_dict.items()
        ]

        campos.insert(0, titulo)

        return Div(campos, id='detalhes_setor_')

    @staticmethod
    def componente_detalhes_distrito(nm_distrito_municipal):
        titulo = H3('Distrito', id='distrito_title',
                            className='layer_title')


        input = Input(value=nm_distrito_municipal,
                            type='text', readonly='readonly')

        return Div([
            Div(
                [
                    titulo,                ],
                id='distrito_header'
            ),
            input
        ], id='distrito_wrapper'
        )
    
    @staticmethod
    def card_detalhes_children(
            codigo_setor='',
            qtd_domicilios='',
            qtd_domicilios_rede_geral='',
            qtd_domicilios_fossa_rudimentar='',
            qtd_domicilios_esgotamento_rio='',
            nm_distrito_municipal=''
            ):
        children = [
            DetailsCard.componente_detalhes_setor(
            codigo_setor,
            qtd_domicilios,
            qtd_domicilios_rede_geral,
            qtd_domicilios_fossa_rudimentar,
            qtd_domicilios_esgotamento_rio
            ),
            DetailsCard.componente_detalhes_distrito(nm_distrito_municipal)
        ]
        return children
    
    @staticmethod
    def get_component():
        return Loading(
            Card(
                DetailsCard.card_detalhes_children(),
                id=DetailsCard.COMPONENT_ID,
                className='p-3'
            )
        )