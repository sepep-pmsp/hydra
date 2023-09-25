

class CensoConfig:
    
    @staticmethod
    def get_asset_config() -> dict:
        
        asset_config ={
            'censo': [dict(name=name_) for name_ in CensoConfig._censo_file_list()],
        }
            
        return asset_config
    
    @staticmethod
    def _censo_file_list() -> list:
        files = [
            CensoFiles.BASICO,
            CensoFiles.DOMICILIO_01
        ]
        return files
    
    @staticmethod
    def get_columns_for_file(file:str) -> list[str]:
        columns = []
        if file == CensoFiles.DOMICILIO_01:
            columns = [
                'V001',
                'V002',
                'V012',
                'V013',
                'V014',
                'V017',
                'V018',
                'V019',
                'V020',
                'V021',
                'V035',
                'V039',
                'V040',
                'V041'
            ]
        return columns
    
class CensoFiles:
    _SUFFIX = '_SP1'
    BASICO = f'Basico{_SUFFIX}'
    DOMICILIO_01 = f'Domicilio01{_SUFFIX}'
