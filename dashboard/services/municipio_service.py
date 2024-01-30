from geopandas import GeoDataFrame

from dao import DuckDBDAO
from .base_service import BaseService

class MunicipioService(BaseService):
    def __init__(self, dao:DuckDBDAO):

        super().__init__(
            nome_da_camada='distrito_municipal_digested',
            dao=dao
        )

    def get_geodataframe(self) -> GeoDataFrame:
        gdf = self.dao.load_parquet(self.nome_da_camada)
        gdf = gdf.dissolve()
        gdf['tooltip'] = 'Limite municipal'
        
        return gdf[['geometry', 'tooltip']]
    