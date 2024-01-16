from extractor import Extractor
import dash_leaflet.express as dlx
from scripts.utils.utils import receber_distrito_aleatorio_em_geodataframe, receber_geobuf_de_geodataframe

class Transformer:

    def __init__(self):
        self.extractor = Extractor()

        self.DAO = self.extractor.configurar_DAO()
        self.package = self.extractor()

    def juntar_colunas (self):
        duckdb_relation = self.package.project('cd_original_setor_censitario, cd_identificador_distrito, geometry')
        
        return duckdb_relation
    
    def filtrar_colunas(self, duckdb_relation, gdf_distrito_aleatorio):
        duckdb_relation = duckdb_relation.filter(f'cd_identificador_distrito == {gdf_distrito_aleatorio["cd_identificador_distrito"].iloc[0]}')

        return duckdb_relation
    
    def transformar_geodataframe(self, duckdb_relation):
        gdf_todos_setores = self.DAO.duckdb_relation_to_gdf(duckdb_relation)
        gdf_todos_setores['tooltip'] = gdf_todos_setores['cd_original_setor_censitario']


        return gdf_todos_setores
    

    def pipeline(self):

        duckdb_relation = self.juntar_colunas()
        gdf_distrito_aleatorio = receber_distrito_aleatorio_em_geodataframe()
        duckdb_relation = self.filtrar_colunas(duckdb_relation)
        gdf_todos_setores = self.transformar_geodataframe(duckdb_relation)

        geobuf_todos_setores = receber_geobuf_de_geodataframe(gdf_todos_setores)

        return geobuf_todos_setores



    def __call__(self):

        return self.pipeline()