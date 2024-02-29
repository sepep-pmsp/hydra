from abc import ABC, abstractmethod
from geopandas import GeoDataFrame

from dao import DuckDBDAO
from utils import gdf_to_geobuf


class BaseService(ABC):
    def __init__(self, nome_da_camada:str, dao:DuckDBDAO):
        self.nome_da_camada = nome_da_camada
        self._dao = dao

    @property
    def dao(self) -> DuckDBDAO:
        return self._dao
    
    @abstractmethod
    def get_geodataframe(self) -> GeoDataFrame:
        """Return a GeoDataFrame with all the itens on the parquet file.
        """

    def get_geobuf(self, **kwargs) -> str:
        """Return a geobuf string of the GeoDataFrame with all the itens on the parquet file.
        """
        return gdf_to_geobuf(self.get_geodataframe(**kwargs))