from dagster import (
    AssetExecutionContext,
    AssetIn,
    AssetsDefinition,
    MetadataValue,
    Output,
    asset,
)
from io import StringIO
import pandas as pd
from pandas import DataFrame


from ...config.censo import (
    Censo2022Config,
    Censo2022Files,
)
from ...resources import CensoResource
from ...utils.io.files import generate_file_hash, extract_text_file


def _build_zip_asset(
        name: str,
        groupname: str = 'censo_2022_bronze') -> AssetsDefinition:
    @asset(
        name=f'{name}_zip',
        io_manager_key='bronze_io_manager',
        group_name='censo_2022_bronze'
    )
    def _zip_asset(
        context: AssetExecutionContext,
        censo_resource: CensoResource
    ) -> bytes:

        context.log.info(
            'Baixando o arquivo zip de '
            f'{censo_resource.BASEURL_CENSO_2022}{name}.zip')

        zip_content = censo_resource.download_zipfile(
            censo_year="2022", file=name)
        zip_hash = generate_file_hash(zip_content)

        context.log.info('Arquivo baixado')

        context.add_output_metadata(
            metadata={
                'SHA256 Hash do arquivo': zip_hash,
            }
        )

        return zip_content
    return _zip_asset


def _build_raw_asset(name: str,
                     groupname: str = 'censo_2022_bronze') -> AssetsDefinition:
    @asset(
        name=name,
        group_name=groupname,
        io_manager_key='bronze_io_manager',
        ins={
            'arquivo_zip_censo': AssetIn(key=f'{name}_zip')
        },
        dagster_type=list[str],
    )
    def _raw_asset(
        context: AssetExecutionContext,
        arquivo_zip_censo: bytes
    ):

        base_path = 'Agregados_por_setores_'
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


def _open_and_filter_csv(
        file_name: str,
        csv_string: list[str],
        context: AssetExecutionContext,
        cd_setor: list[str] = None,
        cd_mun: str = None,
) -> DataFrame:
    context.log.info(f'Carregando o csv {file_name}')

    columns = Censo2022Config.get_columns_for_file(file_name)
    dtypes = {col: object for col in columns}
    chunksize = 5000

    df = pd.DataFrame()

    for chunk in pd.read_csv(StringIO('\n'.join(csv_string)),
                             sep=';',
                             dtype=dtypes,
                             chunksize=chunksize):
        if cd_mun:
            chunk = chunk[chunk['CD_MUN'] == cd_mun]

        if cd_setor:
            chunk = chunk[chunk['CD_setor'].isin(cd_setor)]

        if df.empty:
            df = chunk
        else:
            df = pd.concat([df, chunk])

    n = 10

    metadata = {
        'registros': df.shape[0],
        f'amostra de {n} linhas': MetadataValue.md(df.sample(n).to_markdown()),
    }

    context.add_output_metadata(
        metadata=metadata
    )

    return df


@asset(
    io_manager_key='bronze_io_manager',
    group_name='censo_2022_bronze',
)
def basico_BR_digested(
        context: AssetExecutionContext,
        basico_BR: list[str]) -> DataFrame:

    df = _open_and_filter_csv(
        file_name=Censo2022Files.BASICO,
        csv_string=basico_BR,
        context=context,
        cd_mun='3550308'
    )

    return df


@asset(
    io_manager_key='bronze_io_manager',
    group_name='censo_2022_bronze',
)
def cd_setores_sp(basico_BR_digested: DataFrame) -> list[str]:

    cd_setores_sp = basico_BR_digested['CD_SETOR'].unique().tolist()

    return cd_setores_sp


def _build_digested_asset(
        name: str,
        group_name: str = 'censo_2022_bronze') -> AssetsDefinition:
    @asset(
        name=f'{name}_digested',
        io_manager_key='bronze_io_manager',
        ins={'csv_string': AssetIn(key=name)},
        group_name='censo_2022_bronze',
    )
    def _digested_asset(
            context: AssetExecutionContext,
            csv_string: list[str],
            cd_setores_sp: list[str]) -> DataFrame:

        df = _open_and_filter_csv(
            file_name=name,
            csv_string=csv_string,
            context=context,
            cd_setor=cd_setores_sp
        )

        return df
    return _digested_asset


assets = {}

for file in Censo2022Config._censo_file_list():
    assets.update(
        {
            f'{file}_zip': _build_zip_asset(file),
            f'{file}_raw': _build_raw_asset(file),
        }
    )
    
    if file != Censo2022Files.BASICO:
        assets.update(
            {
                f'{file}_digested': _build_digested_asset(file),
            }
        )

globals().update(assets)
