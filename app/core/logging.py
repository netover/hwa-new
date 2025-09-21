import json
import logging
import os
import sys
from typing import Any, Dict

logger = logging.getLogger("resync")
logger.setLevel("DEBUG" if os.getenv("LOG_LEVEL") == "DEBUG" else "INFO")

handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter("%(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


def log_json(data: Dict[str, Any]) -> None:
    logger.info(json.dumps(data))
