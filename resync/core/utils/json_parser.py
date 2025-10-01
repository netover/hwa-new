# resync/core/utils/json_parser.py
import json
import logging
from typing import Any, Dict, List

from resync.core.exceptions import ParsingError

logger = logging.getLogger(__name__)


def parse_llm_json_response(
    text: str, required_keys: List[str]
) -> Dict[str, Any]:
    """
    Extracts, parses, and validates a JSON object from a string,
    often from an LLM response.

    Args:
        text: The string potentially containing a JSON object.
        required_keys: A list of keys that must be present in the JSON.

    Raises:
        ParsingError: If the JSON is malformed, cannot be found, or is missing
                      required keys.

    Returns:
        The parsed and validated JSON data as a dictionary.
    """
    try:
        # Basic cleanup: find the first '{' and last '}'
        start_index = text.find("{")
        end_index = text.rfind("}")
        if start_index == -1 or end_index == -1 or start_index > end_index:
            raise ParsingError("No valid JSON object found in the text.")

        json_str = text[start_index : end_index + 1]
        data = json.loads(json_str)

        missing_keys = [key for key in required_keys if key not in data]
        if missing_keys:
            raise ParsingError(
                f"JSON is missing required keys: {', '.join(missing_keys)}"
            )

        return data

    except json.JSONDecodeError as e:
        logger.debug("Failed to decode JSON: %s. Original text: %s", e, text)
        raise ParsingError(f"Invalid JSON format in the response: {e}") from e
    except Exception as e:
        # Catch any other unexpected error during parsing and wrap it
        logger.error("Unexpected error during JSON parsing: %s", e, exc_info=True)
        raise ParsingError("An unexpected error occurred while parsing the JSON.") from e