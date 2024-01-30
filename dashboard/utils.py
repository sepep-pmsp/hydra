import json
from dash_leaflet.express import geojson_to_geobuf
from geopandas import GeoDataFrame


from etls.etl_scripts.utils.utils import get_bucket_os as load_s3_vars

def gdf_to_geobuf(gdf:GeoDataFrame) -> str:
    geojson = json.loads(gdf.to_json())
    geobuf = geojson_to_geobuf(geojson)
    return geobuf