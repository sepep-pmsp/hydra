import json
from dash_leaflet.express import geojson_to_geobuf
from geopandas import GeoDataFrame

def gdf_to_geobuf(gdf:GeoDataFrame) -> str:
    geojson = json.loads(gdf.to_json())
    geobuf = geojson_to_geobuf(geojson)
    return geobuf