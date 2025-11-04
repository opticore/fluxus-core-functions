from typing import Annotated

from fluxus_sdk.logger import logger
from fluxus_sdk.func import fluxus_func

from fluxus.network.helpers import create_snapshot as create_snapshot_helper
from fluxus.network.models import Inventory
from fluxus.administration.models import User


@fluxus_func(
    name="create_snapshot",
    description="Create snapshot.",
    dir_path="snapshot/",
)
def create_snapshot(
    inventory: Annotated[Inventory, "Inventory to create snapshot from."],
    user: Annotated[User, "User to create snapshot for."],
    snapshot_name: Annotated[str, "Name of snapshot."] = None,
) -> Annotated[str, "Path to snapshot."]:
    snapshot = create_snapshot_helper(inventory, user, display=snapshot_name)
    logger.info(f"Snapshot created at {snapshot.path}")
    return snapshot.path
