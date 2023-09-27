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
import seaborn as sns

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

def get_md_preview_plot(gdf: gpd.GeoDataFrame, nome_camada:str) -> str:
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
        gdf = gdf.set_crs(camada['crs'].get('properties').get('name'))
        gdf = gdf.to_crs(epsg=31983)
        
        # Recebo a imagem de prévia em markdown
        md_preview = get_md_preview_plot(gdf, nome_camada)
        
        # Extraio algumas linhas como amostra
        n = 10 if gdf.shape[0] > 10 else gdf.shape[0]

        peek = gdf.drop(columns=['geometry']).sample(n)
        
        context.log.info(f'Camada {nome_camada} lida')
        yield Output(
            gdf,
            output_name=nome_camada,
            metadata={
                'núm. features': len(camada['features']),
                'prévia em gráfico': MetadataValue.md(md_preview),
                f'amostra de {n} linhas': MetadataValue.md(peek.to_markdown()),
            })
