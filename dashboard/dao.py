from duckdb import (
    connect,
    DuckDBPyConnection,
    DuckDBPyRelation
)
from geopandas import (
    GeoDataFrame,
    GeoSeries
)

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
        self.connection = None

    def _get_connection(self) -> DuckDBPyConnection:
        if self.connection == None:
            self.connection = connect(self.db_path)
            self._config_connection()

        return self.connection

    def _config_connection(self) -> None:
        self._get_connection().install_extension("httpfs")
        self._get_connection().load_extension("httpfs")
        self._get_connection().install_extension("spatial")
        self._get_connection().load_extension("spatial")

        query = f"""SET s3_endpoint = '{self.endpoint}';
        SET s3_use_ssl = false;
        SET s3_url_style = 'path';
        SET s3_access_key_id = '{self.access_key}';
        SET s3_secret_access_key = '{self.secret_key}';
        """
        self._get_connection().query(query)

    def _get_s3_path_for(self, table_name: str, bucket_name: str = None) -> str:
        bucket_name = bucket_name if bucket_name != None else self.bucket_name
        s3_path = f's3://{bucket_name}/dagster/{table_name}.parquet'
        return s3_path

    def duckdb_relation_to_gdf(self, relation: DuckDBPyRelation, geometry_columns: list = ['geometry'], default_geometry=None) -> GeoDataFrame:
        default_geometry = default_geometry if default_geometry != None else geometry_columns[
            0]

        gdf = GeoDataFrame(relation.df())
        for col in geometry_columns:
            gdf.loc[:, col] = GeoSeries.from_wkt(gdf.loc[:, col])
        gdf = gdf.set_geometry(default_geometry)
        gdf = gdf.set_crs(epsg=31983)
        gdf = gdf.to_crs(epsg=4326)

        return gdf

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

        gdf = self._get_connection().sql(sql_query)
        if not lazy_loading:
            gdf = self.duckdb_relation_to_gdf(gdf, geometry_columns, default_geometry)
        return gdf