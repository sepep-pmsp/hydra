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
            db_path: str = ':memory:',
            logger: Logger = getLogger()
        ) -> None:
        self.bucket_name = bucket_name
        self.access_key = access_key
        self.secret_key = secret_key
        self.endpoint = endpoint
        self.db_path = db_path
        self.logger = logger
        self._connection:DuckDBPyConnection = None
    
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

    def _get_s3_path_for(self, table:str) -> str:
        s3_path = f's3://{self.bucket_name}/dagster/{table}.parquet'
        return s3_path

    def _get_reading_input_log_message(self, path: str) -> str:
        return f"Loading S3 object from: {path}"

    def _get_writing_output_log_message(self, path: str) -> str:
        return f"Writing S3 object at: {path}"

    def save_parquet(self, table_name:str, rel: DuckDBPyRelation, geometry_columns=['geometry'], **kwargs) -> str:        
        other_columns = [col for col in rel.columns if col not in geometry_columns]
        other_columns = ', '.join(other_columns)

        geom_as_blob = ', '.join(
            [f'ST_AsWKB(ST_GeomFromText({col})) AS {col}' for col in geometry_columns])
        
        s3_path = self._get_s3_path_for(table_name)

        self.logger.info(self._get_writing_output_log_message(s3_path))
        rel.select(f'{other_columns} , {geom_as_blob}').to_parquet(s3_path, **kwargs)

        return s3_path

    def load_parquet(self, table_name: str, geometry_columns=['geometry']) -> DuckDBPyRelation:

        s3_path = self._get_s3_path_for(table_name)
        self.logger.info(f'Gerando query para o arquivo {s3_path}...')

        geom_exclude = 'EXCLUDE (' + \
            ', '.join([f'{col}' for col in geometry_columns]) + ')'
        geom_as_text = ', '.join(
            [f'ST_AsText(ST_GeomFromWKB({col})) AS {col}' for col in geometry_columns])
        geom_fix = f'{geom_exclude}, {geom_as_text}'
        sql_query = f'SELECT * {geom_fix} FROM read_parquet("{s3_path}")'
        self.logger.info('Query gerada:')
        self.logger.info(sqlparse.format(sql_query, reindent=True, keyword_case='upper'))

        gdf = self.connection.sql(sql_query)
        return gdf