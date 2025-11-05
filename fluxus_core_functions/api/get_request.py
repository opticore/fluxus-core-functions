import requests
from typing import Annotated

from fluxus_sdk.logger import logger
from fluxus_sdk.func import fluxus_func


@fluxus_func(
    name="get_request",
    label="Get Request",
    description="Make a GET request to the given URL.",
    dir_path="api/",
)
def get_request(
    url: Annotated[str, "URL to make the request to."],
    headers: Annotated[dict, "Headers to include in the request."] = {},
    params: Annotated[dict, "Parameters to include in the request."] = {},
) -> Annotated[requests.models.Response, "Response object."]:
    """Make a GET request to the given URL.

    Args:
        url (str): URL to make the request to.
        headers (dict, optional): Headers to include in the request.
        params (dict, optional): Parameters to include in the request.
    Returns:
        response (requests.models.Response): Response object.
    """
    logger.info(f"Making GET request to {url}")
    response = requests.get(url, headers=headers, params=params, timeout=10)
    logger.info(f"GET request to {url} code {response.status_code}")
    response.raise_for_status()
    logger.debug(f"Response: {response.text}")
    return response
