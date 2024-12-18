from dagster import (
    AssetExecutionContext,
    AssetIn,
    AssetsDefinition,
    MetadataValue,
    Output,
    asset,
)
import numpy as np
from io import StringIO
import pandas as pd

from ...config.censo import (
    CensoConfig,
    CensoFiles,
)
from ...resources import CensoResource
from ...utils.io.files import generate_file_hash, extract_text_file


@asset(
    io_manager_key='bronze_io_manager',
    group_name='censo_2010_bronze',
)
def arquivo_zip_censo(
    context: AssetExecutionContext,
    censo_resource: CensoResource
) -> bytes:
    context.log.info(
        f'Baixando o arquivo zip de {censo_resource.URL_CENSO_2010}')

    zip_content = censo_resource.download_zipfile()
    zip_hash = generate_file_hash(zip_content)

    context.log.info('Arquivo baixado')

    context.add_output_metadata(
        metadata={
            'SHA256 Hash do arquivo': zip_hash,
        }
    )

    return zip_content


def _build_raw_asset(name: str, groupname: str = 'censo_2010_bronze') -> AssetsDefinition:
    @asset(
        name=name,
        group_name=groupname,
        io_manager_key='bronze_io_manager',
        dagster_type=list[str],
    )
    def _raw_asset(
        context: AssetExecutionContext,
        arquivo_zip_censo: bytes
    ):

        base_path = 'Base informaçoes setores2010 universo SP_Capital/CSV/'
        file_format = '.csv'
        csv_string = extract_text_file(
            zip_content=arquivo_zip_censo,
            base_path=base_path,
            file_name=name,
            file_format=file_format,
            logger=context.log
        )

        n = 5
        peek = csv_string[:n]

        return Output(
            csv_string,
            metadata={
                'número de linhas': len(csv_string),
                f'primeiras {n} linhas': '\n'.join(peek)
            })
    return _raw_asset


@asset(
    io_manager_key='bronze_io_manager',
    ins={'csv_string': AssetIn(key=CensoFiles.BASICO)},
    group_name='censo_2010_bronze',
)
def basico_digest(
    context: AssetExecutionContext,
    csv_string: list[str]
) -> pd.DataFrame:
    context.log.info(f'Carregando o csv {CensoFiles.BASICO}')

    # A primeira linha do csv veio com um separador sobrando no final da
    # linha de cabeçalho. Primeiro removo o último ';' apenas dessa linha
    csv_string[0] = csv_string[0].rstrip(';')

    dtypes = {
        'Cod_setor': object,
        'Cod_Grandes Regiões': object,
        'Nome_Grande_Regiao': object,
        'Cod_UF': object,
        'Nome_da_UF': object,
        'Cod_meso': object,
        'Nome_da_meso': object,
        'Cod_micro': object,
        'Nome_da_micro': object,
        'Cod_RM': object,
        'Nome_da_RM': object,
        'Cod_municipio': object,
        'Nome_do_municipio': object,
        'Cod_distrito': object,
        'Nome_do_distrito': object,
        'Cod_subdistrito': object,
        'Nome_do_subdistrito': object,
        'Cod_bairro': object,
        'Nome_do_bairro': object,
        'Situacao_setor': int,
        'Tipo_setor': int,
    }

    df = pd.read_csv(
        StringIO('\n'.join(csv_string)),
        sep=';',
        decimal=',',
        dtype=dtypes
    )

    n = 10

    context.add_output_metadata(
        metadata={
            'registros': df.shape[0],
            f'amostra de {n} linhas': MetadataValue.md(df.sample(n).to_markdown()),
        }
    )

    return df


@asset(
    io_manager_key='bronze_io_manager',
    ins={'csv_string': AssetIn(key=CensoFiles.DOMICILIO_01)},
    group_name='censo_2010_bronze',
)
def domicilio01_digest(
    context: AssetExecutionContext,
    csv_string: list[str]
) -> pd.DataFrame:
    context.log.info(f'Carregando o csv {CensoFiles.DOMICILIO_01}')

    # A primeira linha do csv veio com um separador sobrando no final da
    # linha de cabeçalho. Primeiro removo o último ';' apenas dessa linha
    csv_string[0] = csv_string[0].rstrip(';')

    dtypes = {
        'Cod_setor': object,
        'Situacao_setor': int,
    }

    df = pd.read_csv(
        StringIO('\n'.join(csv_string)),
        sep=';',
        decimal=',',
        dtype=dtypes
    )

    # Esses arquivos possuem uma supressão de valores com a letra X
    # A página 36 do arquivo BASE DE INFORMAÇÕES POR SETOR CENSTÁRIO explica em mais detalhes
    # Por isso, precisamos tratar esses dados, que deveriam ser números inteiros
    # Nesse momento, apenas substituo por valores nulos para facilitar o armazenamento posterior
    df.replace('X', np.nan, inplace=True)
    # Também substituo ',' por '.', para casos de números decimais
    df.replace(',', '.', inplace=True)

    # Por último, converto as colunas de variáveis do Censo (nomeadas V###) em float64, devido aos nulos
    variable_columns = [col for col in df.columns if col.startswith('V')]
    float_dtypes = {col: 'float64' for col in variable_columns}
    dtypes.update(float_dtypes)
    df = df.astype(dtypes)

    n = 10

    context.add_output_metadata(
        metadata={
            'registros': df.shape[0],
            f'amostra de {n} linhas': MetadataValue.md(df.sample(n).to_markdown()),
        }
    )

    return df


globals().update({_asset.get('name'): _build_raw_asset(_asset.get('name'))
                  for _asset in CensoConfig.get_asset_config().get('censo')})
