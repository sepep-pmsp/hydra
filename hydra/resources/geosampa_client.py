from dagster import ConfigurableResource

from hydra.utils.geosampa_client import get_client, GeoSampaWfs

class GeosampaClient(ConfigurableResource):
    client : GeoSampaWfs = None

    def __init__(self):
        self.client = get_client()

    def get_feature(self, feature_name:str, **kwargs):
        return self.client.get_feature(feature_name, **kwargs)
