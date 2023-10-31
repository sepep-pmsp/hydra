from dagster import ConfigurableResource
import urllib.request as req
import ssl


class CensoResource(ConfigurableResource):
    URL:str = 'https://ftp.ibge.gov.br/Censos/Censo_Demografico_2010/Resultados_do_Universo/Agregados_por_Setores_Censitarios/SP_Capital_20231030.zip'

    def download_zipfile(self) -> bytes:
        # Cria um context inseguro. O risco é de interceptação do conteúdo,
        # o que não é um problema no nosso caso
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS)
        ctx.options |= 0x4
        
        r = req.urlopen(self.URL, context=ctx)
        zip_content = r.read()

        return zip_content
