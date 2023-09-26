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


@asset(
    io_manager_key="silver_io_manager",
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
        f'Total de registros antes do merge: {setor_censitario_2010.shape[0]}')
    context.log.info(
        f'Total de registros depois do merge: {df_setor_enriched.shape[0]}')

    missings = df_setor_enriched['Cod_setor'].isna()
    context.log.info(
        f'Total de missings no merge: {df_setor_enriched[missings].shape[0]}')

    missings_supress = df_setor_enriched[CensoFiles.DOMICILIO_01 + '_V012'].isna()
    context.log.info(
        f'Total de missings + supressão depois do merge: {df_setor_enriched[missings_supress].shape[0]}')

    n = 10

    peek = df_setor_enriched.drop(columns=['geometry']).sample(n)

    context.add_output_metadata(
        metadata={
            'registros': df_setor_enriched.shape[0],
            f'amostra de {n} linhas': MetadataValue.md(peek.to_markdown()),
        }
    )

    return df_setor_enriched
