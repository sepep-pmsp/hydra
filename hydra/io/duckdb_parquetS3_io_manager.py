from dagster import (
    IOManager,
    io_manager,
    InitResourceContext,
    InputContext,
    OutputContext,
    StringSource
)
import geopandas as gpd
from duckdb import (
    connect,
    DuckDBPyConnection,
    DuckDBPyRelation
)
import sqlparse


class DuckDBParquetS3IOManager(IOManager):
    '''
    IO manager para salvar os GeoDataFrames como arquivos parquet num bucket S3.

    A princípio, funciona apenas recebendo todas as configurações de acesso (endpoint, access key e secret) nas configurações iniciais.
    Futuramente, pode ser modificado para construir uma sessão com os valores padrão caso não receba os parâmetros.
    '''
    _connection:DuckDBPyConnection = None

    def __init__(
            self,
            bucket_name: str,
            access_key: str,
            secret_key: str,
            endpoint: str,
            db_path: str,
            geom_cols: list[str],
            default_geom: str = None
        ) -> None:
        self.bucket_name = bucket_name
        self.access_key = access_key
        self.secret_key = secret_key
        self.endpoint = endpoint
        self.db_path = db_path
        self._geom_cols = geom_cols
        self._default_geom = default_geom
        self._connection = None

    @property
    def geom_cols(self) -> list[str]:
        return self._geom_cols

    @geom_cols.setter
    def geom_cols(self, value:list[str]) -> None:
        while '' in self.value:
            self.value.remove('')
        if not value:
            raise AttributeError('A lista deve conter ao menos uma string não vazia.')
        self._geom_cols = value

    @property
    def default_geom(self) -> str:
        return self._default_geom

    @default_geom.setter
    def geom_cols(self, value:str) -> None:
        if value not in self.geom_cols:
            raise AttributeError('A coluna deve estar presente na lista de colunas de geometria.')
        if not value:
            self._default_geom = self.geom_cols[0]
        self._default_geom = value
    
    @classmethod
    def connection(cls) -> DuckDBPyConnection:
        if cls._connection == None:
            cls._connection = connect(cls.db_path)
            cls._config_connection()

        return cls.connection

    @classmethod
    def _config_connection(cls) -> None:
        cls.connection.install_extension("httpfs")
        cls.connection.load_extension("httpfs")
        cls.connection.install_extension("spatial")
        cls.connection.load_extension("spatial")

        query = f"""SET s3_endpoint = '{cls.endpoint}';
        SET s3_use_ssl = false;
        SET s3_url_style = 'path';
        SET s3_access_key_id = '{cls.access_key}';
        SET s3_secret_access_key = '{cls.secret_key}';
        """
        cls.connection.query(query)

    def _get_s3_path_for(self, table:str) -> str:

        s3_path = f's3://{self.bucket_name}/dagster/{table}.parquet'
        return s3_path

    def _get_reading_input_log_message(self, path: str) -> str:
        return f"Loading S3 object from: {path}"

    def _get_writing_output_log_message(self, path: str) -> str:
        return f"Writing S3 object at: {path}"


    def handle_output(self, context: OutputContext, obj: DuckDBPyRelation):
        # Skip handling if the output is None
        if obj is None:
            return

        table_name = context.asset_key.to_python_identifier()
        
        s3_path = self._get_s3_path_for(table_name)

        context.log.info(self._get_writing_output_log_message(s3_path))
        obj.to_parquet(s3_path)

        # Recording metadata from an I/O manager:
        # https://docs.dagster.io/concepts/io-management/io-managers#recording-metadata-from-an-io-manager
        context.add_output_metadata({"uri": s3_path})

    def load_input(self, context: InputContext):
        # upstream_output.asset_key is the asset key given to the Out that we're loading for
        table_name = context.upstream_output.asset_key.to_python_identifier()
    
        s3_path = self._get_s3_path_for(table_name)
        print(f'Gerando query para o arquivo {s3_path}...')

        geom_exclude = 'EXCLUDE (' + \
            ', '.join([f'{col}' for col in self.geom_cols]) + ')'
        geom_as_text = ', '.join(
            [f'ST_AsText(ST_GeomFromWKB({col})) AS {col}' for col in self.geom_cols])
        geom_fix = f'{geom_exclude}, {geom_as_text}'
        sql_query = f'SELECT * {geom_fix} FROM read_parquet("{s3_path}")'
        print('Query gerada:')
        print(sqlparse.format(sql_query, reindent=True, keyword_case='upper'))

        gdf = DuckDBParquetS3IOManager.connection.sql(sql_query)
        return gdf


@io_manager(
    config_schema={
        "bucket_name": StringSource,
        "access_key": StringSource,
        "secret_key": StringSource,
        "endpoint": StringSource,
        "access_key": StringSource,
        "db_path": StringSource,
        "geom_cols": list[StringSource],
        "default_geom": StringSource,
    }
)
def duckdb_parquets3_io_manager(init_context: InitResourceContext) -> DuckDBParquetS3IOManager:
    return DuckDBParquetS3IOManager(
        bucket_name=init_context.resource_config["bucket_name"],
        access_key=init_context.resource_config["access_key"],
        secret_key=init_context.resource_config["secret_key"],
        endpoint=init_context.resource_config["endpoint"],
        db_path=init_context.resource_config["db_path"],
        geom_cols=init_context.resource_config["geom_cols"],
        default_geom=init_context.resource_config["default_geom"],
    )
