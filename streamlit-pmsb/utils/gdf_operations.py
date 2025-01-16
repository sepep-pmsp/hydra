import geopandas as gpd
from os.path import join
# Dados
def get_distritos():
    distrito = gpd.read_file(join("data", "2024_11_26", "03_consumo_distrito"))
    return distrito

def get_subbac():
    subbac = gpd.read_file(join("data", "2024_11_26", "03_consumo_subbac"))
    return subbac

def get_subpref():
    subpref = gpd.read_file(join("data", "2024_11_26", "03_consumo_subprefeitura"))
    return subpref

def get_fcu():
    fcu = gpd.read_file(join("data", "2024_11_26", "pop_fcu"))
    return fcu
