from extractor import Extractor
import dash_leaflet.express as dlx
from scripts.utils.utils import receber_distrito_aleatorio_em_geodataframe
import json

class Transformer:

    def __init__(self):
        self.extractor = Extractor()

        self.DAO = self.extractor.configurar_DAO()
        self.package = self.extractor()

    def juntar_colunas (self):
        duckdb_relation = self.package.project(', '.join([
                                               'cd_identificador_distrito',
                                               'cd_distrito_municipal',
                                               'nm_distrito_municipal',
                                               'sg_distrito_municipal',
                                               'geometry'
                                               ]
                                            ))
        
        return duckdb_relation
    
    def transformar_geodataframe(self, duckdb_relation):
        gdf_todos_distritos = self.DAO.duckdb_relation_to_gdf(duckdb_relation)
        gdf_todos_distritos['tooltip'] = gdf_todos_distritos['nm_distrito_municipal']


        return gdf_todos_distritos
    

    def gdf_para_geobuf (self, gdf):

        geojson = json.loads(gdf.to_json())
        
        geobuf = dlx.geojson_to_geobuf(geojson)

        return geobuf
    
    def pipeline(self):

        duckdb_relation = self.juntar_colunas()
        gdf_todos_distritos = self.transformar_geodataframe(duckdb_relation)
        geojson_distrito_aleatorio = receber_distrito_aleatorio_em_geodataframe(gdf_todos_distritos)
        geobuf_distrito_aleatorio = self.gdf_para_geobuf(geojson_distrito_aleatorio)
        geobuf_todos_distritos = self.gdf_para_geobuf(gdf_todos_distritos)

        return [geobuf_todos_distritos, geobuf_distrito_aleatorio]
    def __call__(self):

        return self.pipeline()