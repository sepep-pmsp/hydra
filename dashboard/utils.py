import json
from dash_leaflet.express import geojson_to_geobuf
from duckdb import DuckDBPyRelation
from geopandas import GeoDataFrame, GeoSeries
from dotenv import load_dotenv
import os

def load_s3_vars():
    load_dotenv('../.env')
    AWS_S3_BUCKET = os.getenv("MINIO_SILVER_BUCKET_NAME")
    AWS_ACCESS_KEY_ID = os.getenv("MINIO_ROOT_USER")
    AWS_SECRET_ACCESS_KEY = os.getenv("MINIO_ROOT_PASSWORD")
    ENDPOINT_OVERRIDE = os.getenv("MINIO_ENDPOINT_URL")

    return {"bucket_name" : AWS_S3_BUCKET, 
            "access_key" : AWS_ACCESS_KEY_ID, 
            "secret_key" : AWS_SECRET_ACCESS_KEY,
            "endpoint":  ENDPOINT_OVERRIDE}

def gdf_to_geobuf(gdf:GeoDataFrame) -> str:
    geojson = json.loads(gdf.to_json())
    geobuf = geojson_to_geobuf(geojson)
    return geobuf

def duckdb_relation_to_gdf(relation: DuckDBPyRelation, geometry_columns: list = ['geometry'], default_geometry=None) -> GeoDataFrame:
        geometry_columns = geometry_columns if geometry_columns else []

        gdf = GeoDataFrame(relation.df())
        for col in geometry_columns:
            gdf.loc[:, col] = GeoSeries.from_wkt(gdf.loc[:, col])
        if default_geometry or len(geometry_columns):
            default_geometry = default_geometry if default_geometry != None else geometry_columns[
                0]
            gdf = gdf.set_geometry(default_geometry)
            gdf = gdf.set_crs(epsg=31983)
            gdf = gdf.to_crs(epsg=4326)

        return gdf