# resync/core/utils/json_parser.py
import json
import logging
from typing import Any, Dict, List

from ..exceptions import ParsingError
from .common_error_handlers import handle_parsing_errors

logger = logging.getLogger(__name__)

# Security constants
MAX_JSON_SIZE = 1024 * 1024  # 1MB limit for JSON content
MAX_TEXT_SIZE = 10 * 1024 * 1024  # 10MB limit for input text


@handle_parsing_errors("Failed to parse LLM JSON response")
def parse_llm_json_response(
    text: str,
    required_keys: List[str],
    max_size: int = MAX_JSON_SIZE,
    strict: bool = True,
) -> Dict[str, Any]:
    """
    Extracts, parses, and validates a JSON object from a string,
    often from an LLM response.

    This function includes security measures to prevent DoS attacks
    through large input processing.

    Args:
        text: The string potentially containing a JSON object.
        required_keys: A list of keys that must be present in the JSON.
        max_size: Maximum allowed size for JSON string (security limit).
        strict: If True, raise on extra keys not in required_keys.

    Raises:
        ParsingError: If the JSON is malformed, cannot be found, is missing
                      required keys, or exceeds size limits.
        ValueError: If input exceeds max_size.

    Returns:
        The parsed and validated JSON data as a dictionary.
    """
    # Security: Check input size limits
    if len(text) > MAX_TEXT_SIZE:
        raise ParsingError(f"Input text exceeds maximum size of {MAX_TEXT_SIZE} bytes")

    if len(text.encode("utf-8")) > MAX_TEXT_SIZE:
        raise ParsingError(f"Input text exceeds maximum size of {MAX_TEXT_SIZE} bytes")

    # Sanitization: Remove null bytes and other potentially harmful characters
    text = text.replace("\x00", "").replace("\ufeff", "")

    # Basic cleanup: find the first '{' and last '}'
    start_index = text.find("{")
    end_index = text.rfind("}")
    if start_index == -1 or end_index == -1 or start_index > end_index:
        raise ParsingError("No valid JSON object found in the text.")

    json_str = text[start_index : end_index + 1]

    # Security: Check JSON string size
    if len(json_str) > max_size:
        raise ParsingError(f"JSON content exceeds maximum size of {max_size} bytes")

    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as e:
        logger.warning("JSON decode error", error=str(e), json_length=len(json_str))
        raise ParsingError(f"Invalid JSON format: {str(e)}")

    # Validate that result is a dictionary
    if not isinstance(data, dict):
        raise ParsingError("Parsed JSON is not an object (dictionary)")

    # Check for required keys
    missing_keys = [key for key in required_keys if key not in data]
    if missing_keys:
        raise ParsingError(f"JSON is missing required keys: {', '.join(missing_keys)}")

    # Optional strict validation: ensure no extra keys
    if strict and required_keys:
        extra_keys = [key for key in data.keys() if key not in required_keys]
        if extra_keys:
            raise ParsingError(
                f"JSON contains unexpected keys in strict mode: {', '.join(extra_keys)}"
            )

    # Security: Prevent extremely deep nesting (basic protection)
    def check_nesting(obj: Any, max_depth: int = 10, current_depth: int = 0) -> None:
        if current_depth > max_depth:
            raise ParsingError(f"JSON nesting depth exceeds maximum of {max_depth}")
        if isinstance(obj, dict):
            for value in obj.values():
                check_nesting(value, max_depth, current_depth + 1)
        elif isinstance(obj, list):
            for item in obj:
                check_nesting(item, max_depth, current_depth + 1)

    check_nesting(data)

    return data
