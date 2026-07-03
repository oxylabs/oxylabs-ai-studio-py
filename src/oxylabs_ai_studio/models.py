from typing import Any, Literal, TypedDict


class SchemaResponse(TypedDict):
    openapi_schema: dict[str, Any] | None


class BrowserInstructionSelector(TypedDict):
    type: Literal["xpath", "css", "text"]
    value: str


class BrowserInstruction(TypedDict, total=False):
    """Web Scraper API browser instruction."""

    type: Literal[
        "click",
        "input",
        "scroll",
        "scroll_to_bottom",
        "wait",
        "wait_for_element",
        "fetch_resource",
    ]
    selector: BrowserInstructionSelector
    value: str
    filter: str
    x: int
    y: int
    timeout_s: int
    wait_time_s: int
    on_error: Literal["error", "skip"]
