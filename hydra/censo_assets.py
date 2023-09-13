from dagster import (
    AssetExecutionContext,
    AssetIn,
    AssetOut,
    MetadataValue,
    Output,
    asset,
    multi_asset,
)
import requests
from zipfile import ZipFile
from io import BytesIO, StringIO
import pandas as pd

from .config import Config, CensoFiles

# Função auxiliar para criar as definições de assets com valores padrão
@staticmethod
def _default_censo_bronze(**kwargs) -> AssetOut:
    default = dict(
        group_name="censo_bronze",
        io_manager_key="bronze_io_manager",
        dagster_type=str,
        is_required=False
    )
    default.update(kwargs)
    return AssetOut(**default)

@multi_asset(
    outs={asset_.get('name'): _default_censo_bronze() for asset_ in Config.get_asset_config().get('censo')},
    can_subset=True
)
def arquivos_censo(
    context: AssetExecutionContext
):
    url = 'https://ftp.ibge.gov.br/Censos/Censo_Demografico_2010/Resultados_do_Universo/Agregados_por_Setores_Censitarios/SP_Capital_20190823.zip'
    
    context.log.info(f'Baixando o arquivo zip de {url}')
    r = requests.get(url)
    context.log.info('Arquivo baixado')
    zip_file = ZipFile(BytesIO(r.content))

    for nome_arquivo in context.selected_output_names:

        base_path = 'Base informaçoes setores2010 universo SP_Capital/CSV/'
        file_format = '.csv'
        csv_file_path = f'{base_path}{nome_arquivo}{file_format}'

        context.log.info(f'Abrindo o csv {csv_file_path}')
        csv_file = zip_file.open(csv_file_path, 'r')
        csv_string = [line.decode('latin1').strip() for line in csv_file.readlines()]
        context.log.info(f'Arquivo {csv_file_path} lido')
        
        n = 5
        peek = csv_string[:n]
        

        yield Output(
            '\n'.join(csv_string),
            output_name=nome_arquivo,
            metadata={
                f'primeiras {n} linhas': '\n'.join(peek)
            })
        

@asset(
        io_manager_key="bronze_io_manager",
        ins={"csv_string": AssetIn(key=CensoFiles.BASICO)},
        group_name="censo_bronze",
)
def basico_digest (
    context: AssetExecutionContext, 
    csv_string: str
) -> pd.DataFrame:
    context.log.info(f'Carregando o csv {CensoFiles.BASICO}')
    
    df = pd.read_csv(StringIO(csv_string), sep=';', decimal=',')
    
    n = 10

    context.add_output_metadata(
        metadata={
            'registros': df.shape[0],
            f'amostra de {n} linhas': MetadataValue.md(df.sample(n).to_markdown()),
        }
    )

    return df
