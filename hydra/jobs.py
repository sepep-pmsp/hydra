from dagster import (
    AssetSelection,
    define_asset_job,
    EnvVar,
)


# Definições dos jobs
geosampa_job = define_asset_job(
    'geosampa_job',
    selection=AssetSelection.groups('geosampa_bronze', 'geosampa_silver'),
    config={
        'execution': {
            'config': {
                'max_concurrent': EnvVar.int('GEOSAMPA_JOB_MAX_CONCURRENCY'),
            }
        }
    },
    
)

censo_job = define_asset_job(
    'censo_job',
    selection=AssetSelection.groups('censo_bronze')
)
