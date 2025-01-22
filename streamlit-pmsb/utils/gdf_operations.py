import geopandas as gpd
import pandas as pd
from os.path import join
from os import makedirs


# Dados
def get_dados(dado:str):
    if dado == 'distrito':
        distrito = gpd.read_file(join("data", "2024_11_26", "03_consumo_distrito"))
        return distrito
    elif dado == 'subbac':
        subbac = gpd.read_file(join("data", "2024_11_26", "03_consumo_subbac"))
        return subbac
    elif dado == 'subpref':
        subpref = gpd.read_file(join("data", "2024_11_26", "03_consumo_subprefeitura"))
        return subpref
    elif dado == 'fcu':
        fcu = gpd.read_file(join("data", "2024_11_26", "pop_fcu"))
        return fcu

def find_distrito_name(gdf, prefix:str):
    gdf_columns=gdf.columns
    for column in gdf_columns:
        if column.startswith(prefix):
            if column.endswith('distrit'):
                return column


def create_gdf_sorted(
    gdf, 
    name_gdf, 
    isIntersec:bool=False
):
    
    gdf_sorted = gpd.GeoDataFrame()
    gdf_columns=gdf.columns
    
    if name_gdf == 'subbac':
        gdf_sorted[['cd_subbac', 'nm_subbac']] = (
            gdf[['cd_identif', 'nome_bacia_h']]
        )
    
    else:
        if name_gdf == 'distrito':
            distrito_cd = find_distrito_name(gdf, 'cd_')
            distrito_nm = find_distrito_name(gdf, 'nm_')
            gdf_sorted[distrito_cd]=gdf[distrito_cd]
            gdf_sorted[distrito_nm]=gdf[distrito_nm]
        #return gdf_sorted.columns
        
        else:
            for column in gdf_columns:
                if column == f'cd_{name_gdf}' or column== f'nm_{name_gdf}':
                    gdf_sorted[column] = gdf[column] 
    
    if isIntersec:
        gdf_sorted['geometry'] = gdf['geometry']
    else:
        
        for column in gdf_columns:
            if column.startswith((
                'pop', 
                'dom', 
                'con', 
                'desidade', 
                'geometry'
            )):
                gdf_sorted[column] = gdf[column]
    
    gdf_sorted = gdf_sorted.set_geometry('geometry')

    return gdf_sorted

def overlay_intersec(gdf_intersec, name_gdf_intersec, gdf_unidade, cd_unidade):
    gdf_intersec = create_gdf_sorted(
        gdf_intersec,
        name_gdf_intersec,
        isIntersec=True
    )

    overlay_unidade_intersec = gpd.overlay(
        gdf_unidade,
        gdf_intersec,
        how='intersection',
        keep_geom_type=True
    )

    overlay_unidade_intersec = (
        overlay_unidade_intersec.explode(
            index_parts=False
        )
    )

    overlay_unidade_intersec['area'] = (
        overlay_unidade_intersec['geometry'].area
    )

    overlay_unidade_intersec = overlay_unidade_intersec.sort_values(
        by='area', 
        ascending=False
    )

    gdf_final_unidade = get_uniques(overlay_unidade_intersec, cd_unidade)

    return gdf_final_unidade

def get_uniques(overlay_unidade_intersec, cd_unidade):

    unique_unidades_overlay = (
        overlay_unidade_intersec[cd_unidade]
        .unique()
        .tolist()
    )

    columns_overlay = overlay_unidade_intersec.columns
    gdf_final_unidade=gpd.GeoDataFrame(columns=columns_overlay)

    row_idx=0

    for u in unique_unidades_overlay:
        gdf_unique = (
            overlay_unidade_intersec[
                overlay_unidade_intersec[cd_unidade] == u
            ].head(1)
        )
        
        for _, linha in gdf_unique.iterrows():
            gdf_final_unidade.loc[row_idx] = linha
            row_idx +=1

    return gdf_final_unidade







#Correct gdfs
def intersec_unidades(
    unidades_df,
    choice_unidade,
    gdf_unidade,
    name_column_unidade
)-> gpd.GeoDataFrame:

    gdf_unidade = create_gdf_sorted(gdf=gdf_unidade, name_gdf=choice_unidade)
    index_unidade = (
        unidades_df[
            unidades_df['name'] == choice_unidade
        ].index[0]
    )
    resultados = []
    gdf_final_unidade = gpd.GeoDataFrame()
    
    for i, row in unidades_df.iterrows():
        if i< index_unidade:
            polenta = overlay_intersec(unidades_df, choice_unidade, gdf_unidade, name_column_unidade)
            return polenta
        



