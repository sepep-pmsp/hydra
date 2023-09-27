from dagster import (
    IOManager,
    io_manager,
    InitResourceContext,
    InputContext,
    OutputContext,
    StringSource
)
import geopandas as gpd
from pyarrow.fs import S3FileSystem


class GeoPandasParquetS3IOManager(IOManager):
    '''
    IO manager para salvar os GeoDataFrames como arquivos parquet num bucket S3.

    A princípio, funciona apenas recebendo todas as configurações de acesso (endpoint, access key e secret) nas configurações iniciais.
    Futuramente, pode ser modificado para construir uma sessão com os valores padrão caso não receba os parâmetros.
    '''

    def __init__(
            self,
            bucket_name: str,
            access_key: str,
            secret_key: str,
            endpoint: str
        ) -> None:
        self.bucket_name = bucket_name
        self.access_key = access_key
        self.secret_key = secret_key
        self.endpoint = endpoint

    def _get_s3_path_for(self, table:str) -> str:

        s3_path = f'{self.bucket_name}/dagster/{table}.parquet'
        return s3_path
    
    def _get_s3fs(self) -> S3FileSystem:
        s3fs = S3FileSystem(
            access_key=self.access_key,
            secret_key=self.secret_key,
            endpoint_override=self.endpoint,
            )
        return s3fs

    def _get_reading_input_log_message(self, path: str) -> str:
        return f"Loading S3 object from: {path}"

    def _get_writing_output_log_message(self, path: str) -> str:
        return f"Writing S3 object at: {path}"


    def handle_output(self, context: OutputContext, obj: gpd.GeoDataFrame):
        # Skip handling if the output is None
        if obj is None:
            return

        table_name = context.asset_key.to_python_identifier()
        
        s3_path = self._get_s3_path_for(table_name)
        s3fs = self._get_s3fs()

        context.log.info(self._get_writing_output_log_message(s3_path))
        obj.to_parquet(s3_path, filesystem=s3fs)

        # Recording metadata from an I/O manager:
        # https://docs.dagster.io/concepts/io-management/io-managers#recording-metadata-from-an-io-manager
        context.add_output_metadata({"uri": 's3://' + s3_path})

    def load_input(self, context: InputContext):
        # upstream_output.asset_key is the asset key given to the Out that we're loading for
        table_name = context.upstream_output.asset_key.to_python_identifier()
        
        s3_path = self._get_s3_path_for(table_name)
        s3fs = self._get_s3fs()
        
        context.log.info(self._get_reading_input_log_message(s3_path))
        gdf = gpd.read_parquet(s3_path, filesystem=s3fs)
        return gdf


@io_manager(
    config_schema={
        "bucket_name": StringSource,
        "access_key": StringSource,
        "secret_key": StringSource,
        "endpoint": StringSource,
    }
)
def geo_pandas_parquets3_io_manager(init_context: InitResourceContext) -> GeoPandasParquetS3IOManager:
    return GeoPandasParquetS3IOManager(
        bucket_name=init_context.resource_config["bucket_name"],
        access_key=init_context.resource_config["access_key"],
        secret_key=init_context.resource_config["secret_key"],
        endpoint=init_context.resource_config["endpoint"],
    )
