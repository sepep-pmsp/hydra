from dagster import ConfigurableResource
import requests
from requests import Response

class IBGE_api(ConfigurableResource):
    base_url: str = 'http://servicodados.ibge.gov.br/api/v1/'

    def __request(self, endpoint: str) -> Response:
        
        return requests.get(
            f'{self.base_url}{endpoint}',
            # headers={'user-agent': 'dagster',},
            )
    
    def get_UF(self):
        return self.__request('localidades/estados')
    
    def get_municipio(self, uf: int):
        return self.__request(f'localidades/estados/{uf}/municipios')
