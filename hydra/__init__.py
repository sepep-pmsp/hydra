from dagster import (
    AssetSelection,
    Definitions,
    EnvVar,
    define_asset_job,
    load_assets_from_modules,
)
from dagster_aws.s3 import (
    ConfigurablePickledObjectS3IOManager,
    S3Resource
)


from . import assets
from .resources import (
    IBGE_api,
    GeosampaClient,
    CensoResource,
    DuckDBS3Resource
)
from .io import (
    postgres_pandas_io_manager,
    geo_pandas_parquets3_io_manager
)
from .schedules import (
    censo_2010_schedule,
    geosampa_schedule,
    censo_2022_schedule
)

all_assets = load_assets_from_modules([assets])

municipios_job = define_asset_job(
    "municipios_job", selection=AssetSelection.all()
)

# Definições dos resources
geosampa_client = GeosampaClient()

ibge_api = IBGE_api()

duckdb_s3_resource = DuckDBS3Resource(
    endpoint=EnvVar('MINIO_ENDPOINT_URL'),
    access_key=EnvVar('MINIO_ROOT_USER'),
    secret_key=EnvVar('MINIO_ROOT_PASSWORD'),
    bucket_name=EnvVar('MINIO_SILVER_BUCKET_NAME'),
    db_path=EnvVar('DUCKDB_PATH')
)

# Definições dos managers

bronze_io_manager = ConfigurablePickledObjectS3IOManager(
    s3_resource=S3Resource(
        endpoint_url=EnvVar('MINIO_ENDPOINT_URL'),
        aws_access_key_id=EnvVar('MINIO_ROOT_USER'),
        aws_secret_access_key=EnvVar('MINIO_ROOT_PASSWORD'),
    ), s3_bucket=EnvVar('MINIO_BRONZE_BUCKET_NAME')
)

silver_io_manager = ConfigurablePickledObjectS3IOManager(
    s3_resource=S3Resource(
        endpoint_url=EnvVar('MINIO_ENDPOINT_URL'),
        aws_access_key_id=EnvVar('MINIO_ROOT_USER'),
        aws_secret_access_key=EnvVar('MINIO_ROOT_PASSWORD'),
    ), s3_bucket=EnvVar('MINIO_SILVER_BUCKET_NAME')
)

gpd_silver_io_manager = geo_pandas_parquets3_io_manager.configured(
    {
        'bucket_name': {'env': 'MINIO_SILVER_BUCKET_NAME'},
        'access_key': {'env': 'MINIO_ROOT_USER'},
        'secret_key': {'env': 'MINIO_ROOT_PASSWORD'},
        'endpoint': {'env': 'MINIO_ENDPOINT_URL'},
    }
)

gold_io_manager = postgres_pandas_io_manager.configured(
    {
        'server': {'env': 'GOLD_DB_HOST'},
        'db': {'env': 'GOLD_DB_NAME'},
        'uid': {'env': 'GOLD_DB_USER'},
        'pwd': {'env': 'GOLD_DB_PASSWORD'},
        'port': {'env': 'GOLD_DB_PORT'},
    }
)


# Carregamento das definições
defs = Definitions(
    assets=all_assets,
    schedules=[
        geosampa_schedule,
        censo_2010_schedule,
        censo_2022_schedule
    ],
    resources={
        "bronze_io_manager": bronze_io_manager,
        "silver_io_manager": silver_io_manager,
        'gpd_silver_io_manager': gpd_silver_io_manager,
        'gold_io_manager': gold_io_manager,
        'ibge_api': ibge_api,
        'geosampa_client': geosampa_client,
        'censo_resource': CensoResource(),
        'duckdb_s3_resource': duckdb_s3_resource
    },
)
