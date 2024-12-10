from dagster import ConfigurableResource
import requests


class CensoResource(ConfigurableResource):
    URL_CENSO_2010:str = 'https://ftp.ibge.gov.br/Censos/Censo_Demografico_2010/Resultados_do_Universo/Agregados_por_Setores_Censitarios/SP_Capital_20231030.zip'
    BASEURL_CENSO_2022:str = 'https://ftp.ibge.gov.br/Censos/Censo_Demografico_2022/Agregados_por_Setores_Censitarios/Agregados_por_Setor_csv/Agregados_por_setores_'

    def download_zipfile(self, censo_year:str = "2010") -> bytes:
        if censo_year == "2010":
            r = requests.get(self.URL_CENSO_2010)
            zip_content = r.content
            return zip_content
        