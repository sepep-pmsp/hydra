import warnings
from collections import OrderedDict


class FeatureMdataParser:
    '''Parses feature metadata'''

    def parse_property(self, prop:dict)->dict:

        name = prop['name']
        parsed = dict(
            nullable = prop['nillable'],
            dtype = prop['localType']
            )

        return {name : parsed}
    
    def get_cd_identificador(self, prop:dict, cd_col_name:str='cd_identifica')->bool:

        name = prop['name']
        if name.lower().startswith(cd_col_name):
            return True
        return False
    
    def set_cd_identificador(self, properties:dict, prop:dict)->None:

        if self.get_cd_identificador(prop) and \
            not properties.get('id_col'):

            properties['id_col'] = prop['name']

    def parse_feature_schema(self, feat:dict)->dict:

        name = feat['typeName']
        properties = OrderedDict()
        for prop in feat['properties']:
            parsed_prop = self.parse_property(prop)
            properties.update(parsed_prop)

            self.set_cd_identificador(properties, prop)

        parsed ={
            name : properties
        }

        return parsed
    
    def raise_for_no_id(self, parsed_feature:dict)->None:

        for feature_name, mdata in parsed_feature.items():
            if 'id_col' not in mdata:
                warnings.warn(f"Could not identify id col for feature {feature_name}")

    def parse_all_features(self, get_feature_resp:dict)->dict:

        features = get_feature_resp['featureTypes']

        parsed = OrderedDict()
        for feat in features:
            parsed_feat = self.parse_feature_schema(feat)
            parsed.update(parsed_feat)
            self.raise_for_no_id(parsed_feat)
        return parsed

    def __call__(self, get_feature_resp:dict)->dict:

        return self.parse_all_features(get_feature_resp)