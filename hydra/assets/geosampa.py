from dagster import (
    AssetExecutionContext,
    AssetsDefinition,
    Output,
    asset,
)

from ..resources import GeosampaClient
from ..config import GeosampaConfig


def __build_raw_asset(name, group_name="geosampa_bronze") -> AssetsDefinition:
    @asset(
        name=name,
        group_name=group_name,
        io_manager_key="bronze_io_manager",
        dagster_type=dict,
    )
    def _asset(
        context: AssetExecutionContext,
        geosampa_client: GeosampaClient
    ):
        context.log.info(f'Baixando a camada {name}')
        camada = geosampa_client.get_feature(name)

        context.log.info(f'Camada {name} baixada')

        assert camada["type"] == "FeatureCollection"

        return Output(
            camada,
            metadata={
                'núm. features': len(camada['features']),
            })

    return _asset


globals().update({asset_: __build_raw_asset(asset_)
                  for asset_ in GeosampaConfig.get_asset_config().get('geosampa').keys()})
