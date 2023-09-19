from dagster import (
    AssetExecutionContext,
    AssetOut,
    Output,
    multi_asset,
)  # import the `dagster` library

from ..resources import GeosampaClient
from ..config import GeosampaConfig

# Função auxiliar para criar as definições de assets com valores padrão
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
    outs={asset_.get('name'): default_geosampa_bronze()
          for asset_ in GeosampaConfig.get_asset_config().get('geosampa')},
    can_subset=True
)
def camadas_geosampa(
    context: AssetExecutionContext,
    geosampa_client: GeosampaClient
):
    for nome_camada in context.selected_output_names:
        camada = geosampa_client.get_feature(nome_camada)
        yield Output(
            camada,
            output_name=nome_camada,
            metadata={
                'núm. features': len(camada['features'])
            })
