import json
import dash_leaflet.express as dlx

from ..base_transformer import BaseTransformer

class Transformer(BaseTransformer):
    def __init__(self, filtro_personalizado:str=None):
        super().__init__('intersection_setor_distrito_municipal','cd_original_setor_censitario',['cd_original_setor_censitario', 'cd_identificador_distrito', 'geometry'], filtro_personalizado, True)

    def filtrar_resultado_por_distrito(self,random_dist,duckdb_relation):
        duckdb_relation = duckdb_relation.filter(f'cd_identificador_distrito == {random_dist["cd_identificador_distrito"].iloc[0]}')

        return duckdb_relation
    
    def pipeline(self):

        duckdb_relation = self.filtrar_colunas(self.package)
        if self.filtro_personalizado:
            duckdb_relation = self.filtrar_personalizado(duckdb_relation)
        geodataframe_setores_por_distrito = self.transformar_geodataframe(duckdb_relation)
        geojson = json.loads(geodataframe_setores_por_distrito.to_json())
        geobuf_setores_por_distrito = dlx.geojson_to_geobuf(geojson)

        return geobuf_setores_por_distrito
        
    def __call__(self):
        return self.pipeline()

