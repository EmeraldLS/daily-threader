import api_types
from typing import Any, Dict, TypeVar, Type

T = TypeVar("T")

def parse_response(response: Dict[str, Any], response_type: Type[T]) -> T:
    """Parse a response dictionary into a dataclass."""
    if issubclass(response_type, api_types.Error) and "error" in response:
        response["error"] = api_types.ErrorDetail(**response["error"])
    return response_type(**response)