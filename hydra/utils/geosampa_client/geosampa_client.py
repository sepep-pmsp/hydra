from .base_client import BaseClient
from .build_filter import CQLFilter
from .paginator import Paginator
from .parsers import FeatureMdataParser


class GeoSampaWfs(BaseClient):


    def __init__(self, domain:str, set_schemas:bool=True, verbose:bool=True, auto_paginate:bool=True):

        self.get = BaseClient(domain=domain, verbose=verbose)
        self.parse_features_schemas = FeatureMdataParser()

        self.schemas = self.get_feature_schemas() if set_schemas else None
        self.paginate = Paginator(self.get, self.schemas)

        self.auto_paginate = auto_paginate
    
    def __list_feature_types_raw(self):

        return self.get('DescribeFeatureType')

    def get_feature_schemas(self):

        resp  = self.__list_feature_types_raw()
        return self.parse_features_schemas(resp)

    def __solve_properties(self, query_params, properties:list=None):

         if properties:
            names = ','.join(properties)
            query_params['propertyName']=names

    def __check_feature_exists(self, feature_name:str)->None:

        if self.schemas and feature_name not in self.schemas:
            raise ValueError(f"Feature name {feature_name} doesn't exits")

    def get_feature(self, feature_name:str, properties:list=None, filter:CQLFilter=None, paginate:bool=None,
                    index_col:str=None, **query_params):

        self.__check_feature_exists(feature_name)        
        self.__solve_properties(query_params, properties)
       
        if filter is not None:
            query_params['cql_filter'] = filter()

        resp = self.get('GetFeature', typeName=feature_name, **query_params)

        if paginate or (paginate is None and self.auto_paginate):
            return self.paginate(feature_name, resp, index_col, **query_params)