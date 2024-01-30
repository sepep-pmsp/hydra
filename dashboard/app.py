import dash_leaflet as dl
import dash_leaflet.express as dlx
import dash_daq as daq
from dash import Dash, html, dcc, dash_table, Output, Input, State
from dash_extensions.javascript import arrow_function
import dash_bootstrap_components as dbc
import geopandas as gpd
import pandas as pd
from dotenv import load_dotenv
import os
import json

from dao import DuckDBDAO
from etls import (
    DistritoTransformer,
    SetoresTransformer,
)
from utils import gdf_to_geobuf, load_s3_vars
from services import MunicipioService

dao = DuckDBDAO(**load_s3_vars())

def setores_overlay_children(setor_geobuf: str) -> dl.Pane:
    pane = dl.Pane(dl.GeoJSON(data=setor_geobuf, id="setores", format='geobuf',
                                                    hideout=dict(
                                                        selected=[]),
                                                    options={
                                                        "style": {
                                                            'color': 'rgba(0,0,0,0)',
                                                            'fillColor': 'red',
                                                            'fillOpacity': 0.8
                                                        }},
                                                    hoverStyle=arrow_function(
                                                        dict(weight=5, color='red', dashArray='', fillOpacity=0.5)),
                                                    zoomToBounds=True),
                    name='setores_pane',
                    style={'zIndex': 420}
                    )
    return pane

def setor_detalhes_overlay_children(setor_geobuf: str) -> dl.Pane:
    pane = dl.Pane(dl.GeoJSON(data=setor_geobuf, id="setor_detalhes", format='geobuf',
                                                    hideout=dict(
                                                        selected=[]),
                                                    options={
                                                        "style": {
                                                            'color': 'red',
                                                            'fillColor': '#ffa7a1',
                                                            'fillOpacity': 1
                                                        }},
                                                    hoverStyle=arrow_function(
                                                        dict(weight=5, dashArray=''))),
                    name='setor_detalhes_pane',
                    style={'zIndex': 421}
                    )
    return pane

def load_limite_municipal(dao:DuckDBDAO) -> str:
    ms = MunicipioService(dao)
    
    return ms.get_geobuf()

def limite_municipal_children(limite_municipal_geobuf:str) -> dl.GeoJSON:
    geojson = dl.GeoJSON(data=limite_municipal_geobuf, id="limite_municipal", format='geobuf',
                                        options={
                                            "style": {'color': '#949494',
                                                    'fillColor': '#c0c0c0',
                                                    'fillOpacity': 0.5}},
                                        )
    return geojson

def map_children(dao:DuckDBDAO):
    base = [dl.BaseLayer(
        dl.TileLayer(),
        name='Base',
        checked=True
    )]
    overlay = []
    zindex = 401
    overlay.append(
        dl.Overlay(dl.Pane(children=[],
                    id='limite_municipal_pane',
                    name='limite_municipal_pane',
                    # O z-index padrão do overlay pane é 400 e o próximo pane (shadow) é 500,
                    # portanto os valores personalizados devem estar entre 400 e 500
                    style={'zIndex': zindex}
                    ),
                    id='limite_municipal_ol',
                    name='limite_municipal_ol',
                    checked=True
            )
    )
    zindex += 1
    overlay.append(
        dl.Overlay(dl.Pane(dl.GeoJSON(id="distritos", format='geobuf',
                                        options={
                                            "style": {'color': 'rgba(0,0,0,0)',
                                                    'fillColor': 'green',
                                                    'fillOpacity': 0.8}},
                                        hoverStyle=arrow_function(
                                            dict(weight=5, color='#666', dashArray=''))
                                        ),
                            name='distritos_pane',
                            # O z-index padrão do overlay pane é 400 e o próximo pane (shadow) é 500,
                            # portanto os valores personalizados devem estar entre 400 e 500
                            style={'zIndex': zindex}
                            ),
                    id='distritos_ol',
                    name='distritos_ol',
                    checked=False
                    )
    )
    zindex += 1

    overlay.append(
        dl.Overlay(children=[],
                    id="setores_ol",
                    name='setores_ol',
                    checked=True
                    )
    )

    overlay.append(
        dl.Overlay(children=[],
                    id="setor_detalhes_ol",
                    name='setor_detalhes_ol',
                    checked=True
                    )
    )

    return [
        dl.LayersControl(
            base + overlay,
            id='layers-control'
        ),
    ]

