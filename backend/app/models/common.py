"""Shared API response helpers."""

from datetime import datetime
from typing import Any, Optional

from bson import ObjectId
from pydantic import BaseModel


class ErrorResponse(BaseModel):
    detail: str
    code: str
    status: int


def serialize_doc(doc: Optional[dict[str, Any]]) -> Optional[dict[str, Any]]:
    if doc is None:
        return None
    out = dict(doc)
    if "_id" in out:
        out["id"] = str(out.pop("_id"))
    for key, val in list(out.items()):
        if isinstance(val, ObjectId):
            out[key] = str(val)
    return out
