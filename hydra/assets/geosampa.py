import base64
from io import BytesIO
from dagster import (
    AssetExecutionContext,
    AssetOut,
    MetadataValue,
    Output,
    multi_asset,
)  # import the `dagster` library
import geopandas as gpd
import matplotlib.pyplot as plt

from ..resources import GeosampaClient
from ..config import GeosampaConfig

# Função auxiliar para criar as definições de assets com valores padrão
def default_geosampa_bronze(**kwargs) -> AssetOut:
    default = dict(
        group_name="geosampa_bronze",
        io_manager_key="bronze_io_manager",
        dagster_type=gpd.GeoDataFrame,
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
        context.log.info(f'Baixando a camada {nome_camada}')
        camada = geosampa_client.get_feature(nome_camada)

        context.log.info(f'Lendo a camada {nome_camada}')
        gdf = gpd.GeoDataFrame.from_features(camada['features'])
        gdf.plot()
        plt.axis('off')
        plt.title(f'Features da camada {nome_camada}')
        plt.show()

        # Convert the image to a saveable format
        buffer = BytesIO()
        plt.savefig(buffer, format="png")
        image_data = base64.b64encode(buffer.getvalue())

        # Convert the image to Markdown to preview it within Dagster
        md_preview = f"![img](data:image/png;base64,{image_data.decode()})"
        
        context.log.info(f'Camada {nome_camada} lida')
        yield Output(
            gdf,
            output_name=nome_camada,
            metadata={
                'núm. features': len(camada['features']),
                'prévia em gráfico': MetadataValue.md(md_preview)
            })
