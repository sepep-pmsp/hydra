from geopandas import GeoDataFrame
from logging import warning

from dao import DuckDBDAO
from services.base_service import BaseService
from utils import duckdb_relation_to_gdf, gdf_to_geobuf

class DistritoService(BaseService):
    def __init__(self, dao:DuckDBDAO):

        super().__init__(
            nome_da_camada='distrito_municipal_digested',
            dao=dao
        )

    def get_geodataframe(self, columns:list[str]=None, filter_expr:str=None, tooltip_column:str=None) -> GeoDataFrame:
        rel = self.dao.load_parquet(self.nome_da_camada, lazy_loading=True)
        columns = columns if columns else []

        if len(columns):
            cols_expr = ', '.join(columns)
            rel = rel.select(cols_expr)
        
        if tooltip_column:
            if len(columns) and tooltip_column not in columns:
                warning(f'A coluna {tooltip_column} não está presente na lista de colunas selecionadas. Caso ela não exista, pode causer um erro ao ler o arquivo.')
            rel = rel.select(f'*, {tooltip_column} AS tooltip')


        if filter:
            rel = rel.filter(filter_expr)

        gdf = duckdb_relation_to_gdf(rel)
        
        return gdf
    
    def find_by_setor(self, codigo_setor:str, format:str='geodataframe', **kwargs) -> GeoDataFrame | str:
        intersection_setor = f'intersection_setor_{self.nome_da_camada}'
        intersection_setor = intersection_setor.removesuffix('_digested')
        rel = self.dao.load_parquet(intersection_setor, geometry_columns=None, lazy_loading=True)
        rel = rel.select('cd_identificador_distrito, cd_original_setor_censitario')
        rel = rel.filter(f'cd_original_setor_censitario == {codigo_setor}')

        gdf = duckdb_relation_to_gdf(rel, geometry_columns=None)
        if gdf.shape[0] < 1:
            print(f'Não foi encontrado um distrito para o setor {codigo_setor}. O código do setor está certo?')

        codigo_distrito = gdf.iloc[0]['cd_identificador_distrito']

        if format not in ['geodataframe', 'geobuf']:
            print(f'Formato {format} inválido! Informe o formato como "geodataframe" ou "geobuf".')
            return None
        
        resp = self.get_geodataframe(filter_expr=f'cd_identificador_distrito == {codigo_distrito}', **kwargs)
        if format=='geobuf':
            resp = gdf_to_geobuf(resp)
        
        return resp
        
