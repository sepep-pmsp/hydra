from dagster import ConfigurableResource
import requests
import hashlib


class CensoResource(ConfigurableResource):
    URL = 'https://ftp.ibge.gov.br/Censos/Censo_Demografico_2010/Resultados_do_Universo/Agregados_por_Setores_Censitarios/SP_Capital_20190823.zip'

    def download_zipfile(self, return_hash: bool = False) -> bytes:
        r = requests.get(self.URL)
        zip_content = r.content
        if return_hash:
            zip_hash = self._generate_file_hash(zip_content)
            return zip_content, zip_hash
        
        return zip_content

    def _generate_file_hash(self, file_content: bytes) -> str:
        readable_hash = hashlib.sha256(file_content).hexdigest()
        return readable_hash
