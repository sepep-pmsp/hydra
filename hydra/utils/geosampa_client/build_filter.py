from typing import Union


class CQLFilter:
    '''Builds a CQL filter for querying the WFS server'''
    
    def __init__(self, feature_name:str, schema:dict)->None:
        
        self.feature_name = feature_name
        self.schema = schema[feature_name]
        self.cql_filter = ''
        
    def add_to_filter(self, query_str:str, sep:str=';')->None:
        
        if len(self.cql_filter)<1:
            self.cql_filter=query_str
        else:
            query_str = sep + query_str
            self.cql_filter += query_str
    
    def __check_propertie_in_schema(self, prop_name:str)->None:
        
        if prop_name not in self.schema:
            raise ValueError(f'Feature name {prop_name} must be in {self.schema.keys()}')
        
    def __propertie_equals(self, propertie_name:str, equals_to:Union[str, int, float]):
        
        self.__check_propertie_in_schema(propertie_name)
        if type(equals_to) is str:
            equals_to = f"'{equals_to}'"

        query_str = f"({propertie_name}={equals_to})"
        
        return query_str
    
    def properties_equals(self, *ignore, **propertie_comparisons):
        
        #se tiver mais de um filtro, separa corretamente
        self.add_to_filter('', sep=';')
        for prop_name, prop_val in propertie_comparisons.items():
            query_str = self.__propertie_equals(prop_name, prop_val)
            self.add_to_filter(query_str, sep='AND')

    def point_within_pol(self, x:float, y:float, precision:int=5)->dict:
        '''Precision is in meters. Returns the polygon in self.feature_name 
        which intersects a buffer of {precision} meters centralized at the point'''

        query = f'DWITHIN(ge_poligono,POINT({x} {y}),{precision},meters)'
        self.add_to_filter(query)

    def point_within_linha(self, x:float, y:float, precision:int=5)->dict:
        '''Precision is in meters. Returns the polygon in self.feature_name 
        which intersects a buffer of {precision} meters centralized at the point'''

        query = f'DWITHIN(ge_linha,POINT({x} {y}),{precision},meters)'
        self.add_to_filter(query)

    def point_within_multipol(self, x:float, y:float, precision:int=5)->dict:
        '''Precision is in meters. Returns the polygon in self.feature_name 
        which intersects a buffer of {precision} meters centralized at the point'''

        query = f'DWITHIN(ge_multipoligono,POINT({x} {y}),{precision},meters)'
        self.add_to_filter(query)

    def polygon_within_pol(self, coordinates:str, precision:int=5)->dict:
        '''Precision is in meters. Returns the polygon in self.feature_name 
        which intersects a buffer of {precision} meters centralized at the point'''

        query = f'DWITHIN(ge_poligono,POLYGON({coordinates}),{precision},meters)'
        self.add_to_filter(query)

    def polygon_within_linha(self, coordinates:str, precision:int=5)->dict:
        '''Precision is in meters. Returns the polygon in self.feature_name 
        which intersects a buffer of {precision} meters centralized at the point'''

        query = f'DWITHIN(ge_linha,POLYGON({coordinates}),{precision},meters)'
        self.add_to_filter(query)

    def polygon_within_multipol(self, coordinates:str, precision:int=5)->dict:
        '''Precision is in meters. Returns the polygon in self.feature_name 
        which intersects a buffer of {precision} meters centralized at the point'''

        query = f'DWITHIN(ge_multipoligono,POLYGON({coordinates}),{precision},meters)'
        self.add_to_filter(query)


    def __call__(self):
        
        return self.cql_filter