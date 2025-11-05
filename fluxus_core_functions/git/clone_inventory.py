from django.utils import timezone
from git import Repo
from typing import Annotated
from fluxus_sdk.logger import logger
from fluxus_sdk.func import fluxus_func
from fluxus.network.models import Inventory
from fluxus.administration.models import User


def get_repo_url_with_token(repo_url, token):
    if repo_url.startswith("https://"):
        return repo_url.replace("https://", f"https://{token}@")
    return repo_url


@fluxus_func(
    name="clone_inventory",
    label="Clone Inventory",
    description="Clone inventory using a personal access token.",
    dir_path="git/",
)
def clone_inventory(
    inventory_pk: Annotated[int, "The primary key of the inventory."],
    user: Annotated[User, "The user object."] = None,
) -> Annotated[Inventory, "The inventory object."]:
    """Clone inventory using a personal access token.

    Args:
        inventory_pk (fluxus.network.models.Inventory): The primary key of the inventory.

    Returns:
        inventory: The inventory object.
    """
    inventory = Inventory.objects.get(pk=inventory_pk)
    logger.info(f"Cloning inventory {inventory.name}")
    token = user.github_access_token
    repo_url = get_repo_url_with_token(inventory.inv_config["github_url"], token)
    repo_path = inventory.get_inventory_path(user)

    try:
        Repo.clone_from(repo_url, repo_path)
    except Exception as e:
        logger.error(f"Error cloning repository: {e}")
        inventory.last_sync_status = "failed"

    inventory.last_sync = timezone.now()
    inventory.save()
    return inventory
