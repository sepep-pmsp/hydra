from dagster import (
    AssetExecutionContext,
    AssetIn,
    AssetsDefinition,
    MetadataValue,
    asset,
    Output,
)
import base64
from io import BytesIO
from geopandas import GeoDataFrame
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

from hydra.config.censo import (
    CensoConfig,
    CensoFiles,
)
from hydra.config.geosampa import GeosampaConfig
from hydra.utils.geopandas import sjoin_largest
from hydra.resources import DuckDBS3Resource


def _get_log_masssages_setor_censitario(
        df: GeoDataFrame,
        missing_col: str = 'missing',
        supressed_col: str = 'supressed'
) -> str:
    df = df.copy()
    assert missing_col in df.columns
    assert supressed_col in df.columns

    logs = []
    total_registros = df.shape[0]
    logs.append(f'Total de registros depois do merge: {total_registros}')

    total_missing = df[df[missing_col] == True].shape[0]
    logs.append(f'Total de missings no merge: {total_missing}')
    logs.append(
        f'Percentual de missings depois do merge: {total_missing/total_registros:.2%}')

    total_supress = df[df[supressed_col] == True].shape[0]
    logs.append(f'Total de suprimidos depois do merge: {total_supress}')
    logs.append(
        f'Percentual de suprimidos depois do merge: {total_supress/total_registros:.2%}')

    return '\n'.join(logs)


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


def _fill_na_by_buffer(
        gdf_to_fill: GeoDataFrame,
        columns_to_fill: list[str],
        gdf_fill_from: GeoDataFrame,
        geometry_column: str = 'geometry',
        buffer_size: int = 5
) -> GeoDataFrame:
    new_gdf_to_fill = gdf_to_fill.copy()
    new_gdf_fill_from = gdf_fill_from.copy()

    for i, row in new_gdf_to_fill.iterrows():

        buffer = row[geometry_column].buffer(buffer_size)
        prox = new_gdf_fill_from[geometry_column].intersects(buffer)
        mapper = new_gdf_fill_from[prox][columns_to_fill].mean().to_dict()
        for col, val in mapper.items():
            new_gdf_to_fill.loc[i, col] = val

    return new_gdf_to_fill


def _fill_na_by_nearest_neighbours(
        gdf_to_fill: GeoDataFrame,
        columns_to_fill: list[str],
        gdf_fill_from: GeoDataFrame,
        geometry_column: str = 'geometry',
        neighbours: int = 3
) -> GeoDataFrame:
    new_gdf_to_fill = gdf_to_fill.copy()

    for i, row in new_gdf_to_fill.iterrows():

        new_gdf_fill_from = gdf_fill_from.copy()
        new_gdf_fill_from['dist'] = new_gdf_fill_from.distance(
            row[geometry_column])
        new_gdf_fill_from = new_gdf_fill_from.nsmallest(neighbours, 'dist')

        new_gdf_to_fill.loc[i,
                            columns_to_fill] = new_gdf_fill_from[columns_to_fill].mean()

        na_cells = new_gdf_to_fill.loc[i, columns_to_fill].isna().sum().sum()
        assert na_cells == 0, f'A linha {i} ainda contém {na_cells} células sem dados.'

    return new_gdf_to_fill


