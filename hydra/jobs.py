from dagster import (
    AssetSelection,
    define_asset_job,
    EnvVar,
    multi_or_in_process_executor,
)

exec_geosampa = multi_or_in_process_executor.configured({
    "multiprocess": {
        "max_concurrent": EnvVar.int('GEOSAMPA_JOB_MAX_CONCURRENCY'),
    },
})

# Definições dos jobs
geosampa_job = define_asset_job(
    'geosampa_job',
    selection=AssetSelection.groups('geosampa_bronze', 'geosampa_silver'),
    executor_def=exec_geosampa)

censo_2010_job = define_asset_job(
    'censo_2010_job',
    selection=AssetSelection.groups('censo_2010_bronze'))

exec_censo_2022 = multi_or_in_process_executor.configured({
    "multiprocess": {
        "max_concurrent": EnvVar.int('CENSO_2022_JOB_MAX_CONCURRENCY'),
    },
})

censo_2022_job = define_asset_job(
    'censo_2022_job',
    selection=AssetSelection.groups('censo_2022_bronze'),
    executor_def=exec_censo_2022)
