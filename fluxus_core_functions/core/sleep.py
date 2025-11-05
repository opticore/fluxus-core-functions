import time
from typing import Annotated

from fluxus_sdk.func import fluxus_func
from fluxus_sdk.logger import logger


@fluxus_func(
    name="sleep",
    label="Sleep",
    description="Sleep for a given amount of time",
    dir_path="fluxus_core_functions/core",
)
def sleep(
    seconds: Annotated[int, "Number of seconds to sleep"],
):
    logger.info(f"Sleeping for {seconds} seconds")
    time.sleep(seconds)
    logger.info(f"Slept for {seconds} seconds")
