from dagster import (
    AssetExecutionContext,
    AssetIn,
    AssetOut,
    MetadataValue,
    Output,
    asset,
    multi_asset,
)  # import the `dagster` library
import geopandas as gpd
import pandas as pd

from hydra.config.censo import (
    CensoConfig,
    CensoFiles,
)

def get_log_masssages_setor_censitario(df: gpd.GeoDataFrame) -> str:
    df = df.copy()
    assert 'missing' in df.columns
    assert 'supressed' in df.columns

    logs = []
    total_registros = df.shape[0]
    logs.append(f'Total de registros depois do merge: {total_registros}')

    total_missing = df[df['missing'] == True].shape[0]
    logs.append(f'Total de missings no merge: {total_missing}')
    logs.append(f'Percentual de missings depois do merge: {total_missing/total_registros:.2%}')

    total_supress = df[df['supressed'] == True].shape[0]
    logs.append( f'Total de suprimidos depois do merge: {total_supress}')
    logs.append(f'Percentual de suprimidos depois do merge: {total_supress/total_registros:.2%}')

    return '\n'.join(logs)

@asset(
    io_manager_key="gpd_silver_io_manager",
    ins={"df_censo": AssetIn(key='domicilio01_digest')},
    group_name="silver",
)
def setor_censitario_enriched(
    context: AssetExecutionContext,
    df_censo: pd.DataFrame,
    setor_censitario_2010: gpd.GeoDataFrame
) -> gpd.GeoDataFrame:
    context.log.info(f'Carregando os dados de {CensoFiles.DOMICILIO_01}')

    # Primeiro confiro se o tipo das duas colunas de identificação são iguais
    assert setor_censitario_2010['cd_original_setor_censitario'].dtype == df_censo['Cod_setor'].dtype

    # Então filtro as colunas na tabela do censo
    cols = CensoConfig.get_columns_for_file(CensoFiles.DOMICILIO_01)

    df_censo = df_censo[list(cols.keys())]

    # Renomeio as colunas para evitar duplicidade
    df_censo = df_censo.rename(columns=cols)

    # Faço o merge
    df_setor_enriched = setor_censitario_2010.merge(
        df_censo,
        how='left',
        left_on='cd_original_setor_censitario',
        right_on='Cod_setor'
    )

    context.log.info(
        f'Total de registros antes do merge: {setor_censitario_2010.shape[0]}'
    )

    # Crio as colunas de missing e supressed

    df_setor_enriched['missing'] = df_setor_enriched['Cod_setor'].isna()
    df_setor_enriched['supressed'] = (df_setor_enriched['missing']==False) & (df_setor_enriched[CensoFiles.DOMICILIO_01 + '_V012'].isna())

    # Exibo as informações no log

    context.log.info(
        get_log_masssages_setor_censitario(df_setor_enriched)
    )

    n = 10

    peek = df_setor_enriched.drop(columns=['geometry']).sample(n)

    context.add_output_metadata(
        metadata={
            'registros': df_setor_enriched.shape[0],
            f'amostra de {n} linhas': MetadataValue.md(peek.to_markdown()),
        }
    )

    return df_setor_enriched
