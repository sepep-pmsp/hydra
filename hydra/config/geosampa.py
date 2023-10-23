from ..utils.io.files import read_json


class GeosampaConfig:

    @staticmethod
    def get_asset_config() -> dict:

        asset_config = {'geosampa': GeosampaConfig._camadas_dict()}

        return asset_config

    @staticmethod
    def _camadas_dict() -> dict:
        camadas = read_json(file='camadas.json', path='./hydra/config')
        return camadas
