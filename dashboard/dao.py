from duckdb import (
    connect,
    DuckDBPyConnection,
    DuckDBPyRelation
)
from geopandas import (
    GeoDataFrame,
    GeoSeries
)

from utils import duckdb_relation_to_gdf

class DuckDBDAO():
    '''
    IO manager para carregar os arquivos parquet do bucket S3.

    A princípio, funciona apenas recebendo todas as configurações de acesso (endpoint, access key, secret e bucket) nas configurações iniciais.
    Futuramente, pode ser modificado para construir uma sessão com os valores padrão caso não receba os parâmetros.
    '''

    def __init__(
        self,
        bucket_name: str,
        access_key: str,
        secret_key: str,
        endpoint: str,
        db_path:str = ''
    ) -> None:
        self.bucket_name = bucket_name
        self.access_key = access_key
        self.secret_key = secret_key
        self.endpoint = endpoint.removeprefix("http://")
        self.db_path = db_path
        self._connection = None

    @property
    def connection(self) -> DuckDBPyConnection:
        if self._connection == None:
            self._connection = connect(self.db_path)
            self._config_connection()

        return self._connection

    def _config_connection(self) -> None:
        self._connection.install_extension("httpfs")
        self._connection.load_extension("httpfs")
        self._connection.install_extension("spatial")
        self._connection.load_extension("spatial")

        query = f"""SET s3_endpoint = '{self.endpoint}';
        SET s3_use_ssl = false;
        SET s3_url_style = 'path';
        SET s3_access_key_id = '{self.access_key}';
        SET s3_secret_access_key = '{self.secret_key}';
        """
        self._connection.query(query)

    def _get_s3_path_for(self, table_name: str, bucket_name: str = None) -> str:
        bucket_name = bucket_name if bucket_name != None else self.bucket_name
        s3_path = f's3://{bucket_name}/dagster/{table_name}.parquet'
        return s3_path

    def duckdb_relation_to_gdf(self, relation: DuckDBPyRelation, geometry_columns: list = ['geometry'], default_geometry=None) -> GeoDataFrame:
        return duckdb_relation_to_gdf(relation, geometry_columns, default_geometry)

    def load_parquet(self, table_name: str, bucket_name: str = None, geometry_columns=['geometry'], default_geometry=None, lazy_loading=False) -> DuckDBPyRelation | GeoDataFrame:

        s3_path = self._get_s3_path_for(table_name)
        print(f'Gerando query para o arquivo {s3_path}...')

        geom_exclude = 'EXCLUDE (' + \
            ', '.join([f'{col}' for col in geometry_columns]) + ')'
        geom_as_text = ', '.join(
            [f'ST_AsText(ST_GeomFromWKB({col})) AS {col}' for col in geometry_columns])
        geom_fix = f'{geom_exclude}, {geom_as_text}'
        sql_query = f'SELECT * {geom_fix} FROM read_parquet("{s3_path}")'
        print('Query gerada:')
        print(sql_query)

        gdf = self.connection.sql(sql_query)
        if not lazy_loading:
            gdf = self.duckdb_relation_to_gdf(gdf, geometry_columns, default_geometry)
        return gdf
