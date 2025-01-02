from duckdb import (
    connect,
    DuckDBPyConnection,
    DuckDBPyRelation
)
from geopandas import (
    GeoDataFrame,
    GeoSeries
)
import json

from utils import duckdb_relation_to_gdf


class DuckDBDAO():
    '''
    IO manager para carregar os arquivos parquet do bucket S3.

    A princípio, funciona apenas recebendo todas as configurações de 
    acesso (endpoint, access key, secret e bucket) nas configurações
    iniciais.
    Futuramente, pode ser modificado para construir uma sessão com os
    valores padrão caso não receba os parâmetros.
    '''

    def __init__(
        self,
        bucket_name: str,
        access_key: str,
        secret_key: str,
        endpoint: str,
        db_path: str = ''
    ) -> None:
        self.bucket_name = bucket_name
        self.access_key = access_key
        self.secret_key = secret_key
        self.endpoint = (endpoint
                         .removeprefix("http://")
                         .removeprefix("https://"))
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

    def _get_s3_path_for(self,
                         table_name: str,
                         bucket_name: str = None) -> str:

        bucket_name = bucket_name if bucket_name != None else self.bucket_name
        s3_path = f's3://{bucket_name}/dagster/{table_name}.parquet'
        return s3_path

    def _get_geometry_columns_crs(
            self,
            s3_path: str,
            geometry_columns: list[str]) -> dict:

        sql = ("SELECT value "
                f"FROM parquet_kv_metadata('{s3_path}') "
                "WHERE key = 'geo'")
        geo_metadata = json.loads(self.connection.sql(sql).fetchone()[0])

        cols_crs = dict()
        for col in geometry_columns:
            if col not in geo_metadata['columns']:
                continue
            if 'crs' in geo_metadata['columns'][col]:
                col_crs = geo_metadata['columns'][col]['crs']
                col_crs_authority = col_crs['id']['authority']
                col_crs_code = col_crs['id']['code']
                cols_crs.update({col: f'{col_crs_authority}:{col_crs_code}'})
            else:
                cols_crs.update({col: 'OGC:CRS84'})
        
        return cols_crs

    def duckdb_relation_to_gdf(self,
                               relation: DuckDBPyRelation,
                               geometry_columns: list = ['geometry'],
                               default_geometry=None,
                               geometries_crs=None) -> GeoDataFrame:

        return duckdb_relation_to_gdf(relation=relation,
                                      geometry_columns=geometry_columns,
                                      default_geometry=default_geometry,
                                      geometries_crs=geometries_crs)

    def load_parquet(self,
                     table_name: str,
                     bucket_name: str = None,
                     geometry_columns=['geometry'],
                     default_geometry=None,
                     lazy_loading=False) -> DuckDBPyRelation | GeoDataFrame:

        s3_path = self._get_s3_path_for(table_name)
        print(f'Gerando query para o arquivo {s3_path}...')
        rel = self.connection.read_parquet(s3_path)
        print('Query gerada:')
        print(rel.sql_query())
        if lazy_loading:
            return rel
        geometries_crs = self._get_geometry_columns_crs(s3_path,
                                                  geometry_columns)
        gdf = self.duckdb_relation_to_gdf(relation=rel,
                                          geometry_columns=geometry_columns,
                                          default_geometry=default_geometry,
                                          geometries_crs=geometries_crs)
        return gdf
