import dash_leaflet as dl
import dash_leaflet.express as dlx
import dash_daq as daq
from dash import Dash, html, Output, Input
from dash_extensions.javascript import arrow_function
import geopandas as gpd
from dotenv import load_dotenv
import os
from pyarrow.fs import S3FileSystem
import json

from dao import DuckDBDAO

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


gdf_distrito = duckdb_dao.load_parquet('distrito_municipal_digested')
gdf_distrito = gdf_distrito[['cd_identificador_distrito', 'cd_distrito_municipal',
                             'nm_distrito_municipal', 'sg_distrito_municipal', 'geometry']]
gdf_distrito['tooltip'] = gdf_distrito['nm_distrito_municipal']

random_dist = gdf_distrito.sample(n=1)

dist_geojson = json.loads(random_dist.to_json())
dist_geobuf = dlx.geojson_to_geobuf(dist_geojson)

gdf_setor = duckdb_dao.load_parquet('setor_censitario_enriched')
filtro_setor = gdf_setor.intersects(random_dist['geometry'].iloc[0])
gdf_setor = gdf_setor[filtro_setor]
gdf_setor['tooltip'] = gdf_setor['cd_original_setor_censitario']
setor_geojson = json.loads(gdf_setor.to_json())
setor_geobuf = dlx.geojson_to_geobuf(setor_geojson)


def map_children(distrito_toggle: bool):
    return [dl.LayersControl(
            [dl.BaseLayer(
                dl.TileLayer(),
                name='Base',
                checked=True
            )] + [
                dl.Overlay(dl.Pane(dl.GeoJSON(data=dist_geobuf, id="distritos", format='geobuf',
                                      options={
                                      "style":{'color': 'green',
                                             'fillColor': 'green',
                                             'fillOpacity': 0.5}},
                                      hoverStyle=arrow_function(
                                          dict(weight=5, color='#666', dashArray=''))
                                    ),
                           name='distritos_pane',
                           style={'zIndex':1000}
                           ),
                           id='distritos_ol',
                           name='distritos_ol',
                           checked=distrito_toggle
                           ),
                dl.Overlay(children=[dl.Pane(dl.GeoJSON(data=setor_geobuf, id="setores", format='geobuf',
                       hideout=dict(selected=[]),
                       options={
                       "style": {
                           'color': 'red',
                           'fillColor': 'red'
                       }},
                       hoverStyle=arrow_function(
                           dict(weight=5, color='red', dashArray='', fillOpacity=0.5)),
                       zoomToBounds=True),
                        name='setores_pane',
                        style={'zIndex': 1100}
                    )],
                        id="setores_ol",
                        name='setores_ol',
                        checked=True
                    ),

                ],
            id='layers-control'),]


# Create example app.
app = Dash()
app.layout = html.Div([
    dl.Map(center=[-23.5475, -46.6375],
           children=map_children(False), id="map"),
    html.Div([
        html.Div(id='setor_data'),
        html.Div([
            html.H2('Distrito', id='distrito_header', className='layer_header'),
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
    html.Div(children=[],id='message')
],
    id="wrapper"
)

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
        msg = f2['properties']['cd_original_setor_censitario']

    if msg is not None:
        return f"You clicked {msg}"


@app.callback(
    Output('distritos_ol', 'checked'),
    Input('distrito_toggle', 'on')
)
def update_checked_layers(value):
    return value

if __name__ == '__main__':
    app.run_server(debug=True, port=7777)
