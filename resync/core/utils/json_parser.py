"""
Robust JSON parsing utilities for LLM responses.

This module provides enhanced JSON parsing capabilities with multiple fallback strategies
for handling malformed or inconsistent JSON responses from language models.
"""

import re
import json
import logging
from typing import Any, Dict, Optional, Tuple, List

try:
    import orjson
    ORJSON_AVAILABLE = True
except ImportError:
    ORJSON_AVAILABLE = False

logger = logging.getLogger(__name__)


class JSONParseError(Exception):
    """Exception raised when JSON parsing fails."""
    pass


class RobustJSONParser:
    """
    A robust JSON parser designed specifically for LLM responses.

    Features:
    - Multiple parsing strategies with fallbacks
    - Fast parsing using orjson when available
    - Comprehensive error handling and logging
    - Support for various malformed JSON formats
    """

    def __init__(self):
        """Initialize the parser with regex patterns for JSON extraction."""
        # Common patterns for JSON in LLM responses
        self.json_patterns = [
            r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}',  # Simple JSON object
            r'\{(?:[^{}]|"(?:[^"\\]|\\.)*"|[^{}]*\{[^{}]*\}[^{}]*)*\}',  # Complex JSON with nested objects
            r'\{[^{}]*\}',  # Basic object pattern
            r'\{.*\}',  # Greedy pattern as last resort
        ]

        # Common prefixes/suffixes to strip
        self.strip_prefixes = [
            '```json\n', '```json', 'json\n', '```\n',
            'Here is the JSON:\n', 'JSON:\n', 'Response:\n'
        ]
        self.strip_suffixes = [
            '\n```', '```', '\n', ' '
        ]

    def clean_llm_response(self, response: str) -> str:
        """
        Clean LLM response by removing common prefixes/suffixes and normalizing.

        Args:
            response: Raw LLM response text.

        Returns:
            Cleaned response text.
        """
        cleaned = response.strip()

        # Remove common markdown formatting
        if cleaned.startswith('```'):
            cleaned = cleaned.replace('```json', '').replace('```', '').strip()

        # Remove common prefixes
        for prefix in self.strip_prefixes:
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix):].strip()
                break

        # Remove common suffixes
        for suffix in self.strip_suffixes:
            if cleaned.endswith(suffix):
                cleaned = cleaned[:-len(suffix)].strip()
                break

        return cleaned

    def extract_json_from_text(self, text: str) -> List[str]:
        """
        Extract all JSON-like strings from text using multiple regex patterns.

        Args:
            text: Text to search for JSON objects.

        Returns:
            List of potential JSON strings found in the text.
        """
        candidates = []

        for pattern in self.json_patterns:
            matches = re.findall(pattern, text, re.DOTALL)
            candidates.extend(matches)

        # Remove duplicates while preserving order
        seen = set()
        unique_candidates = []
        for candidate in candidates:
            if candidate not in seen:
                seen.add(candidate)
                unique_candidates.append(candidate)

        return unique_candidates

    def parse_json_safe(self, json_str: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Safely parse a JSON string with comprehensive error handling.

        Args:
            json_str: JSON string to parse.

        Returns:
            Tuple of (parsed_dict, error_message). Parsed dict is None if parsing failed.
        """
        if not json_str or not json_str.strip():
            return None, "Empty JSON string"

        try:
            # Try orjson first if available (faster)
            if ORJSON_AVAILABLE:
                try:
                    return orjson.loads(json_str), None
                except orjson.JSONDecodeError:
                    pass

            # Fall back to standard json library
            return json.loads(json_str), None

        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            error_msg = f"JSON decode error: {str(e)}"
            logger.debug(f"Failed to parse JSON: {error_msg}. Input: {json_str[:100]}...")
            return None, error_msg

    def try_fix_common_json_issues(self, json_str: str) -> List[str]:
        """
        Attempt to fix common JSON formatting issues.

        Args:
            json_str: Malformed JSON string.

        Returns:
            List of potentially fixed JSON strings to try.
        """
        fixes = [json_str]  # Original first

        # Fix trailing commas
        fixed = re.sub(r',(\s*[}\]])', r'\1', json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Fix single quotes (though this might break some strings)
        if "'" in json_str and json_str.count("'") > json_str.count('"'):
            fixed = json_str.replace("'", '"')
            fixes.append(fixed)

        # Fix missing quotes around keys
        fixed = re.sub(r'(\w+):', r'"\1":', json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Try to balance braces if they're unbalanced
        open_braces = json_str.count('{')
        close_braces = json_str.count('}')
        if open_braces > close_braces:
            fixes.append(json_str + '}')
        elif close_braces > open_braces:
            fixes.append('{' + json_str)

        return fixes

    def extract_and_parse_json(self, text: str, max_candidates: int = 5) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Extract and parse JSON from LLM response with multiple fallback strategies.

        Args:
            text: Text containing JSON response from LLM.
            max_candidates: Maximum number of JSON candidates to try.

        Returns:
            Tuple of (parsed_json, error_message). Returns None, error_msg if all parsing fails.
        """
        if not text or not text.strip():
            return None, "Empty response text"

        # Clean the response
        cleaned_text = self.clean_llm_response(text)
        if not cleaned_text:
            return None, "Response became empty after cleaning"

        # Try parsing the cleaned text directly first
        parsed, error = self.parse_json_safe(cleaned_text)
        if parsed is not None:
            return parsed, None

        # Extract JSON candidates from the cleaned text
        candidates = self.extract_json_from_text(cleaned_text)

        # Limit candidates to avoid excessive processing
        candidates = candidates[:max_candidates]

        # Try each candidate
        for candidate in candidates:
            # Try the candidate as-is
            parsed, error = self.parse_json_safe(candidate)
            if parsed is not None:
                return parsed, None

            # Try to fix common issues
            fixed_candidates = self.try_fix_common_json_issues(candidate)
            for fixed in fixed_candidates:
                if fixed != candidate:  # Only try if different
                    parsed, error = self.parse_json_safe(fixed)
                    if parsed is not None:
                        return parsed, None

        # If all parsing failed, return the best error message
        return None, f"Failed to extract valid JSON from response. Tried {len(candidates)} candidates."

    def parse_with_schema_validation(self, text: str, required_keys: List[str]) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Parse JSON and validate it contains required keys.

        Args:
            text: Text containing JSON response from LLM.
            required_keys: List of keys that must be present in the JSON.

        Returns:
            Tuple of (parsed_json, error_message).
        """
        parsed, error = self.extract_and_parse_json(text)
        if parsed is None:
            return None, error

        missing_keys = []
        for key in required_keys:
            if key not in parsed:
                missing_keys.append(key)

        if missing_keys:
            return None, f"Missing required keys: {missing_keys}"

        return parsed, None


# Global instance for convenience
json_parser = RobustJSONParser()


def parse_llm_json_response(response: str, required_keys: List[str] = None) -> Dict[str, Any]:
    """
    Convenience function to parse JSON from LLM response.

    Args:
        response: Raw LLM response text.
        required_keys: Optional list of keys that must be present.

    Returns:
        Parsed JSON dictionary.

    Raises:
        JSONParseError: If parsing fails or required keys are missing.
    """
    if required_keys:
        parsed, error = json_parser.parse_with_schema_validation(response, required_keys)
    else:
        parsed, error = json_parser.extract_and_parse_json(response)

    if parsed is None:
        raise JSONParseError(f"Failed to parse JSON from LLM response: {error}")

    return parsed


def safe_parse_llm_json_response(response: str, required_keys: List[str] = None) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """
    Safe version of parse_llm_json_response that doesn't raise exceptions.

    Args:
        response: Raw LLM response text.
        required_keys: Optional list of keys that must be present.

    Returns:
        Tuple of (parsed_json, error_message).
    """
    try:
        return json_parser.extract_and_parse_json(response, required_keys)
    except Exception as e:
        return None, str(e)