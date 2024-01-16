from dashboard.dao import DuckDBDAO
from dashboard.etls.scripts.utils.utils import get_bucket_os

 

class Extractor: 
    def __init__(self):
        self.bucket_os = get_bucket_os()

        print(self.bucket_os)

    def configurar_DAO(self):
        DAO = DuckDBDAO(**self.bucket_os)
        return DAO
    
    def armazenar_parquet(self, DAO):
        
        intersection_setor_censitario = DAO.load_parquet('intersection_setor_distrito_municipal', lazy_loading=True)

        return intersection_setor_censitario
    def pipeline(self):
            DAO = self.configurar_DAO()
            intersection_setor_censitario = self.armazenar_parquet(DAO)
            

            return intersection_setor_censitario
    def __call__(self):

            return self.pipeline()