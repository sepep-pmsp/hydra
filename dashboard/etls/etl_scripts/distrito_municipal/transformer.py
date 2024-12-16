from ..base_transformer import BaseTransformer
import dash_leaflet.express as dlx


class Transformer(BaseTransformer):
    def __init__(self, get_geobuf:bool = True):
        self.get_geobuf = get_geobuf
        super().__init__('distrito_municipal_digested','nm_distrito_municipal',[
                                               'cd_identificador_distrito',
                                               'cd_distrito_municipal',
                                               'nm_distrito_municipal',
                                               'sg_distrito_municipal',
                                               'geometry'
                                               ], True)

    @staticmethod
    def receber_distrito_aleatorio_em_geojson():
        T = Transformer
        t = T(get_geobuf=False)

        return t
    
    def pipeline(self):

        duckdb_relation = self.filtrar_colunas(self.package)
        geodataframe_todos_distritos = self.transformar_geodataframe(duckdb_relation)
        distrito_aleatorio_json = BaseTransformer.receber_resultado_aleatorio_em_gjson(geodataframe_todos_distritos)


        if self.get_geobuf:
            geobuf_distrito_aleatorio = dlx.geojson_to_geobuf(distrito_aleatorio_json)
            return geobuf_distrito_aleatorio 
        
        return distrito_aleatorio_json
    
    def __call__(self):
        return self.pipeline()

