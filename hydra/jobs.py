from dagster import (
    AssetSelection,
    define_asset_job,
    EnvVar,
    multi_or_in_process_executor,
)

exec = multi_or_in_process_executor.configured({
    "multiprocess": {
        "max_concurrent": EnvVar.int('GEOSAMPA_JOB_MAX_CONCURRENCY'),
    },
}
)

# Definições dos jobs
geosampa_job = define_asset_job(
    'geosampa_job',
    selection=AssetSelection.groups('geosampa_bronze', 'geosampa_silver'),
    executor_def=exec
)

censo_job = define_asset_job(
    'censo_job',
    selection=AssetSelection.groups('censo_bronze')
)

censo_2022_job = define_asset_job(
    'censo_2022_job',
    selection=AssetSelection.groups('censo_2022_bronze')
)
