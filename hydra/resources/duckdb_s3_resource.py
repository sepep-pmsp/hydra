from dagster import (
    ConfigurableResource,
    OpExecutionContext,
)
from duckdb import DuckDBPyRelation
from hydra.dao import DuckDBS3

class DuckDBS3Resource(ConfigurableResource):
    '''
    Resource para salvar os GeoDataFrames como arquivos parquet num bucket S3.

    A princípio, funciona apenas recebendo todas as configurações de acesso (endpoint, access key e secret) nas configurações iniciais.
    Futuramente, pode ser modificado para construir uma sessão com os valores padrão caso não receba os parâmetros.
    '''

    def __init__(
            self,
            bucket_name: str,
            access_key: str,
            secret_key: str,
            endpoint: str,
            db_path: str = None
        ) -> None:
        self.bucket_name = bucket_name
        self.dao = DuckDBS3(
            bucket_name=bucket_name,
            access_key=access_key,
            secret_key=secret_key,
            endpoint=endpoint.removeprefix('http://'),
            db_path=db_path
        )

    def save_parquet(self, context: OpExecutionContext, rel: DuckDBPyRelation, geometry_columns:list[str]=None, **kwargs) -> str:
        table_name = context.upstream_output.asset_key.to_python_identifier()
        
        self.dao.logger = context.log
        s3_path = self.dao.save_parquet(table_name, rel, geometry_columns, **kwargs)

        return s3_path

    def load_parquet(self, context: OpExecutionContext, geometry_columns=None) -> DuckDBPyRelation:
        table_name = context.upstream_output.asset_key.to_python_identifier()
        self.dao.logger = context.log
        
        rel = self.dao.load_parquet(table_name, geometry_columns)
        return rel