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

    return {"bucket_name": AWS_S3_BUCKET,
            "access_key": AWS_ACCESS_KEY_ID,
            "secret_key": AWS_SECRET_ACCESS_KEY,
            "endpoint":  ENDPOINT_OVERRIDE}


def gdf_to_geobuf(gdf: GeoDataFrame) -> str:
    geojson = json.loads(gdf.to_json())
    geobuf = geojson_to_geobuf(geojson)
    return geobuf


def _resolve_geometry_columns(relation: DuckDBPyRelation,
                              geometry_columns: list = None,
                              geometries_crs: dict = None) -> list:
    """
    Resolves and returns a list of geometry columns for a               
    DuckDBPyRelation object.
    This function identifies geometry columns in the given relation
    based on the provided geometry_columns list, geometries_crs
    dictionary, or by detecting columns with the 'GEOMETRY' data
    type.

    Parameters:
    relation (DuckDBPyRelation): The relation object from which to
    resolve geometry columns.
    geometry_columns (list, optional): A list of column names to
    consider as geometry columns. Defaults to an empty list if not
                                        provided.
    geometries_crs (dict, optional): A dictionary where keys are
    column names and values are coordinate reference systems (CRS).
    Used to identify geometry columns if geometry_columns is not
    provided. Defaults to None.

    Returns:
    list: A list of resolved geometry column names present in the
    relation.
    """

    geometry_columns = geometry_columns if geometry_columns else []

    geometry_columns = [col for col in geometry_columns
                        if col in relation.columns]

    if not len(geometry_columns):
        if geometries_crs:
            geometry_columns = [col for col in geometries_crs.keys()
                                if col in relation.columns]

    if not len(geometry_columns):
        geometry_columns = [
            col for col, type in zip(relation.columns, relation.dtypes)
            if type == 'GEOMETRY'
        ]

    return geometry_columns

def _load_geospatial_relation(relation: DuckDBPyRelation,
                   geometry_columns: list) -> GeoDataFrame:
    """
    Loads the relation as GeoDataFrame converting the geometry columns.
    This is needed because the DuckDBPyRelation can't automatically
    convert geometry columns from GEOMETRY type format to GeoSeries.
    Args:
        geometry_columns (list): List of column names that contain
        geometry data.

        relation (DuckDBPyRelation): The DuckDB relation containing the
        data.

    Returns:
        GeoDataFrame: A GeoDataFrame with the specified geometry columns
        as GeoSeries.
    """

    cols_replace = [f'ST_AsHEXWKB({col}) as {col}'
                    for col in geometry_columns]
    replace_str = (f'REPLACE ({", ".join(cols_replace)})'
                   if len(cols_replace) else '')

    gdf = GeoDataFrame(relation.select(f'* {replace_str}').df())
    for col in geometry_columns:
        gdf.loc[:, col] = GeoSeries.from_wkb(gdf.loc[:, col])

    return gdf
    

def duckdb_relation_to_gdf(
        relation: DuckDBPyRelation,
        geometry_columns: list = None,
        default_geometry: str = None,
        geometries_crs: dict = None,
        output_crs: str = 'EPSG:4326') -> GeoDataFrame:

    geometry_columns = _resolve_geometry_columns(relation,
                                                 geometry_columns,
                                                 geometries_crs)
    
    gdf = _load_geospatial_relation(relation, geometry_columns)

    if default_geometry or len(geometry_columns):
        default_geometry = (default_geometry
                            if default_geometry != None
                            else geometry_columns[0])
        gdf = gdf.set_geometry(default_geometry)

    # If geometries_crs doesn't exist, assumes all geometries are in
    # EPSG:31983
    if geometries_crs == None:
        geometries_crs = {geom: 'EPSG:31983' for geom in geometry_columns}

    if geometries_crs:
        for geom, crs in geometries_crs.items():
            if geom in gdf.columns:
                gdf[geom] = gdf[geom].set_crs(crs)
                gdf[geom] = gdf[geom].to_crs(output_crs)

    return gdf