def componente_filtro(colunas: list[str] = [''], coluna_selecionada: str = None) -> list:
    filtro_tipo = dbc.RadioItems(
        ['Básico', 'Avançado'], 'Básico',
        id='filtro_tipo'
    )

    coluna_selecionada = coluna_selecionada if coluna_selecionada else colunas[0]
    filtro_coluna = dcc.Dropdown(
        colunas, coluna_selecionada,
        id='filtro_coluna',
        className='form-control'
    )

    filtro_operacao = dcc.Dropdown(
        ['<', '<=', '==', '>=', '>', '!='], '>',
        id='filtro_operacao',
        className='form-control'
    )

    filtro_basico_valor = dbc.Input(
        type='text',
        id='filtro_basico_valor',
        value='0',
        class_name='m-2'
    )

    filtro_basico_collapse = dbc.Collapse(
        html.Div(
            [
                filtro_coluna,
                filtro_operacao,
                filtro_basico_valor
            ],
            className='d-md-flex'
        ),
        id='filtro_basico_collapse',
        is_open=False
    )

    filtro_avancado_valor = dbc.Input(
        type='text',
        id='filtro_avancado_valor',
        value='qtd_domicilios_esgotamento_rio > 0'
    )

    filtro_avancado_collapse = dbc.Collapse(
        [
            filtro_avancado_valor
        ],
        id='filtro_avancado_collapse',
        is_open=True
    )

    filtro_botao = html.Div(
        dbc.Button(
            'Filtrar',
            id='filtro_botao',
            class_name='m-3'
        ),
        className='d-flex flex-row-reverse'
    )

    message_text = html.P(
        id='message',
        className='mx-auto',
    )

    filtro_titulo = html.H4(
        "Filtrar setores censitários",
        className="card-title"
    )

    card = dbc.Card([
        filtro_titulo,
        filtro_tipo,
        filtro_basico_collapse,
        filtro_avancado_collapse,
        filtro_botao,
        message_text
    ],
        class_name='p-3')

    return card

def componente_detalhes_setor(codigo_setor, qtd_domicilios, qtd_domicilios_rede_geral, qtd_domicilios_fossa_rudimentar, qtd_domicilios_esgotamento_rio):
    titulo = html.H2(
        f'Detalhes do setor {str(codigo_setor)}'
    )

    campos_dict = {
        'Domicílios particulares permanentes: ': qtd_domicilios,
        'Domicílios particulares permanentes com banheiro de uso exclusivo dos moradores ou sanitário e esgotamento sanitário via rede geral de esgoto ou pluvial: ': qtd_domicilios_rede_geral,
        'Domicílios particulares permanentes com banheiro de uso exclusivo dos moradores ou sanitário e esgotamento sanitário via fossa rudimentar: ': qtd_domicilios_fossa_rudimentar,
        'Domicílios particulares permanentes, com banheiro de uso exclusivo dos moradores ou sanitário e esgotamento sanitário via rio, lago ou mar: ': qtd_domicilios_esgotamento_rio
    }

    campos = [
        html.Div([
            dbc.Label(label),
            dbc.Input(value=value, type='text', readonly='readonly'),
        ], className='d-flex') for label, value in campos_dict.items()
    ]

    campos.insert(0, titulo)

    return html.Div(campos, id='detalhes_setor_')

def componente_detalhes_distrito(nm_distrito_municipal):
    titulo = html.H3('Distrito', id='distrito_title',
                        className='layer_title')

    botao = daq.BooleanSwitch(
        id='distrito_toggle',
        label="Exibir no mapa",
        on=False,
        className='layer_toggle',
    )

    input = dbc.Input(value=nm_distrito_municipal,
                        type='text', readonly='readonly')

    return html.Div([
        html.Div(
            [
                titulo,
                botao,
            ],
            id='distrito_header'
        ),
        input
    ], id='distrito_wrapper'
    )

def card_detalhes_children(
        codigo_setor='',
        qtd_domicilios='',
        qtd_domicilios_rede_geral='',
        qtd_domicilios_fossa_rudimentar='',
        qtd_domicilios_esgotamento_rio='',
        nm_distrito_municipal=''
        ):
    children = [
        componente_detalhes_setor(
        codigo_setor,
        qtd_domicilios,
        qtd_domicilios_rede_geral,
        qtd_domicilios_fossa_rudimentar,
        qtd_domicilios_esgotamento_rio
        ),
        componente_detalhes_distrito(nm_distrito_municipal)
    ]
    return children

# Create example app.
app = Dash(external_stylesheets=[dbc.themes.MATERIA])

# @app.callback(
#     Output('distritos_ol', 'checked'),
#     Input('distrito_toggle', 'on')
# )
# def update_checked_layers(value):
#     return value

@app.callback(
    Output('filtro_avancado_collapse', 'is_open'),
    Output('filtro_basico_collapse', 'is_open'),
    Input('filtro_tipo', 'value')
)
def selecionar_filtro(filtro_tipo_value: str) -> (bool, bool):
    if filtro_tipo_value == 'Básico':
        return False, True
    if filtro_tipo_value == 'Avançado':
        return True, False

