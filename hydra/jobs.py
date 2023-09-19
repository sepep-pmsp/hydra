from dagster import (
    AssetSelection,
    define_asset_job,
)


# Definições dos jobs
geosampa_job = define_asset_job(
    'geosampa_job',
    selection=AssetSelection.groups('geosampa_bronze', 'geosampa_silver')
)

censo_job = define_asset_job(
    'censo_job',
    selection=AssetSelection.groups('censo_bronze')
)
