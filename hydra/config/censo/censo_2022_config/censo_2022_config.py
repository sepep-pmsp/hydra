from .censo_2022_files import Censo2022Files


class Censo2022Config:
    
    @staticmethod
    def get_asset_config() -> dict:
        
        asset_config ={
            'censo': [dict(name=name_) for name_ in Censo2022Config._censo_file_list()],
        }
            
        return asset_config
    
    @staticmethod
    def _censo_file_list() -> list:
        files = [
            Censo2022Files.BASICO,
            Censo2022Files.DOMICILIO_1,
            Censo2022Files.DOMICILIO_2,
        ]
        return files
    
    @staticmethod
    def get_columns_for_file(file:str, supressed_only:bool=False) -> dict:
        if file == Censo2022Files.BASICO:
            columns = [
                'v0001',
                'v0002',
                'v0003',
                'v0004',
                'v0005',
                'v0006',
                'v0007'
            ]
        if file == Censo2022Files.DOMICILIO_1:
            columns = [
                'V00001',
                'V00002',
                'V00003'
            ]
        
        if file == Censo2022Files.DOMICILIO_2:
            columns = [
                'V00111',
                'V00112',
                'V00113',
                'V00114',
                'V00115',
                'V00116',
                'V00117',
                'V00118',
                'V00199',
                'V00200',
                'V00201',
                'V00309',
                'V00310',
                'V00311',
                'V00312',
                'V00313',
                'V00314',
                'V00315',
                'V00316'
            ]
        original_columns = [
                'CD_setor',
                'CD_SETOR',
                'SITUACAO',
                'CD_SIT',
                'CD_TIPO',
                'AREA_KM2',
                'CD_REGIAO',
                'NM_REGIAO',
                'CD_UF',
                'NM_UF',
                'CD_MUN',
                'NM_MUN',
                'CD_DIST',
                'NM_DIST',
                'CD_SUBDIST',
                'NM_SUBDIST',
                'CD_BAIRRO',
                'NM_BAIRRO',
                'CD_NU',
                'NM_NU',
                'CD_FCU',
                'NM_FCU',
                'CD_AGLOM',
                'NM_AGLOM',
                'CD_RGINT',
                'NM_RGINT',
                'CD_RGI',
                'NM_RGI',
                'CD_CONCURB',
                'NM_CONCURB'
            ]
        renamed_columns = {col: file + '_' + col for col in columns}

        all_columns = {col: col for col in original_columns}
        all_columns.update(renamed_columns)

        if supressed_only:            
            for col in original_columns:
                if col in all_columns.keys():
                    all_columns.pop(col)

        return  all_columns
