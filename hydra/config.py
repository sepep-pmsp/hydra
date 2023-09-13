
class Config:
    
    @staticmethod
    def get_asset_config() -> dict:
        
        asset_config ={
            'censo': [dict(name=name_) for name_ in Config._censo_file_list()],
        }
            
        return asset_config
    
    @staticmethod
    def _censo_file_list() -> list:
        files = [
            'Basico_SP1'
        ]
        return files
    
