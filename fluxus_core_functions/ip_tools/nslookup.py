import socket

from typing import Annotated
from fluxus_sdk.logger import logger
from fluxus_sdk.func import fluxus_func


@fluxus_func(
    name="nslookup",
    description="Perform a DNS lookup for the given hostname.",
    dir_path="ip_tools/",
)
def nslookup(
    hostname: Annotated[str, "The hostname to look up."],
) -> Annotated[str, "The IP address of the hostname."]:
    """
    Perform a DNS lookup for the given hostname.

    Args:
        hostname (str): The hostname to look up.

    Returns:
        nslookup_result (str): The IP address of the hostname.
    """
    logger.info(f"Performing DNS lookup for {hostname}...")
    try:
        ip_address = socket.gethostbyname(hostname)
        logger.info(f"IP address for {hostname} is {ip_address}.")
        return ip_address
    except socket.gaierror as e:
        logger.error(f"DNS lookup failed for {hostname}: {e}")
        return None
