import os
from .. import BASE_DIR


def _locate_resource(filename: str) -> str:
    return os.path.join(BASE_DIR, "icons", filename)
