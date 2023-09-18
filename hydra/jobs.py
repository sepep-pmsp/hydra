from dagster import (
    AssetSelection,
    define_asset_job,
)


censo_job = define_asset_job('censo_job', selection=AssetSelection.groups('censo_bronze'))