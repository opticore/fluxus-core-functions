from typing import Annotated

from fluxus_sdk.func import fluxus_func
from fluxus_sdk.logger import logger


@fluxus_func(
    name="print",
    label="Print",
    description="Print a string to logs.",
    dir_path="core/",
)
def print(string: Annotated[str, "String to print."]):
    """Print a string to logs."""
    logger.info("I'm about to print a string...")
    logger.info(string)
    logger.info("I just printed a string...")
