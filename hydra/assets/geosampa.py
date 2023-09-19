from dagster import (
    AssetExecutionContext,
    AssetOut,
    Output,
    multi_asset,
)  # import the `dagster` library

from ..resources import GeosampaClient

from ..utils.io.files import read_json

CAMADAS = read_json(file='camadas.json', path='./hydra')


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
    outs={out: default_geosampa_bronze() for out in CAMADAS},
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
