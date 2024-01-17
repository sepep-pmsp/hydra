from dotenv import load_dotenv
import os
import json
import dash_leaflet.express as dlx
from dashboard.etls.scripts.distrito_municipal.transformer import Transformer



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

def receber_distrito_aleatorio_em_geojson():
    T = Transformer
    t = T(get_geobuf=False)

    return t
