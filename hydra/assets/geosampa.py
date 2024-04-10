from dagster import (
    AssetExecutionContext,
    AssetKey,
    AssetsDefinition,
    Output,
    asset,
)

from ..resources import GeosampaClient
from ..config import GeosampaConfig
from ..utils.io.hash import generate_hash_from_obj


def __build_raw_asset(name, group_name="geosampa_bronze") -> AssetsDefinition:
    @asset(
        name=name,
        group_name=group_name,
        io_manager_key="bronze_io_manager",
        dagster_type=dict,
        output_required=False,
    )
    def _asset(
        context: AssetExecutionContext,
        geosampa_client: GeosampaClient
    ):
        context.log.info(f'Baixando a camada {name}')
        camada = geosampa_client.get_feature(name)

        context.log.info(f'Camada {name} baixada')

        assert camada["type"] == "FeatureCollection"

        # Para que o checksum funcione conforme esperado, o timestamp de
        # consulta dos dados deve ser removido
        camada_checksum = camada.copy()
        camada_checksum['timeStamp'] = None

        checksum = generate_hash_from_obj(camada_checksum)

        materialization_event = context.instance.get_latest_materialization_event(
            AssetKey([name])
        )

        previous_checksum = None
        if materialization_event != None:
            metadata = materialization_event.asset_materialization.metadata
            if 'SHA256 Hash da camada' in metadata:
                previous_checksum = metadata['SHA256 Hash da camada'].value

        if previous_checksum != None and checksum != previous_checksum:
            context.log.info(f"A camada {name} foi alterada e será atualizada agora.")
            yield Output(
                camada,
                metadata={
                    'núm. features': len(camada['features']),
                    'SHA256 Hash da camada': checksum,
                })
        else:
            context.log.info(f"A camada {name} não foi alterada desde a última atualização.")

    return _asset


globals().update({asset_: __build_raw_asset(asset_)
                  for asset_ in GeosampaConfig.get_asset_config().get('geosampa').keys()})
