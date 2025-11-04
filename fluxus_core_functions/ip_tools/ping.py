import os

from typing import Annotated
from fluxus_sdk.logger import logger
from fluxus_sdk.func import fluxus_func


@fluxus_func(
    name="ping",
    description="Ping a host to check its reachability.",
    dir_path="ip_tools/",
)
def ping(
    host: Annotated[str, "The host to ping."],
    count: Annotated[int, "The number of ping requests to send."] = 4,
) -> Annotated[bool, "True if the host is reachable, False otherwise."]:
    """
    Ping a host to check its reachability.

    Args:
        host (str): The host to ping.
        count (int): The number of ping requests to send.

    Returns:
        reachable (bool): True if the host is reachable, False otherwise.
    """
    logger.info(f"Pinging {host}...")
    response = os.system(f"ping -c {count} {host}")  # nosec
    if response == 0:
        logger.info(f"{host} is reachable.")
        return True
    else:
        logger.error(f"{host} is not reachable.")
        return False
