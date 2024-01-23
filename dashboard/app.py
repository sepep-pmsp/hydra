import dash_leaflet as dl
import dash_leaflet.express as dlx
import dash_daq as daq
from dash import Dash, html, dcc, Output, Input, State
from dash_extensions.javascript import arrow_function
import geopandas as gpd
from dotenv import load_dotenv
import os
import json

from dao import DuckDBDAO
from etls import (
    DistritoTransformer,
    SetoresTransformer,
)

if __name__ == '__main__':

    load_dotenv('../.env')

    AWS_S3_BUCKET = os.getenv("MINIO_SILVER_BUCKET_NAME")
    AWS_ACCESS_KEY_ID = os.getenv("MINIO_ROOT_USER")
    AWS_SECRET_ACCESS_KEY = os.getenv("MINIO_ROOT_PASSWORD")
    ENDPOINT_OVERRIDE = os.getenv("MINIO_ENDPOINT_URL")

    duckdb_dao = DuckDBDAO(
        bucket_name=AWS_S3_BUCKET,
        access_key=AWS_ACCESS_KEY_ID,
        secret_key=AWS_SECRET_ACCESS_KEY,
        endpoint=ENDPOINT_OVERRIDE
    )

    def setor_overlay_children(setor_geobuf:str) -> dl.Pane:
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

    def map_children(setor_children:dl.Pane, dist_geobuf: str, distrito_toggle: bool):
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
        return [
            dl.LayersControl(
                base + overlay,
                id='layers-control'
            ),
        ]

    def componente_filtro(colunas: list[str] = ['']) -> list:
        filtro_tipo = dcc.RadioItems(
            ['Básico', 'Avançado'], 'Avançado',
            id='filtro_tipo'
        )

        filtro_coluna = dcc.Dropdown(
            colunas, colunas[0],
            id='filtro_coluna'
        )

        filtro_operacao = dcc.Dropdown(
            ['<', '<=', '==', '>=', '>', '!='], '',
            id='filtro_operacao'
        )

        filtro_valor = dcc.Input(
            type='text',
            id='filtro_valor',
            value='qtd_domicilios_esgotamento_rio > 0'
        )

        filtro_botao = html.Button(
            'Filtrar',
            id='filtro_botao'
        )

        return [
            filtro_tipo,
            filtro_coluna,
            filtro_operacao,
            filtro_valor,
            filtro_botao
        ]

    # Create example app.
    app = Dash()

    @app.callback(
        Output("setor_data", "children"),
        Input("distritos", "click_feature"),
        Input("setores", "click_feature"),
        prevent_initial_call=True
    )
    def feature_click(f1, f2):
        msg = None
        if f1 is not None:
            msg = f1['properties']['nm_distrito_municipal']
        if f2 is not None:
            msg = f2['properties']['codigo_setor']

        if msg is not None:
            return f"You clicked {msg}"

    @app.callback(
        Output('distritos_ol', 'checked'),
        Input('distrito_toggle', 'on')
    )
    def update_checked_layers(value):
        return value

    @app.callback(
        Output('setores_ol', 'children'),
        Input('filtro_botao', 'n_clicks'),
        State('filtro_tipo', 'value'),
        State('filtro_coluna', 'value'),
        State('filtro_operacao', 'value'),
        State('filtro_valor', 'value'),
    )
    def filter_setores(n_clicks, filtro_tipo, filtro_coluna, filtro_operacao, filtro_valor):
        if not filtro_valor:
            setores = SetoresTransformer()
        else:
            if filtro_tipo == 'Avançado':
                setores = SetoresTransformer(filtro_personalizado=filtro_valor)
            elif filtro_tipo == 'Básico':
                filtro_basico = f'{filtro_coluna} {filtro_operacao} {filtro_valor}'
                setores = SetoresTransformer(filtro_personalizado=filtro_basico)
        setor_geobuf = setores()
        # Carrega as variaveis de ambiente


        coluna_options = [
            col.split(' ')[-1] for col in setores.colunas_selecionadas
        ]

        return setor_overlay_children(setor_geobuf)
    
    def init_data():
        distritos = DistritoTransformer(get_geobuf=False)
        distritos = distritos()

        setor_children = filter_setores(
            n_clicks=0,
            filtro_tipo='Avançado',
            filtro_coluna='',
            filtro_operacao='',
            filtro_valor='qtd_domicilios_esgotamento_rio > 0'
        )

        return map_children(setor_children, distritos, False)

    app.layout = html.Div([
        dl.Map(center=[-23.5475, -46.6375],
               zoom=10,
               children=init_data(), id="map"),
        html.Div([
            html.Div(componente_filtro(
                [
                    'codigo_setor',
                    'qtd_domicilios',
                    'qtd_domicilios_rede_geral',
                    'qtd_domicilios_fossa_rudimentar',
                    'qtd_domicilios_esgotamento_rio',
                    'geometry'
                ]
            ), id='componente_filtro'),
            html.Div(id='setor_data'),
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
            )
        ],
            id="info_panel"),
        html.Div(children=[], id='message')
    ],
        id="wrapper"
    )

    app.run_server(debug=True, port=7777)
