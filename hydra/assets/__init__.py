from dagster import (
    load_assets_from_modules,
    AutoMaterializePolicy,
)

from . import geosampa as _geosampa
from . import censo as _censo
from . import ibge_api as _ibge_api

censo_assets = load_assets_from_modules([_censo], auto_materialize_policy=AutoMaterializePolicy.eager())
geosampa_assets = load_assets_from_modules([_geosampa], auto_materialize_policy=AutoMaterializePolicy.eager())
ibge_api_assets = load_assets_from_modules([_ibge_api], auto_materialize_policy=AutoMaterializePolicy.eager())
