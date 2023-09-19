from .geosampa_client import GeoSampaWfs

GEOSAMPA_WFS_DOMAIN = 'http://wfs.geosampa.prefeitura.sp.gov.br/geoserver/ows'

def get_client(domain=GEOSAMPA_WFS_DOMAIN, set_schemas=True):

    return GeoSampaWfs(domain, set_schemas=set_schemas)