def carregar_detalhes_setor(codigo_setor:str):
    setores = SetoresTransformer(filtro_personalizado=f'codigo_setor == {codigo_setor}')
    gdf = setores()
    df = pd.DataFrame(gdf.drop(columns=['geometry','tooltip']))
    df = df.iloc[0]
    setor = df.to_dict()
    setor_geobuf = gdf_to_geobuf(gdf) 
    return card_detalhes_children(**setor), setor_detalhes_overlay_children(setor_geobuf)

@app.callback(
    Output('card_detalhes', 'children', allow_duplicate=True),
    Output('setor_detalhes_ol', 'children', allow_duplicate=True),
    Input('dados_setores', 'active_cell'),
    prevent_initial_call='initial_duplicate'
)
def load_details_from_table(active_cell):
    if active_cell:
        print(active_cell)
        return carregar_detalhes_setor(active_cell['row_id'])
    return None, None

@app.callback(
    Output('card_detalhes', 'children', allow_duplicate=True),
    Output('setor_detalhes_ol', 'children', allow_duplicate=True),
    Input('setores', 'click_feature'),
    prevent_initial_call='initial_duplicate'
)
def load_details_from_map(feature):
    if feature:
        print(feature['properties'])
        return carregar_detalhes_setor(feature['properties']['codigo_setor'])
    return None, None

@app.callback(
    Output('setores_ol', 'children'),
    Output('message', 'children'),
    Output('dados_setores', 'data'),
    Output('dados_setores', 'columns'),
    Input('filtro_botao', 'n_clicks'),
    State('filtro_tipo', 'value'),
    State('filtro_coluna', 'value'),
    State('filtro_operacao', 'value'),
    State('filtro_basico_valor', 'value'),
    State('filtro_avancado_valor', 'value'),
)
def filter_setores(basico_n_clicks, filtro_tipo, filtro_coluna, filtro_operacao, filtro_basico_valor, filtro_avancado_valor):
    print('Filtrando setores...')
    if not (filtro_basico_valor or filtro_avancado_valor):
        setores = SetoresTransformer()
    else:
        if filtro_tipo == 'Avançado':
            filtro = filtro_avancado_valor
        elif filtro_tipo == 'Básico':
            filtro = f'{filtro_coluna} {filtro_operacao} {filtro_basico_valor}'

        setores = SetoresTransformer(
            filtro_personalizado=filtro)

    setor_gdf = setores()
    setor_geobuf = gdf_to_geobuf(setor_gdf)

    coluna_options = [
        col.split(' ')[-1] for col in setores.colunas_selecionadas
    ]

    msg = f"{setor_gdf.shape[0]} setores censitários encontrados com o filtro {filtro}!"
    print(msg)
    print('Retornando setores...')
    setor_gdf = setor_gdf.drop(columns=['geometry', 'tooltip'])
    setor_df = pd.DataFrame(setor_gdf)
    setor_df['id'] = setor_df['codigo_setor']
    dados_setor = setor_df.to_dict('records')

    cols = [{'id': col, 'name': col}
            for col in setor_df.columns if col != 'id']

    return setores_overlay_children(setor_geobuf), msg, dados_setor, cols

@app.callback(
    Output('limite_municipal_pane', 'children'),
    Input('initial_load_span', 'children')
)
def initial_load(children):
    print('initial_load_span children updated')
    geobuf = load_limite_municipal(dao)
    return limite_municipal_children(geobuf)

app.layout = html.Div([
    # Span para detectar o carregamento inicial da página
    html.Span(id='initial_load_span', style={'display': 'none'}),
    # Mapa no painel esquerdo
    dcc.Loading(
        dl.Map(center=[-23.5475, -46.6375],
                zoom=10,
                children=map_children(dao),
                id="map",
                className='p-3')
    ),
    # Filtro e detalhes no painel direito
    html.Div([
        html.Div(componente_filtro(
            [
                'codigo_setor',
                'qtd_domicilios',
                'qtd_domicilios_rede_geral',
                'qtd_domicilios_fossa_rudimentar',
                'qtd_domicilios_esgotamento_rio',
            ],
            coluna_selecionada='qtd_domicilios_esgotamento_rio'
        ), id='componente_filtro'),
        dcc.Loading(
            dash_table.DataTable(
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
        ),
        dcc.Loading(
            dbc.Card(
                card_detalhes_children(),
                id='card_detalhes',
                className='p-3'
            )
        ),
    ],
        id="info_panel",
        className='p-3'),
],
    id="wrapper",
    className='m-3'
)

if __name__ == '__main__':
    app.run_server(debug=True, port=7777)
