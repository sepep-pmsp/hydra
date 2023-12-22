import dash_leaflet as dl
import dash_leaflet.express as dlx
from dash import Dash, html, Output, Input
from dash_extensions.javascript import arrow_function
import geopandas as gpd
from dotenv import load_dotenv
import os
from pyarrow.fs import S3FileSystem
import json

from os import path

load_dotenv('../.env')

AWS_S3_BUCKET = os.getenv("MINIO_SILVER_BUCKET_NAME")
AWS_ACCESS_KEY_ID = os.getenv("MINIO_ROOT_USER")
AWS_SECRET_ACCESS_KEY = os.getenv("MINIO_ROOT_PASSWORD")
ENDPOINT_OVERRIDE = os.getenv("MINIO_ENDPOINT_URL")

s3fs = S3FileSystem(
    access_key=AWS_ACCESS_KEY_ID,
    secret_key=AWS_SECRET_ACCESS_KEY,
    endpoint_override=ENDPOINT_OVERRIDE,
)


def _get_s3_path_for(table_name: str, bucket_name: str = AWS_S3_BUCKET) -> str:

    s3_path = f'{bucket_name}/dagster/{table_name}.parquet'
    return s3_path


def load_parquet(table_name: str, bucket_name: str = AWS_S3_BUCKET) -> gpd.GeoDataFrame:

    s3_path = _get_s3_path_for(table_name)
    print(f'Baixando parquet de {s3_path}')

    gdf = gpd.read_parquet(s3_path, filesystem=s3fs)
    gdf = gdf.to_crs(epsg=4326)
    return gdf


gdf_distrito = load_parquet('distrito_municipal_digested')
gdf_distrito = gdf_distrito[['cd_identificador_distrito', 'cd_distrito_municipal',
                             'nm_distrito_municipal', 'sg_distrito_municipal', 'geometry']]
gdf_distrito['tooltip'] = gdf_distrito['nm_distrito_municipal']

random_dist = gdf_distrito.sample(n=1)

dist_geojson = json.loads(random_dist.to_json())
dist_geobuf = dlx.geojson_to_geobuf(dist_geojson)


    gdf_distrito = load_parquet('distrito_municipal_digested')
    gdf_distrito = gdf_distrito[['cd_identificador_distrito', 'cd_distrito_municipal', 'nm_distrito_municipal', 'sg_distrito_municipal', 'geometry']]
    gdf_distrito = gdf_distrito.drop_duplicates()
    gdf_distrito.to_parquet(local_file)

gdf_distrito = gpd.read_parquet(local_file)
geojson=json.loads(gdf_distrito.to_json())

# Create example app.
app = Dash()
app.layout = html.Div([
    dl.Map(center=[-23.5475, -46.6375], children=[
        dl.TileLayer(),
        dl.GeoJSON(data=geojson, id="distritos",
                   hoverStyle=arrow_function(dict(weight=5, color='#666', dashArray='')),
                   zoomToBounds=True, zoomToBoundsOnClick=True),
    ]),
    html.Div(id="capital")
    ],
    id="wrapper"
)

@app.callback(Output("capital", "children"), [Input("distritos", "clickData")])
def capital_click(feature):
    if feature is not None:
        return f"You clicked {feature['properties']['nm_distrito_municipal']}"

if __name__ == '__main__':
    app.run_server(debug=True, port=7777)