@asset(
    io_manager_key='gpd_silver_io_manager',
    ins={'df_censo': AssetIn(key='domicilio01_digest')},
    group_name='silver',
)
def setor_censitario_enriched(
    context: AssetExecutionContext,
    df_censo: pd.DataFrame,
    setor_censitario_2022_digested: GeoDataFrame
) -> GeoDataFrame:
    context.log.info(f'Carregando os dados de {CensoFiles.DOMICILIO_01}')

    # Primeiro confiro se o tipo das duas colunas de identificação são iguais
    assert setor_censitario_2022_digested['cd_original_setor_censitario'].dtype == df_censo['Cod_setor'].dtype

    # Então filtro as colunas na tabela do censo
    cols = CensoConfig.get_columns_for_file(CensoFiles.DOMICILIO_01)

    df_censo = df_censo[list(cols.keys())]

    # Renomeio as colunas para evitar duplicidade
    df_censo = df_censo.rename(columns=cols)

    context.log.info(
        f'Total de registros antes do merge: {setor_censitario_2022_digested.shape[0]}'
    )

    # Dissolvo os registros do geosampa para que o dataset contenha apenas uma linha
    # por setor sensitário de acordo com o código original do censo
    setor_censitario_2022_digested = setor_censitario_2022_digested.dissolve(
        by='cd_original_setor_censitario',
        as_index=False
    )[['cd_original_setor_censitario', 'geometry']]

    # Faço o merge
    df_setor_enriched = setor_censitario_2022_digested.merge(
        df_censo,
        how='left',
        left_on='cd_original_setor_censitario',
        right_on='Cod_setor'
    )

    # Crio as colunas de missing e supressed

    df_setor_enriched['missing'] = df_setor_enriched['Cod_setor'].isna()
    df_setor_enriched['missing'] = df_setor_enriched['missing'].fillna(False)

    df_setor_enriched['supressed'] = (df_setor_enriched['missing'] == False) & (
        df_setor_enriched[CensoFiles.DOMICILIO_01 + '_V012'].isna())
    df_setor_enriched['supressed'] = df_setor_enriched['supressed'].fillna(
        False)

    # Exibo as informações no log

    context.log.info(
        _get_log_masssages_setor_censitario(df_setor_enriched)
    )

    # Preencho os valores suprimidos
    neighbours = 3
    sup_filter = df_setor_enriched['supressed'] == True
    miss_filter = df_setor_enriched['missing'] == True
    sup_cols = list(CensoConfig.get_columns_for_file(
        CensoFiles.DOMICILIO_01, supressed_only=True).values())
    subset_cols = sup_cols.copy()
    subset_cols.append('geometry')

    context.log.info(
        f'Preenchendo os valores suprimidos com base nos {neighbours} vizinhos mais próximos'
    )

    df_setor_enriched.loc[sup_filter, subset_cols] = _fill_na_by_nearest_neighbours(
        gdf_to_fill=df_setor_enriched.loc[sup_filter, subset_cols],
        columns_to_fill=sup_cols,
        gdf_fill_from=df_setor_enriched.loc[(
            ~sup_filter) & (~miss_filter), subset_cols],
        neighbours=neighbours
    )

    context.log.info(
        f'Valores preenchidos. Avaliando se ainda existem valores nulos indevidos'
    )

    na_cells = df_setor_enriched.loc[df_setor_enriched['missing']
                                     == False, sup_cols].isna().sum().sum()

    assert na_cells == 0, f'O dataset ainda contém {na_cells} células sem dados.'

    n = 10

    peek = df_setor_enriched.drop(columns=['geometry']).sample(n)

    context.add_output_metadata(
        metadata={
            'registros': df_setor_enriched.shape[0],
            f'amostra de {n} linhas': MetadataValue.md(peek.to_markdown()),
        }
    )

    return df_setor_enriched


