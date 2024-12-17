from duckdb import (
    DuckDBPyConnection,
    DuckDBPyRelation,
    connect,
)
import sqlparse
from logging import (
    Logger,
    getLogger,
)


class DuckDBS3():
    '''
    Classe criada para carregar e salvar os GeoDataFrames como arquivos parquet num bucket S3.

    A princípio, funciona apenas recebendo todas as configurações de acesso (endpoint, access key e secret) nas configurações iniciais.
    Futuramente, pode ser modificado para construir uma sessão com os valores padrão caso não receba os parâmetros.
    '''

    def __init__(
        self,
        bucket_name: str,
        access_key: str,
        secret_key: str,
        endpoint: str,
        db_path: str = None,
        logger: Logger = getLogger()
    ) -> None:
        self.bucket_name = bucket_name
        self.access_key = access_key
        self.secret_key = secret_key
        self.endpoint = endpoint
        self.db_path = db_path if db_path != None else ':memory:'
        self.logger = logger
        self._connection: DuckDBPyConnection = None

    @property
    def connection(self) -> DuckDBPyConnection:
        if self._connection == None:
            self._connection = connect(self.db_path)
            self._config_connection()

        return self._connection

    def _config_connection(self) -> None:
        self.connection.install_extension("httpfs")
        self.connection.load_extension("httpfs")
        self.connection.install_extension("spatial")
        self.connection.load_extension("spatial")

        query = f"""SET s3_endpoint = '{self.endpoint}';
        SET s3_use_ssl = false;
        SET s3_url_style = 'path';
        SET s3_access_key_id = '{self.access_key}';
        SET s3_secret_access_key = '{self.secret_key}';
        """
        self.connection.query(query)

    def _get_s3_path_for(self, table: str) -> str:
        s3_path = f's3://{self.bucket_name}/dagster/{table}.parquet'
        return s3_path

    def _get_reading_input_log_message(self, path: str) -> str:
        return f"Loading S3 object from: {path}"

    def _get_writing_output_log_message(self, path: str) -> str:
        return f"Writing S3 object at: {path}"

    def _geometry_columns_save_fix(self, geometry_columns: list[str]) -> str:
        geometry_columns = list(filter(None, geometry_columns))

        if not len(geometry_columns):
            return ''

        # O DuckDB ainda não trabalho com arquivos no formato GeopParquet, por isso transformo a geometria
        # para salvar um parquet "compatível" de acordo com a especificação
        # em https://github.com/opengeospatial/geoparquet/blob/main/format-specs/compatible-parquet.md
        geom_as_blob = ', '.join(
            [f"ST_AsWKB(ST_FlipCoordinates(ST_Transform(ST_GeomFromText({col}), 'EPSG:31983', 'EPSG:4326'))) AS {col}"
             for col in geometry_columns])

        return f' , {geom_as_blob}'

    def _to_compatible_geoparquet(self, rel: DuckDBPyRelation, geometry_columns: list[str] = None) -> DuckDBPyRelation:
        geometry_columns = geometry_columns if geometry_columns != None else []
        other_columns = [
            col for col in rel.columns if col not in geometry_columns]
        other_columns = ', '.join(other_columns)

        geom_as_blob = self._geometry_columns_save_fix(geometry_columns)

        return rel.select(f'{other_columns}{geom_as_blob}')

    def save_parquet(self, table_name: str, rel: DuckDBPyRelation, geometry_columns: list[str] = None, **kwargs) -> str:

        s3_path = self._get_s3_path_for(table_name)

        self.logger.info(self._get_writing_output_log_message(s3_path))
        self.logger.info(f'Columns: {rel.columns}')
        self.logger.info(f'Code to run: {rel.explain()}')

        self._to_compatible_geoparquet(
            rel, geometry_columns).to_parquet(s3_path, **kwargs)

        return s3_path

    def _geometry_columns_load_fix(self, geometry_columns: list[str], table:DuckDBPyRelation) -> str:
        if geometry_columns == None:
            geometry_columns = [None]

        geometry_columns = list(filter(None, geometry_columns))

        if not len(geometry_columns):
            geometry_columns = [col for col, type in zip(table.columns, table.dtypes) if type == 'GEOMETRY']

        if not len(geometry_columns):
            return ''

        geom_repl_str = [f'ST_AsText(ST_GeomFromWKB({g})) AS {g}' for g in geometry_columns]
        replace_str = f'REPLACE ({", ".join(geom_repl_str)})'

        return replace_str

    def load_parquet(self, table_name: str, geometry_columns: list[str] = None) -> DuckDBPyRelation:

        s3_path = self._get_s3_path_for(table_name)
        self.logger.info(f'Gerando query para o arquivo {s3_path}...')
            
        table = self.connection.table(s3_path)

        geom_fix = self._geometry_columns_load_fix(geometry_columns, table)

        sql_query = f'SELECT * {geom_fix} FROM read_parquet("{s3_path}") AS {table_name}'
        self.logger.info('Query gerada:')
        self.logger.info(sqlparse.format(
            sql_query, reindent=True, keyword_case='upper'))

        gdf = self.connection.sql(sql_query)
        return gdf
