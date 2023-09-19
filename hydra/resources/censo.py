from dagster import ConfigurableResource
import requests


class CensoResource(ConfigurableResource):
    URL = 'https://ftp.ibge.gov.br/Censos/Censo_Demografico_2010/Resultados_do_Universo/Agregados_por_Setores_Censitarios/SP_Capital_20190823.zip'

    def download_zipfile(self) -> bytes:
        r = requests.get(self.URL)
        zip_content = r.content

        return zip_content
