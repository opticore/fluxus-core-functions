from typing import Annotated

from fluxus_sdk.func import fluxus_func
from fluxus_sdk.logger import logger

from fluxus.network.models import Snapshot


@fluxus_func(
    name="delete_snapshot",
    label="Delete Snapshot",
    description="Delete snapshot.",
    dir_path="snapshot/",
)
def delete_snapshot(snapshot_path: Annotated[str, "Path to snapshot."]):
    snapshot = Snapshot.objects.get(path=snapshot_path)
    snapshot.delete()
    logger.info(f"Snapshot deleted from {snapshot_path}")
