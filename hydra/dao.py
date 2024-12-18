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
from json import dumps, loads


class DuckDBS3():
    '''
    Classe criada para carregar e salvar os GeoDataFrames como arquivos 
    parquet num bucket S3.

    A princípio, funciona apenas recebendo todas as configurações de 
    acesso (endpoint, access key e secret) nas configurações iniciais.
    Futuramente, pode ser modificado para construir uma sessão com os 
    valores padrão caso não receba os parâmetros.
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

    def _geometry_columns_save_fix(self,
                                   rel: DuckDBPyRelation,
                                   geometry_columns: list[str]) -> str:
        if geometry_columns == None:
            geometry_columns = [None]

        geometry_columns = list(filter(None, geometry_columns))

        if not len(geometry_columns):
            return ''

        # O DuckDB trabalha parcialmente com arquivos GeopParquet, mas
        # aceita apenas o CRS padrão, OGC:CRS84. Mais detalhes em
        # https://github.com/duckdb/duckdb/pull/12503
        transform_str = ', '.join(
            [f"ST_Transform({col}, 'EPSG:31983', 'OGC:CRS84') AS {col}"
             for col in geometry_columns])

        return f'REPLACE ({transform_str})'

    def save_parquet(self,
                     table_name: str,
                     rel: DuckDBPyRelation,
                     geometry_columns: list[str] = None,
                     **kwargs) -> str:

        s3_path = self._get_s3_path_for(table_name)

        self.logger.info(self._get_writing_output_log_message(s3_path))
        self.logger.info(f'Columns: {rel.columns}')
        self.logger.info(f'Code to run: {rel.explain()}')

        geom_fix = self._geometry_columns_save_fix(
            rel=rel, geometry_columns=geometry_columns)
        rel.select(f'* {geom_fix}').to_parquet(s3_path, **kwargs)

        return s3_path

    def _get_geometry_columns_crs(
            self,
            s3_path: str,
            geometry_columns: list[str]) -> dict:

        sql = ("SELECT value "
               f"FROM parquet_kv_metadata('{s3_path}') "
               "WHERE key = 'geo'")
        geo_metadata = loads(self.connection.sql(sql).fetchone()[0])

        cols_crs = dict()
        for col in geometry_columns:
            if 'crs' in geo_metadata['columns'][col]:
                col_crs = geo_metadata['columns'][col]['crs']
                col_crs_authority = col_crs['id']['authority']
                col_crs_code = col_crs['id']['code']
                cols_crs.update({col: f'{col_crs_authority}:{col_crs_code}'})
            else:
                cols_crs.update({col: 'OGC:CRS84'})
        
        return cols_crs

    def _geometry_columns_load_fix(
            self,
            geometry_columns: list[str],
            s3_path: str,
            default_crs:str = 'EPSG:31983') -> str:
        if geometry_columns == None:
            geometry_columns = [None]

        geometry_columns = list(filter(None, geometry_columns))

        if not len(geometry_columns):
            table = self.connection.table(s3_path).limit(1)
            geometry_columns = [col for col, type in zip(
                table.columns, table.dtypes) if type == 'GEOMETRY']

        if not len(geometry_columns):
            return ''

        geom_cols_crs = self._get_geometry_columns_crs(s3_path,
                                                       geometry_columns)

        geom_repl_str = [
            f"ST_Transform({col}, '{crs}', '{default_crs}') AS {col}"
            for col, crs in geom_cols_crs.items()
            if crs.lower() != default_crs.lower()]
        
        replace_str = (f'REPLACE ({", ".join(geom_repl_str)})'
                       if len(geom_repl_str) else '')

        return replace_str

    def load_parquet(self,
                     table_name: str,
                     geometry_columns: list[str] = None) -> DuckDBPyRelation:

        s3_path = self._get_s3_path_for(table_name)
        self.logger.info(f'Gerando query para o arquivo {s3_path}...')

        geom_fix = self._geometry_columns_load_fix(geometry_columns, s3_path)

        sql_query = (f'SELECT * {geom_fix} '
                     f'FROM read_parquet("{s3_path}") AS {table_name}')
        self.logger.info('Query gerada:')
        self.logger.info(sqlparse.format(
            sql_query, reindent=True, keyword_case='upper'))

        gdf = self.connection.sql(sql_query)
        return gdf
