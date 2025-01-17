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

def create_gdf_sorted(gdf, name_gdf, isIntersec:bool=False):
    gdf_sorted = gpd.GeoDataFrame()
    gdf_columns=gdf.columns
    
    if name_gdf == 'subbac':
        gdf_sorted[['cd_subbac', 'nm_subbac']] = gdf[['cd_identif', 'nome_bacia_h']]
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
        
def overlay_intersec(unidades_df, choice_unidade, gdf_unidade, name_column_unidade):
    name_gdf_intersec= (
        unidades_df[
            unidades_df['name']==choice_unidade
            ]['gdf_name']
            .values[0]
        )
    name_column_intersec= (
        unidades_df[
            unidades_df['name']==choice_unidade
        ]['column_name']
        .values[0]
    )
    gdf_intersec = get_dados(name_gdf_intersec)
    gdf_intersec = create_gdf_sorted(
        gdf_intersec, 
        name_gdf_intersec,
        isIntersec=True
        )

    overlay_unidade = gpd.overlay(
        gdf_unidade,
        gdf_intersec,
        how= 'intersection',
        keep_geom_type=True
    )
    overlay_unidade = (
        overlay_unidade.explode(
            index_parts=False
        )
    )
    overlay_unidade['area'] = overlay_unidade['geometry'].area

    overlay_unidade = (
        overlay_unidade.sort_values(
            by='area', 
            ascending=False
        )
    )

    return overlay_unidade

def get_uniques():
    unique_unidades = (
        overlay_unidade[
            name_column_unidade #trocar pelo cd
        ].unique().tolist()
    )
    
    for u in unique_unidades:
        gdf_unique = (
            overlay_unidade[
                overlay_unidade[
                    name_column_unidade #cd
                ] == u
            ]
        )
        gdf_unique = gdf_unique.head(2)

        gdf_final_unidade[name_column_unidade]=( #cd
            [u]   
        ) 
        for contador, e in enumerate(
            gdf_unique.itertuples()
        ):
            gdf_final_unidade[f'intersec_{name_gdf_intersec}{contador}'] =(
                e.name_column_intersec #cd
            ) 
                
        resultados.append(gdf_final_unidade)
    
    resultados = gpd.GeoDataFrame(
        pd.concat(
            resultados, 
            ignore_index=True
            ), 
        crs="EPSG:31983"
    )
    
    return resultados

