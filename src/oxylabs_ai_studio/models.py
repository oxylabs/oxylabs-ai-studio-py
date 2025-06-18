from typing import Any, TypedDict


class SchemaResponse(TypedDict):
    openapi_schema: dict[str, Any] | None
