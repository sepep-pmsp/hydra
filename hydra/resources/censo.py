from dagster import ConfigurableResource
import requests

from ..config.censo.censo_2022_config import Censo2022Config, Censo2022Files

class CensoResource(ConfigurableResource):
    URL_CENSO_2010:str = 'https://ftp.ibge.gov.br/Censos/Censo_Demografico_2010/Resultados_do_Universo/Agregados_por_Setores_Censitarios/SP_Capital_20231030.zip'
    BASEURL_CENSO_2022:str = 'https://ftp.ibge.gov.br/Censos/Censo_Demografico_2022/Agregados_por_Setores_Censitarios/Agregados_por_Setor_csv/Agregados_por_setores_'

    def download_zipfile(self, censo_year:str = "2010", file:str=None) -> bytes:
        if censo_year == "2010":
            url = self.URL_CENSO_2010
        if censo_year == '2022':
            # TODO: alterar a lógia para lançar uma mensagem de erro ou exceção
            if file in Censo2022Config._censo_file_list():
                url = f'{self.BASEURL_CENSO_2022}{file}.zip'

        r = requests.get(url)
        zip_content = r.content
        return zip_content
        