

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
    
class CensoFiles:
    _SUFFIX = '_SP1'
    BASICO = f'Basico{_SUFFIX}'
    DOMICILIO_01 = f'Domicilio01{_SUFFIX}'
