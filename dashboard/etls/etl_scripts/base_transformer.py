from duckdb import DuckDBPyRelation
from .base_extractor import Extractor
import json

class BaseTransformer:

    def __init__(
            self,
            nome_da_camada:str,
            tooltip_text:str,
            colunas:list[str] = [],
            filtro_personalizado:str = None,
            lazy_loading:bool = True,
            ):
        self.extractor = Extractor(nome_da_camada, lazy_loading= lazy_loading)
        self.tooltip_text = tooltip_text
        self.colunas_selecionadas = colunas
        self.filtro_personalizado = filtro_personalizado

        self.DAO = self.extractor.dao
        self.package = self.extractor()

    @staticmethod
    def receber_resultado_aleatorio_em_gjson(t):
        random = t.sample(n=1)
        random_gjsn = json.loads(random.to_json())

        return random_gjsn
    
    def filtrar_colunas(self,duckdb_relation):
        if len(self.colunas_selecionadas):
           duckdb_relation = duckdb_relation.select(', '.join(self.colunas_selecionadas))
           return duckdb_relation
    
    def filtrar_personalizado(
            self,
            duckdb_relation:DuckDBPyRelation
    ) -> DuckDBPyRelation:
        return duckdb_relation.filter(self.filtro_personalizado)
        

    def transformar_geodataframe(self, duckdb_relation):
        gdf = self.DAO.duckdb_relation_to_gdf(duckdb_relation)
        gdf['tooltip'] = gdf[self.tooltip_text]
            
        return gdf