def __build_digested_asset(name, group_name="silver") -> AssetsDefinition:
    @asset(
        name=f'{name}_digested',
        ins={"raw_asset": AssetIn(key=name)},
        group_name=group_name,
        io_manager_key="gpd_silver_io_manager",
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

        context.log.info(f'Camada {name} lida')
        context.log.info(f'Lendo as configurações da camada {name}')
        conf = GeosampaConfig.get_asset_config().get('geosampa').get(name)
        if 'renamed_columns' in conf.keys():
            context.log.info(f'Renomeando as colunas da camada {name}')
            gdf = gdf.rename(columns=conf.get('renamed_columns'))
        else:
            context.log.info(f'A camada {name} não possui colunas a renomear')

        context.log.info(f'Extraindo metadados da camada {name}')

        # Recebo a imagem de prévia em markdown
        md_preview = _get_md_preview_plot(gdf, name)

        # Extraio algumas linhas como amostra
        n = 10 if gdf.shape[0] > 10 else gdf.shape[0]

        peek = gdf.drop(columns=['geometry']).sample(n)

        return Output(
            gdf,
            metadata={
                'núm. linhas': gdf.shape[0],
                'prévia em gráfico': MetadataValue.md(md_preview),
                f'amostra de {n} linhas': MetadataValue.md(peek.to_markdown()),
            })

    return _asset


globals().update({f'{asset_}_digested': __build_digested_asset(asset_)
                  for asset_ in GeosampaConfig.get_asset_config().get('geosampa').keys()})


def __build_intersections_asset(name, group_name="silver") -> AssetsDefinition:
    @asset(
        name=f'intersection_setor_{name}',
        ins={
            'camada': AssetIn(key=f'{name}_digested'),
            'setor': AssetIn(key='setor_censitario_enriched')
        },
        group_name=group_name,
        io_manager_key='gpd_silver_io_manager',
        dagster_type=GeoDataFrame,
    )
    def _asset(
        context: AssetExecutionContext,
        camada: GeoDataFrame,
        setor: GeoDataFrame
    ):
        # Primero removo os setores sem domicílios particulares
        setor = setor[
            setor['missing'] == False]

        # Depois adapto o gdf de setores para minimizar o tamanho
        df_inter = setor[[
            'geometry', 'cd_original_setor_censitario']].copy()
        df_inter['negative_buffer'] = df_inter['geometry'].buffer(-10)
        df_inter = df_inter.set_geometry('negative_buffer')

        context.log.info(
            f'Buscando configurações da camada {name}'
        )
        conf = GeosampaConfig.get_asset_config().get('geosampa').get(name)
        if conf.get('predicate') == 'intersects':
            context.log.info(
                f'Agregando a camada {name}'
            )
            props = conf.get('properties')
            left_geometry = 'geometry'
            right_geometry = 'right_geometry'

            camada = camada[props]
            camada[right_geometry] = camada['geometry']

            df_inter = df_inter.sjoin(
                camada, how='inner', predicate='intersects')

            # Crio uma nova coluna com o polígono da interseção entre o setor e o camada
            # e calculo o percentual de interseção
            df_inter.loc[:, 'intersection'] = \
                df_inter.loc[:, left_geometry].intersection(
                    df_inter.loc[:, right_geometry])
            df_inter.loc[:, 'intersection_pct'] = \
                df_inter.loc[:, 'intersection'].area / \
                df_inter.loc[:, left_geometry].area

        if conf.get('predicate') == 'largest_intersection':
            context.log.info(
                f'Agregando a camada {name}'
            )
            props = conf.get('properties')

            camada = camada[props]

            rows_before_sjoin = df_inter.shape[0]

            df_inter = sjoin_largest(
                df_inter,
                camada,
                'cd_original_setor_censitario',
                left_geometry='geometry',
                right_geometry='geometry',
                try_covered_by=True,
                keep_right_geometry=True,
                keep_intersection_geometry=True
            )

            rows_after_sjoin = df_inter.shape[0]

            assert rows_before_sjoin == rows_after_sjoin, f'A relação entre setores e {name} foi diferente de 1:1'

            na_after_sjoin = df_inter['index_right'].isna().sum()

            assert na_after_sjoin == 0,  f'Existem setores sem nenhuma interseção com a camada {name}'

        df_inter = df_inter.drop(columns=['index_right'])

        n = 10 if df_inter.shape[0] > 10 else df_inter.shape[0]

        hide_cols = [
            'geometry',
            'negative_buffer',
            'intersection',
            'right_geometry',
        ]
        peek = df_inter.drop(columns=hide_cols).sample(n)

        context.add_output_metadata(
            metadata={
                'registros': df_inter.shape[0],
                f'amostra de {n} linhas': MetadataValue.md(peek.to_markdown()),
            }
        )
        return df_inter
    return _asset


globals().update({f'intersection_setor_{asset_}': __build_intersections_asset(asset_)
                  for asset_ in GeosampaConfig.get_asset_config().get('geosampa').keys()
                  if 'id_col' in GeosampaConfig.get_asset_config().get('geosampa').get(asset_).keys()})


# Não é possível definir dinâmicamente uma lista de assets como um parâmetro.
# Cada definição em ins deve corresponder a um upstream asset único e um
# parâmetro único na função que define o asset. Assim, para que a lista possa ser
# gerada dinâmicamente, precisarei definir uma lista de asset keys como string e
# utilizar o parâmetro deps da definição
intersections = [f'intersection_setor_{asset_}'
                 for asset_ in GeosampaConfig.get_asset_config().get('geosampa').keys()
                 if 'id_col' in GeosampaConfig.get_asset_config().get('geosampa').get(asset_).keys()]


@asset(
    deps=intersections + ['setor_censitario_enriched'],
    group_name='silver',
)
def setor_censitario_enriched_geosampa(
    context: AssetExecutionContext,
    duckdb_s3_resource: DuckDBS3Resource
) -> None:
    duckdb_s3_resource.setup()
    # Como as dependências não são gerenciadas pelo IOManager, preciso carregar
    # as dependências individualmente
    rel_setor = duckdb_s3_resource.load_parquet(
        'setor_censitario_enriched', context, ['geometry'])

    # Primero removo os setores sem domicílios particulares
    rel_setor = rel_setor.filter('missing = False')

    left_id_col = 'cd_original_setor_censitario'

    # Depois adapto o gdf de setores para minimizar o tamanho
    setor_keep_columns = f'geometry, {left_id_col}'
    rel_setor = rel_setor.select(setor_keep_columns)

    # Defino a lista de camadas a agregar ao gdf de setores censitários
    schemas_to_add = [
        dep_key for dep_key in context.op_def.ins.keys()
        if dep_key != 'setor_censitario_enriched'
    ]

    # Crio uma variável para receber a relation com os joins
    join_rel = None

    for dep_key in schemas_to_add:
        schema = dep_key.removesuffix('_digested')
        context.log.info(
            f'Agregando a camada {schema}'
        )

        # Carrego o parquet da camada atual
        camada = duckdb_s3_resource.load_parquet(dep_key, context)
        # Defino uma lista de colunas a se descartar
        # TODO: definir a lista de colunas nas configurações
        drop_columns = [
            'geometry',
            'right_geometry',
            'intersection',
            'negative_buffer',
            '__index_level_0__',
        ]
        # Defino a lista de colunas a manter por exclusão com as colunas a descartar
        keep_columns = [
            col for col in camada.columns if col not in drop_columns]

        # Crio a string de seleção e seleciono as colunas
        select_str = ', '.join(keep_columns)
        camada = camada.select(select_str)

        # Defino a lista de colunas a renomear
        # TODO: renomear colunas nos assets anteriores ou resolver ambiguidades
        # (nomes de colunas repetidos) automaticamente
        rename_columns = [
            'intersection_pct',
            'dc_classe',
            'sg_classe',
            'dc_area_especial',
            'nm_bacia',
            'dt_ocorrencia',
            'dc_tipo_ocorrencia',
            'cd_identificador_subprefeitura',
        ]
        # Crio a nova lista de colunas, renomeando as colunas necessárias
        keep_columns = [col if col not in rename_columns
                        else f'{col} AS {dep_key.removeprefix("intersection_setor_")}_{col}'
                        for col in keep_columns]

        keep_columns.remove(left_id_col)

        # Se a variável estiver vazia é a primeira execução, então crio o join com a partir
        # da relation de setor censitário
        if not join_rel:
            join_condition = f'{rel_setor.alias}.{left_id_col} = {camada.alias}.{left_id_col}'

            keep_columns = ['geometry',
                            f'{rel_setor.alias}.{left_id_col}'] + keep_columns

            join_rel = rel_setor.join(
                camada, condition=join_condition, how='left')

        # Caso contrário, já existe algum join anterior, então apenas encadeio um novo join
        # ao join existente
        else:
            join_condition = f'{join_rel.alias}.{left_id_col} = {camada.alias}.{left_id_col}'

            keep_columns = [
                f'{join_rel.alias}.{col}' for col in join_rel.columns] + keep_columns

            join_rel = join_rel.join(
                camada, condition=join_condition, how='left')

        # Depois do join, seleciono as colunas desejadas
        select_str = ', '.join(keep_columns)
        join_rel = join_rel.select(select_str)

    # Depois de todas as iterações, salvo o parquet
    duckdb_s3_resource.save_parquet(join_rel, context, geometry_columns=['geometry'])

    n = 10

    s3_path = duckdb_s3_resource._dao._get_s3_path_for(
        context.asset_key.to_python_identifier())
    peek_sql = f'SELECT * EXCLUDE (geometry) FROM "{s3_path}" USING SAMPLE {n};'
    peek = duckdb_s3_resource._dao.connection.sql(peek_sql).df()

    context.add_output_metadata(
        metadata={
            'registros': join_rel.count(left_id_col).fetchone()[0],
            f'amostra de {n} linhas': MetadataValue.md(peek.to_markdown()),
        }
    )
