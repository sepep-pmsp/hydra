#mudar nome para operations_gdf

import geopandas as gpd
import pandas as pd
from os.path import join, exists
from os import makedirs
from utils import functions

DATA_DATE = "2024_11_26"
PATH_ORIGINAL= join("data", DATA_DATE)
SUBPATH_DISTRITO= "03_consumo_distrito"
SUBPATH_SUBBAC= "03_consumo_subbac"
SUBPATH_SUBPREF= "03_consumo_subprefeitura"
SUBPATH_FCU= "pop_fcu"




# Dados
#lista unidades
def listing_unidades(subbac_gdf):
    cd_subbac = find_gdf_name(subbac_gdf, 'subbac', 'cd_')
    nm_subbac = find_gdf_name(subbac_gdf, 'subbac','nm_')

    unidades_list = [
        ('subbac', "Sub Bacias Hidrográficas", cd_subbac, nm_subbac, 'tata'),
        ('subpref', "Subprefeituras", "cd_subpref" , 'nm_subpref', 'tete'),
        ('distrito', "Distritos", 'cd_distrit', 'nm_distrit', 'titi'),
        ('fcu', "Favelas e Comunidades Urbanas", 'cd_fcu', 'nm_fcu', 'tutu')
        
    ]
    unidades_df = pd.DataFrame(unidades_list, columns=[
        'gdf_name', 
        'name', 
        'column_cd', 
        'column_name', 
        'teste'])
    return unidades_df

def get_dados(dado:str):
    if dado == 'distrito':
        distrito = gpd.read_file(join(PATH_ORIGINAL, SUBPATH_DISTRITO))
        return distrito
    elif dado == 'subbac':
        subbac = gpd.read_file(join(PATH_ORIGINAL, SUBPATH_SUBBAC))
        return subbac
    elif dado == 'subpref':
        subpref = gpd.read_file(join(PATH_ORIGINAL, SUBPATH_SUBPREF))
        return subpref
    elif dado == 'fcu':
        fcu = gpd.read_file(join(PATH_ORIGINAL, SUBPATH_FCU))
        return fcu



def find_distrito_name(gdf, prefix:str): #apagar
    gdf_columns=gdf.columns
    for column in gdf_columns:
        if column.startswith(prefix):
            if column.endswith('distrit'):
                return column

def find_subbac_name(gdf, prefix): #apagar
    if prefix == 'cd_':
        info = find_gdf_name(gdf, 'identif', prefix)
    else:
        if prefix == 'nm_':
            info = find_gdf_name(gdf, 'bacia_h', prefix)

    return info


def find_gdf_name(gdf, gdf_name:str, prefix:str):
    if gdf_name== 'distrito':
        gdf_name = 'distrit'
    else:
        if gdf_name == 'subbac':
            if prefix=='cd_':
                gdf_name='identif'
            else:
                if prefix== 'nm_':
                    gdf_name='bacia_h'

    
    gdf_columns=gdf.columns
    for column in gdf_columns:
        if column.startswith(prefix):
            if column.endswith(gdf_name):
                return column


def create_gdf_sorted(
    gdf, 
    name_gdf, 
    isIntersec:bool=False
):
    
    gdf_sorted = gpd.GeoDataFrame()
    gdf_columns=gdf.columns
    
    if name_gdf == 'subbac':
        cd_subbac = find_subbac_name(gdf, 'cd_')
        nm_subbac = find_subbac_name(gdf, 'nm_')
        gdf_sorted[[cd_subbac, nm_subbac]] = (
            gdf[[cd_subbac, nm_subbac]]
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

def overlay_intersec(name_gdf_intersec, gdf_unidade, name_gdf_unidade):
    
    gdf_intersec= get_dados(name_gdf_intersec)
    cd_unidade = find_gdf_name(gdf_unidade, name_gdf_unidade, 'cd_')
    
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

#Save gdf
def save_intersec(
    gdf:gpd.GeoDataFrame, 
    file_name,
    path=join(PATH_ORIGINAL, 'intersec'),
    **kwargs) -> None:
    
    full_path = join(path, file_name)
    if not exists(path):
        makedirs(path)
    if not exists(full_path): #fazer isso fora do save, antes de fazer o processo todo
        gdf.to_file(full_path, **kwargs)

def intersec_unidades(
    unidades_df,
    gdf_unidade:gpd.GeoDataFrame,
    name_gdf_unidade:str
    
):
    gdf_sorted = create_gdf_sorted(
        gdf_unidade, 
        name_gdf_unidade
    )

    gdf_unidade= gdf_sorted

    name_column_unidade = find_gdf_name(
        gdf_unidade, name_gdf_unidade, 'nm_'
    )
#    name_column_unidade = functions.find_gdf_info(unidades_df, name_gdf_unidade, 'gdf_name', 'column_name')

    index_unidade = (
        unidades_df[
            unidades_df['gdf_name'] == name_gdf_unidade
        ].index[0]
    )

  

    cd_unidade = find_gdf_name(
        gdf_unidade, 
        name_gdf_unidade, 
        'cd_'
    )

    overlay_gdf = gpd.GeoDataFrame()

    for i, row in unidades_df.iterrows():
        if i< index_unidade:
            name_gdf_intersec = row.loc['gdf_name']
            cd_intersec = row.loc['column_cd']
            
            overlay_gdf = overlay_intersec(
                name_gdf_intersec= name_gdf_intersec, 
                gdf_unidade = gdf_unidade, 
                name_gdf_unidade=name_gdf_unidade
            )

            
            gdf_unidade[cd_unidade] = (
                gdf_unidade[cd_unidade].astype(str)
            )
            overlay_gdf[cd_intersec] = (
                overlay_gdf[cd_intersec]
                .astype(int)
                .astype(str)
            )
            overlay_gdf[cd_unidade] = (
                overlay_gdf[cd_unidade].astype(str)
            )

    


            gdf_unidade = pd.merge(
                gdf_unidade, 
                overlay_gdf[[cd_unidade, cd_intersec]], 
                on=cd_unidade, 
                how='left'
            )

    
    save_intersec(gdf_unidade, name_gdf_unidade)

    return gdf_unidade
            

        



