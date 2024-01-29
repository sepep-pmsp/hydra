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
from utils import gdf_to_geobuf

if __name__ == '__main__':

    def setor_overlay_children(setor_geobuf: str) -> dl.Pane:
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

    def map_children(setor_children: dl.Pane, dist_geobuf: str, distrito_toggle: bool):
        base = [dl.BaseLayer(
            dl.TileLayer(),
            name='Base',
            checked=True
        )]
        overlay = []
        zindex = 401
        if dist_geobuf:
            overlay.append(
                dl.Overlay(dl.Pane(dl.GeoJSON(data=dist_geobuf, id="distritos", format='geobuf',
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
                           checked=distrito_toggle
                           )
            )
            zindex += 1

        if setor_children:
            overlay.append(
                dl.Overlay(children=[setor_children],
                           id="setores_ol",
                           name='setores_ol',
                           checked=True
                           )
            )
        else:
            overlay.append(
                dl.Overlay(children=[],
                           id="setores_ol",
                           name='setores_ol',
                           checked=True
                           )
            )

        return [
            dl.LayersControl(
                base + overlay,
                id='layers-control'
            ),
        ]

    def componente_filtro(colunas: list[str] = [''], coluna_selecionada:str=None) -> list:
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
        
        
    @app.callback(
            Output('detalhes_setor', 'children', allow_duplicate=True),
            Input('dados_setores', 'active_cell'),
            prevent_initial_call='initial_duplicate'
    )
    def load_details_from_table(active_cell):
        if active_cell:
            print(active_cell)
            return str(active_cell) if active_cell else "Click the table"
        
    @app.callback(
            Output('detalhes_setor', 'children', allow_duplicate=True),
            Input('setores', 'click_feature'),
            prevent_initial_call='initial_duplicate'
    )
    def load_details_from_map(feature):
        if feature:
            print(feature['properties'])
            return str(feature['properties']) if feature else "Click the table"

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

        cols = [{'id': col, 'name': col} for col in setor_df.columns if col != 'id']

        return setor_overlay_children(setor_geobuf), msg, dados_setor, cols

    def init_data():
        data = filter_setores(
            n_clicks=0,
            filtro_tipo='Básico',
            filtro_coluna='qtd_domicilios_esgotamento_rio',
            filtro_operacao='>',
            filtro_valor='0'
        )

        return data

    app.layout = html.Div([
        # Mapa no painel esquerdo
        dcc.Loading(
            dl.Map(center=[-23.5475, -46.6375],
                zoom=10,
                children=map_children(None, None, False), id="map")
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
                    page_current= 0,
                    page_size= 10,
                )
            ),
            dcc.Loading(
                html.Div(
                    [html.P(
                        id='detalhes_setor'
                    ),
                    html.Div([
                        html.H2('Distrito', id='distrito_header',
                                className='layer_header'),
                        daq.BooleanSwitch(
                            id='distrito_toggle',
                            label="Exibir no mapa",
                            on=False,
                            className='layer_toggle',
                        )
                    ], id='distrito_wrapper'
                    )]
                )
            ),
        ],
            id="info_panel",
            className='p-3'),
    ],
        id="wrapper",
        className='m-3'
    )

    app.run_server(debug=True, port=7777)
