from scripts.base_extractor import Extractor
import dash_leaflet.express as dlx
import json

class Transformer:

    def __init__(self, nome_da_camada:str,tooltip_text:str, colunas:list[str] = [], lazy_loading:bool = True, ):
        self.extractor = Extractor(nome_da_camada, lazy_loading= lazy_loading)
        self.tooltip_text = tooltip_text
        self.colunas_selecionadas = colunas

        self.DAO = self.extractor.configurar_DAO()
        self.package = self.extractor()






    def transformar_geodataframe(self, duckdb_relation):
        if len(self.colunas_selecionadas):
            duckdb_relation.select(', '.join(self.colunas_selecionadas))
        gdf = self.DAO.duckdb_relation_to_gdf(duckdb_relation)
        gdf['tooltip'] = gdf[self.tooltip_text]
            



        return gdf

    def receber_geobuf_de_geodataframe (gdf):

        geojson = json.loads(gdf.to_json())
        
        geobuf = dlx.geojson_to_geobuf(geojson)

        return geobuf
    
    
