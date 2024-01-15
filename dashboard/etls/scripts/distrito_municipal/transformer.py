from extractor import Extractor
import dash_leaflet.express as dlx
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
        gdf_distrito = duckdb_relation.duckdb_relation_to_gdf(self.package)
        gdf_distrito['tooltip'] = gdf_distrito['nm_distrito_municipal']


        return gdf_distrito
    

    def distrito_aleatorio_para_geojson(self, gdf_distrito):

        random_dist = gdf_distrito.sample(n=1)
        geojson_distrito = json.loads(random_dist.to_json())

        return geojson_distrito
    
    def gdf_para_geobuf (self, gdf_distrito):
        
        geobuf_distrito = dlx.geojson_to_geobuf(gdf_distrito)

        return geobuf_distrito
    
    def pipeline(self):

        duckdb_relation = self.juntar_colunas()
        gdf_distrito = self.transformar_geodataframe(duckdb_relation)
        geojson_distrito_aleatorio = self.distrito_aleatorio_para_geojson(gdf_distrito)
        geobuf_distrito = self.gdf_para_geobuf()

        return geobuf_distrito
    def __call__(self):

        return self.pipeline()