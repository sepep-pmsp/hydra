from dotenv import load_dotenv
import os
import json
import dash_leaflet.express as dlx



load_dotenv('../.env')

def get_bucket_os():
    AWS_S3_BUCKET = os.getenv("MINIO_SILVER_BUCKET_NAME")
    AWS_ACCESS_KEY_ID = os.getenv("MINIO_ROOT_USER")
    AWS_SECRET_ACCESS_KEY = os.getenv("MINIO_ROOT_PASSWORD")
    ENDPOINT_OVERRIDE = os.getenv("MINIO_ENDPOINT_URL")

    return {"bucket_name" : AWS_S3_BUCKET, 
            "access_key" : AWS_ACCESS_KEY_ID, 
            "secret_key" : AWS_SECRET_ACCESS_KEY,
            "endpoint":  ENDPOINT_OVERRIDE}

def receber_distrito_aleatorio_em_geodataframe(t):

    random_dist = t[1].sample(n=1)
    gdf_distrito_aleatorio = json.loads(random_dist.to_json())

    return gdf_distrito_aleatorio


def receber_geobuf_de_geodataframe (gdf):

    geojson = json.loads(gdf.to_json())
        
    geobuf = dlx.geojson_to_geobuf(geojson)

    return geobuf
    