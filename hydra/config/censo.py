

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
    def get_columns_for_file(file:str, supressed_only:bool=False) -> dict:
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
        original_columns = ['Cod_setor']
        renamed_columns = {col: file + '_' + col for col in columns}

        all_columns = {col: col for col in original_columns}
        all_columns.update(renamed_columns)

        if supressed_only:
            all_columns.pop('Cod_setor')
            
            for col in ['V001', 'V002']:
                if col in all_columns.keys():
                    all_columns.pop(col)

        return  all_columns
    
class CensoFiles:
    _SUFFIX = '_SP1'
    BASICO = f'Basico{_SUFFIX}'
    DOMICILIO_01 = f'Domicilio01{_SUFFIX}'
