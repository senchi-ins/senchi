import logging
from typing import List
from pydantic import BaseModel

logger = logging.getLogger(__name__)


def get_all_model_fields(model_classes: List[BaseModel]) -> List[str]:
    # Helper func to get all the fields from a list of pydantic models
    all_fields = set()
    for model_class in model_classes:
        all_fields.update(model_class.model_fields.keys())
    return list(all_fields)
