from geopandas import GeoDataFrame
from pandas import concat


def sjoin_largest(
    left_gdf: GeoDataFrame,
    right_gdf: GeoDataFrame,
    id_columns: str | list[str],
    left_geometry: str = 'geometry',
    right_geometry: str = 'geometry',
    try_covered_by: bool = True,
    keep_right_geometry: bool = False,
    keep_intersection_geometry: bool = False
) -> GeoDataFrame:

    assert isinstance(
        left_gdf, GeoDataFrame), 'left_gdf precisa ser um geopandas.GeoDataFrame'
    assert isinstance(
        right_gdf, GeoDataFrame), 'right_gdf precisa ser um geopandas.GeoDataFrame'

    if isinstance(id_columns, str):
        id_columns = [id_columns]

    assert isinstance(id_columns, list),\
        'É preciso informar ao menos uma coluna de identificação'

    assert len(id_columns) > 0,\
        'É preciso informar ao menos uma coluna de identificação'

    intersect = left_gdf.copy()
    left_copy = left_gdf.copy().set_geometry(left_geometry)
    right_copy = right_gdf.copy().set_geometry(right_geometry)
    # Renomeio as colunas da direita em caso de overlapping de colunas
    mapper = {
        col: f'right_{col}' for col in right_copy.columns if col in left_copy.columns
    }
    # Mantenho o nome da geometria da direita mesmo que seja igual à da esquerda
    mapper = {
        k: v for k, v in mapper.items() if k != right_geometry
    }
    right_copy = right_copy.rename(columns=mapper)
    # Crio uma nova coluna de geometria no camada
    right_copy.loc[:, 'right_geometry'] = right_copy.loc[:, right_geometry]

    not_covered = left_copy.shape[0]

    if try_covered_by == True:
        covered = left_copy.sjoin(
            right_copy, how='left', predicate='covered_by')
        covered.loc[:, 'intersection_pct'] = 1

        not_covered_filter = covered['index_right'].isna()
        not_covered = not_covered_filter.sum()

        if not_covered == 0:
            return covered.sort_index()

        intersect = covered[not_covered_filter].copy()
        intersect = intersect[left_copy.columns]

    intersect = intersect.sjoin(right_copy, how='left', predicate='intersects')

    # Crio uma nova coluna com o polígono da interseção entre o setor e o camada
    # e calculo o percentual de interseção
    intersect.loc[:, 'intersection'] = \
            intersect.loc[:,left_geometry].intersection(intersect.loc[:, 'right_geometry'])
    intersect.loc[:, 'intersection_pct'] = \
            intersect.loc[:, 'intersection'].area/intersect.loc[:, left_geometry].area
    intersect  = intersect.drop(columns='intersection')

    # Ordeno pelo identificador dos registros e percentual de interseção
    intersect = intersect.sort_values(
        id_columns + ['intersection_pct'], ascending=[True] * len(id_columns) + [False])

    # Mantenho apenas as features com maior percentual de interseção
    largest = intersect.drop_duplicates(id_columns, keep='first')

    # Filtro o dataframe apenas para as colunas de identificação
    _id_columns = id_columns.copy()
    _id_columns.append('index_right')

    largest = largest[_id_columns]

    # Transfiro o index para uma coluna para não perdê-lo
    intersect = intersect.reset_index(names='intersect_index')
    # Trago os outros dados do dataframe de interseção
    intersect = intersect.merge(largest, how='right', left_on=_id_columns, right_on=_id_columns)
    # Defino o index como o index anterior
    intersect = intersect.set_index('intersect_index')
    intersect = intersect.rename_axis(index=None)

    assert intersect.shape[0] == not_covered,\
        'O número de registros no dataframe baseado na maior interseção não é igual ao número de registros não cobertos por uma feature'

    final_gdf = intersect.copy()

    if try_covered_by == True:
        # Por último, crio um novo gdf concatenando os dois tipos de sjoin
        final_gdf = concat([covered[~not_covered_filter], intersect])

    assert final_gdf.shape[0] >= left_gdf.shape[0],\
        'O número de registros no dataframe final é menor do que o número de registros do dataframe original'
    
    if keep_right_geometry==False:
        final_gdf.drop(columns='right_geometry', inplace=True)
    if keep_right_geometry==False:
        final_gdf.drop(columns='intersection', inplace=True)

    return final_gdf.sort_index()
