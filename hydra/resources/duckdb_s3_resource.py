from dagster import (
    ConfigurableResource,
    OpExecutionContext,
)
from duckdb import DuckDBPyRelation
from pydantic import PrivateAttr
from hydra.dao import DuckDBS3

class DuckDBS3Resource(ConfigurableResource):
    '''
    Resource para salvar os GeoDataFrames como arquivos parquet num bucket S3.

    A princípio, funciona apenas recebendo todas as configurações de acesso (endpoint, access key e secret) nas configurações iniciais.
    Futuramente, pode ser modificado para construir uma sessão com os valores padrão caso não receba os parâmetros.
    '''
    bucket_name: str
    access_key: str
    secret_key: str
    endpoint: str
    db_path: str = None
    _dao:DuckDBS3 = PrivateAttr()

    def setup(self) -> None:
        self._dao = DuckDBS3(
            bucket_name=self.bucket_name,
            access_key=self.access_key,
            secret_key=self.secret_key,
            endpoint=self.endpoint.removeprefix('http://'),
            db_path=self.db_path
        )

    def save_parquet(self, rel: DuckDBPyRelation, context: OpExecutionContext, table_name:str=None, geometry_columns:list[str]=None, **kwargs) -> str:
        table_name = context.asset_key.to_python_identifier() if not table_name else table_name
        
        self._dao.logger = context.log
        s3_path = self._dao.save_parquet(table_name, rel, geometry_columns, **kwargs)

        return s3_path

    def load_parquet(self, table_name:str, context: OpExecutionContext, geometry_columns=None) -> DuckDBPyRelation:
        self._dao.logger = context.log
        
        rel = self._dao.load_parquet(table_name, geometry_columns)
        return rel
