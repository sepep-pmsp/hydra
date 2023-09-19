from dagster import ConfigurableResource

from hydra.utils.geosampa_client import get_client

class GeosampaClient(ConfigurableResource):

    def get_feature(self, feature_name:str, **kwargs):
        return get_client().get_feature(feature_name, **kwargs)
