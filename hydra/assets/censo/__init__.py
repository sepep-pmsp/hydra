from dagster import (
    load_assets_from_modules,
)


from . import censo_2010 as censo_2010_
from . import censo_2022 as censo_2022_

censo_assets = load_assets_from_modules([censo_2010_, censo_2022_])