import pandas as pd  # Add new imports to the top of `assets.py`
from dagster import (
    AssetExecutionContext,
    AssetOut,
    MetadataValue,
    Output,
    asset,
    get_dagster_logger,
    multi_asset,
)  # import the `dagster` library

from .resources import IBGE_api, GeosampaClient


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


# Método auxiliar para criar as definições de assets com valores padrão
def default_geosampa_bronze(**kwargs) -> AssetOut:
    default = dict(
        group_name="geosampa_bronze",
        io_manager_key="bronze_io_manager",
        dagster_type=dict,
        is_required=False
    )
    default.update(kwargs)
    return AssetOut(**default)


@multi_asset(
    outs={
        "distrito_municipal": default_geosampa_bronze(),
        "setor_censitario_2010": default_geosampa_bronze()
    },
    can_subset=True
)
def camadas_geosampa(
    context: AssetExecutionContext,
    geosampa_client: GeosampaClient
):
    for camada in context.selected_output_names:
        yield Output(geosampa_client.get_feature(camada), output_name=camada)
