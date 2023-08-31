import pandas as pd  # Add new imports to the top of `assets.py`
from dagster import (
    AssetExecutionContext,
    MetadataValue,
    asset,
    get_dagster_logger,
)  # import the `dagster` library

from .resources import IBGE_api


@asset(
    io_manager_key="bronze_io_manager",
)
def ufs(
    context: AssetExecutionContext,
    ibge_api: IBGE_api
) -> list:
    ufs = ibge_api.get_UF().json()

    context.add_output_metadata(
        metadata={
            "registros": len(ufs),
            "JSON": MetadataValue.json(ufs),
        }
    )

    return ufs


@asset(
    io_manager_key="bronze_io_manager",
)
def municipios(
    context: AssetExecutionContext,
    ufs: list,
    ibge_api: IBGE_api
) -> list:
    logger = get_dagster_logger()

    results = []
    for uf in ufs:
        logger.info(f'Loading municipios from {uf["nome"]}')

        municipios = ibge_api.get_municipio(uf['id']).json()

        results = results + municipios

    context.add_output_metadata(
        metadata={
            "registros": len(results),
            "JSON": MetadataValue.json(results[:5]),
        }
    )

    return results


@asset(
    io_manager_key="silver_io_manager",
)
def municipios_silver(
    context: AssetExecutionContext,
    municipios: list
) -> bytes:
    mun_df = pd.DataFrame(municipios)

    mun_df.loc[:, 'uf'] = mun_df.loc[:, 'microrregiao'].apply(
        lambda x: x['mesorregiao']['UF']['id']
    )
    mun_df.loc[:, 'sigla_uf'] = mun_df.loc[:, 'microrregiao'].apply(
        lambda x: x['mesorregiao']['UF']['sigla']
    )

    mun_df.loc[:, 'microrregiao'] = mun_df.loc[:, 'microrregiao'].apply(
        lambda x: x['id']
    )
    mun_df.loc[:, 'regiao-imediata'] = mun_df.loc[:, 'regiao-imediata'].apply(
        lambda x: x['id']
    )

    context.add_output_metadata(
        metadata={
            "registros": mun_df.shape[0],
            "preview": MetadataValue.md(mun_df.sample(10).to_markdown()),
        }
    )

    return mun_df.to_parquet()  # return df and the I/O manager will save it
