from dagster import (
    AssetKey,
    DefaultScheduleStatus,
    RunRequest,
    ScheduleEvaluationContext,
    SkipReason,
    schedule,
)

from .resources import CensoResource
from .jobs import censo_job


@schedule(
    job=censo_job,
    cron_schedule='0/3 * * * *',
    default_status=DefaultScheduleStatus.RUNNING
)
def censo_schedule(
        context: ScheduleEvaluationContext,
        censo_resource: CensoResource,
):
    zip_content, zip_hash = censo_resource.download_zipfile(return_hash=True)

    materialization_event = context.instance.get_latest_materialization_event(
        AssetKey(['arquivo_zip_censo'])
    )

    previous_zip_hash = None
    if materialization_event != None:
        previous_zip_hash = materialization_event.asset_materialization\
            .metadata['SHA256 Hash do arquivo'].value

    if previous_zip_hash != None and zip_hash == previous_zip_hash:
        yield SkipReason(f"O arquivo zip do censo não foi alterado.")
    else:
        yield RunRequest(run_key=None, run_config={})
