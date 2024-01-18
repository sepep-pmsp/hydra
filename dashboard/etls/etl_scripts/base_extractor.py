from dao import DuckDBDAO
from etls.etl_scripts.utils.utils import get_bucket_os

 

class Extractor: 
    def __init__(self, nome_da_camada:str, lazy_loading:bool = True):
        self.lazy_loading= lazy_loading
        self.nome_da_camada = nome_da_camada
        self.bucket_os = get_bucket_os()

        print(self.bucket_os)

    def configurar_DAO(self):
        DAO = DuckDBDAO(**self.bucket_os)
        return DAO
    
    def armazenar_parquet(self, DAO):
        
        parquet = DAO.load_parquet(self.nome_da_camada, lazy_loading=self.lazy_loading)

        return parquet
    def pipeline(self):
            DAO = self.configurar_DAO()
            camada_em_parquet = self.armazenar_parquet(DAO)
            

            return camada_em_parquet
    def __call__(self):

            return self.pipeline()