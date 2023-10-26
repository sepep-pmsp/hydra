import base64
from io import BytesIO
from dagster import (
    AssetExecutionContext,
    AssetIn,
    AssetsDefinition,
    MetadataValue,
    Output,
    asset,
)
from geopandas import GeoDataFrame
import matplotlib.pyplot as plt
import seaborn as sns

from ..resources import GeosampaClient
from ..config import GeosampaConfig


def _get_md_preview_plot(gdf: GeoDataFrame, nome_camada: str) -> str:
    # Defino o seaborn theme
    sns.set_theme(rc={'patch.linewidth': 0.1})

    # Ploto o dataframe
    gdf.plot()
    plt.axis('off')
    plt.title(f'Features da camada {nome_camada}')

    # Converto a imagem em um formato decodificável
    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    image_data = base64.b64encode(buffer.getvalue())

    # Converto a imagem em markdown
    return f"![img](data:image/png;base64,{image_data.decode()})"


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

def __build_digested_asset(name, group_name="geosampa_bronze") -> AssetsDefinition:
    @asset(
        name=f'{name}_digested',
        ins={"raw_asset": AssetIn(key=name)},
        group_name=group_name,
        io_manager_key="bronze_io_manager",
        dagster_type=GeoDataFrame,
    )
    def _asset(
        context: AssetExecutionContext,
        raw_asset: dict
    ):
        context.log.info(f'Lendo a camada {name}')
        gdf = GeoDataFrame.from_features(raw_asset['features'])
        gdf = gdf.set_crs(raw_asset['crs'].get('properties').get('name'))
        gdf = gdf.to_crs(epsg=31983)

        # Recebo a imagem de prévia em markdown
        md_preview = _get_md_preview_plot(gdf, name)

        # Extraio algumas linhas como amostra
        n = 10 if gdf.shape[0] > 10 else gdf.shape[0]

        peek = gdf.drop(columns=['geometry']).sample(n)

        context.log.info(f'Camada {name} lida')

        return Output(
            gdf,
            metadata={
                'núm. linhas': gdf.shape[0],
                'prévia em gráfico': MetadataValue.md(md_preview),
                f'amostra de {n} linhas': MetadataValue.md(peek.to_markdown()),
            })

    return _asset


globals().update({asset_: __build_raw_asset(asset_)
                  for asset_ in GeosampaConfig.get_asset_config().get('geosampa').keys()})

globals().update({f'{asset_}_digested': __build_digested_asset(asset_)
                  for asset_ in GeosampaConfig.get_asset_config().get('geosampa').keys()})
