from etl_scripts.base_transformer import Transformer
import json
import dash_leaflet.express as dlx


class Transformer(Transformer):
    def __init__(self, get_geobuf:bool = True):
        self.get_geobuf = get_geobuf
        super().__init__('distrito_municipal_digested','nm_distrito_municipal',[
                                               'cd_identificador_distrito',
                                               'cd_distrito_municipal',
                                               'nm_distrito_municipal',
                                               'sg_distrito_municipal',
                                               'geometry'
                                               ], True)
        

    def receber_geobuf_de_json (json):
        geojson = json
        geobuf = dlx.geojson_to_geobuf(geojson)

        return geobuf


    
    def pipeline(self):

        duckdb_relation = self.filtrar_colunas(self.package)
        geodataframe_todos_distritos = self.transformar_geodataframe(duckdb_relation)
        distrito_aleatorio_json = self.receber_resultado_aleatorio_em_gjson(geodataframe_todos_distritos)
        geobuf_distrito_aleatorio = self.receber_geobuf_de_json(distrito_aleatorio_json)


        if self.get_geobuf:
            return geobuf_distrito_aleatorio 
        
        return distrito_aleatorio_json
    
    def __call__(self):
        return self.pipeline()
