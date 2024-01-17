from scripts.base_transformer import Transformer
from utils.utils import receber_distrito_aleatorio_em_geojson as random

class Transformer(Transformer):
    def __init__(self):
        super().__init__('intersection_setor_distrito_municipal','cd_original_setor_censitario',['cd_original_setor_censitario', 'cd_identificador_distrito', 'geometry'], True)

    def filtrar_resultado_por_distrito(self,random_dist,duckdb_relation):
        duckdb_relation = duckdb_relation.filter(f'cd_identificador_distrito == {random_dist["cd_identificador_distrito"].iloc[0]}')

        return duckdb_relation
    
    def pipeline(self):

        distrito_aleatorio_json = random()
        duckdb_relation = self.filtrar_colunas(self.package)
        duckdb_relation = self.filtrar_resultado_por_distrito(distrito_aleatorio_json,duckdb_relation)
        geodataframe_setores_por_distrito = self.transformar_geodataframe(duckdb_relation)
        geobuf_setores_por_distrito = self.receber_geobuf_de_geodataframe(geodataframe_setores_por_distrito)

        return geobuf_setores_por_distrito
        
        