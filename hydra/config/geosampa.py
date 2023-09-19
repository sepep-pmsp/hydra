from ..utils.io.files import read_json

class GeosampaConfig:
    
    @staticmethod
    def get_asset_config() -> dict:
        
        asset_config ={
            'geosampa': [dict(name=name_) for name_ in GeosampaConfig._camadas_list()],
        }
            
        return asset_config
    
    @staticmethod
    def _camadas_list() -> list:
        camadas = read_json(file='camadas.json', path='./hydra/config')
        return camadas
