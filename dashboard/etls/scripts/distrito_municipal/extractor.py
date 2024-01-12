from  ....dao import DuckDBDAO
from ..utils.utils import get_bucket_os

 

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
        distritos_relacao = armazenar_parquet(DAO)
        

        return DAO, distritos_relacao

def __call__(self):

        return self.pipeline()