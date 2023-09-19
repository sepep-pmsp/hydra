from dagster import (
    AssetKey,
    ScheduleDefinition,
    DefaultScheduleStatus,
    RunRequest,
    ScheduleEvaluationContext,
    SkipReason,
    schedule,
)

from .resources import CensoResource
from .jobs import (
    censo_job,
    geosampa_job,
)
from .utils.io.files import generate_file_hash


geosampa_schedule = ScheduleDefinition(
    job=geosampa_job,
    cron_schedule="0 4 * * *",
    default_status=DefaultScheduleStatus.RUNNING
)


@schedule(
    job=censo_job,
    cron_schedule='0 3 * * *',
    default_status=DefaultScheduleStatus.RUNNING
)
def censo_schedule(
        context: ScheduleEvaluationContext,
        censo_resource: CensoResource,
):
    zip_content = censo_resource.download_zipfile()
    zip_hash = generate_file_hash(zip_content)

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
