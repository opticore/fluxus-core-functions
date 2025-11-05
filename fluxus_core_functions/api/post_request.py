import requests
from typing import Annotated
from fluxus_sdk.logger import logger
from fluxus_sdk.func import fluxus_func


@fluxus_func(
    name="post_request",
    label="Post Request",
    description="Make a POST request to the given URL.",
    dir_path="api/",
)
def post_request(
    url: Annotated[str, "URL to make the request to."],
    headers: Annotated[dict, "Headers to include in the request."] = {},
    data: Annotated[dict, "Data to include in the request."] = {},
    json: Annotated[dict, "JSON data to include in the request."] = {},
) -> Annotated[requests.models.Response, "Response object."]:
    """Make a POST request to the given URL.

    Args:
        url (str): URL to make the request to.
        headers (dict, optional): Headers to include in the request.
        data (dict, optional): Data to include in the request.
        json (dict, optional): JSON data to include in the request.
    Returns:
        response (requests.models.Response): Response object.
    """
    logger.info(f"Making POST request to {url}")
    response = requests.post(url, headers=headers, data=data, json=json, timeout=10)
    logger.info(f"POST request to {url} code {response.status_code}")
    response.raise_for_status()
    logger.debug(f"Response: {response.text}")
    return response
