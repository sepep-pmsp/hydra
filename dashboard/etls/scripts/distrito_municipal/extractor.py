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
        
        rel_distrito = DAO.load_parquet('distrito_municipal_digested', lazy_loading=True)

        return rel_distrito
    def pipeline(self):
            DAO = self.configurar_DAO()
            distritos_relacao = self.armazenar_parquet(DAO)
            

            return distritos_relacao
    def __call__(self):

            return self.pipeline()