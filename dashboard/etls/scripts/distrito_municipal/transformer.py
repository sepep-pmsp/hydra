from extractor import Extractor

class Transformer:

    def __init__(self):
        self.extractor = Extractor()

        self.DAO = self.extractor.configurar_DAO()
        self.package = self.extractor()
