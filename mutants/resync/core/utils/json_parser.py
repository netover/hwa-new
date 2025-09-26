"""
Robust JSON parsing utilities for LLM responses.

This module provides enhanced JSON parsing capabilities with multiple fallback strategies
for handling malformed or inconsistent JSON responses from language models.
"""

import json
import logging
import re
from typing import Any, Dict, List, Optional, Tuple

try:
    import orjson

    ORJSON_AVAILABLE = True
except ImportError:
    ORJSON_AVAILABLE = False

logger = logging.getLogger(__name__)
from inspect import signature as _mutmut_signature
from typing import Annotated, Callable, ClassVar

MutantDict = Annotated[dict[str, Callable], "Mutant"]


def _mutmut_trampoline(orig, mutants, call_args, call_kwargs, self_arg=None):
    """Forward call to original or mutated function, depending on the environment"""
    import os

    mutant_under_test = os.environ["MUTANT_UNDER_TEST"]
    if mutant_under_test == "fail":
        from mutmut.__main__ import MutmutProgrammaticFailException

        raise MutmutProgrammaticFailException("Failed programmatically")
    elif mutant_under_test == "stats":
        from mutmut.__main__ import record_trampoline_hit

        record_trampoline_hit(orig.__module__ + "." + orig.__name__)
        result = orig(*call_args, **call_kwargs)
        return result
    prefix = orig.__module__ + "." + orig.__name__ + "__mutmut_"
    if not mutant_under_test.startswith(prefix):
        result = orig(*call_args, **call_kwargs)
        return result
    mutant_name = mutant_under_test.rpartition(".")[-1]
    if self_arg:
        # call to a class method where self is not bound
        result = mutants[mutant_name](self_arg, *call_args, **call_kwargs)
    else:
        result = mutants[mutant_name](*call_args, **call_kwargs)
    return result


class JSONParseError(Exception):
    """Exception raised when JSON parsing fails."""


class RobustJSONParser:
    """
    A robust JSON parser designed specifically for LLM responses.

    Features:
    - Multiple parsing strategies with fallbacks
    - Fast parsing using orjson when available
    - Comprehensive error handling and logging
    - Support for various malformed JSON formats
    """

    def xǁRobustJSONParserǁ__init____mutmut_orig(self) -> None:
        """Initialize the parser with regex patterns for JSON extraction."""
        # Common patterns for JSON in LLM responses
        self.json_patterns = [
            r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}",  # Simple JSON object
            r'\{(?:[^{}]|"(?:[^"\\]|\\.)*"|[^{}]*\{[^{}]*\}[^{}]*)*\}',  # Complex JSON with nested objects
            r"\{[^{}]*\}",  # Basic object pattern
            r"\{.*\}",  # Greedy pattern as last resort
        ]

        # Common prefixes/suffixes to strip
        self.strip_prefixes = [
            "```json\n",
            "```json",
            "json\n",
            "```\n",
            "Here is the JSON:\n",
            "JSON:\n",
            "Response:\n",
        ]
        self.strip_suffixes = ["\n```", "```", "\n", " "]

    def xǁRobustJSONParserǁ__init____mutmut_1(self) -> None:
        """Initialize the parser with regex patterns for JSON extraction."""
        # Common patterns for JSON in LLM responses
        self.json_patterns = None

        # Common prefixes/suffixes to strip
        self.strip_prefixes = [
            "```json\n",
            "```json",
            "json\n",
            "```\n",
            "Here is the JSON:\n",
            "JSON:\n",
            "Response:\n",
        ]
        self.strip_suffixes = ["\n```", "```", "\n", " "]

    def xǁRobustJSONParserǁ__init____mutmut_2(self) -> None:
        """Initialize the parser with regex patterns for JSON extraction."""
        # Common patterns for JSON in LLM responses
        self.json_patterns = [
            r"XX\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}XX",  # Simple JSON object
            r'\{(?:[^{}]|"(?:[^"\\]|\\.)*"|[^{}]*\{[^{}]*\}[^{}]*)*\}',  # Complex JSON with nested objects
            r"\{[^{}]*\}",  # Basic object pattern
            r"\{.*\}",  # Greedy pattern as last resort
        ]

        # Common prefixes/suffixes to strip
        self.strip_prefixes = [
            "```json\n",
            "```json",
            "json\n",
            "```\n",
            "Here is the JSON:\n",
            "JSON:\n",
            "Response:\n",
        ]
        self.strip_suffixes = ["\n```", "```", "\n", " "]

    def xǁRobustJSONParserǁ__init____mutmut_3(self) -> None:
        """Initialize the parser with regex patterns for JSON extraction."""
        # Common patterns for JSON in LLM responses
        self.json_patterns = [
            r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}",  # Simple JSON object
            r'\{(?:[^{}]|"(?:[^"\\]|\\.)*"|[^{}]*\{[^{}]*\}[^{}]*)*\}',  # Complex JSON with nested objects
            r"\{[^{}]*\}",  # Basic object pattern
            r"\{.*\}",  # Greedy pattern as last resort
        ]

        # Common prefixes/suffixes to strip
        self.strip_prefixes = [
            "```json\n",
            "```json",
            "json\n",
            "```\n",
            "Here is the JSON:\n",
            "JSON:\n",
            "Response:\n",
        ]
        self.strip_suffixes = ["\n```", "```", "\n", " "]

    def xǁRobustJSONParserǁ__init____mutmut_4(self) -> None:
        """Initialize the parser with regex patterns for JSON extraction."""
        # Common patterns for JSON in LLM responses
        self.json_patterns = [
            r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}",  # Simple JSON object
            r'\{(?:[^{}]|"(?:[^"\\]|\\.)*"|[^{}]*\{[^{}]*\}[^{}]*)*\}',  # Complex JSON with nested objects
            r"\{[^{}]*\}",  # Basic object pattern
            r"\{.*\}",  # Greedy pattern as last resort
        ]

        # Common prefixes/suffixes to strip
        self.strip_prefixes = [
            "```json\n",
            "```json",
            "json\n",
            "```\n",
            "Here is the JSON:\n",
            "JSON:\n",
            "Response:\n",
        ]
        self.strip_suffixes = ["\n```", "```", "\n", " "]

    def xǁRobustJSONParserǁ__init____mutmut_5(self) -> None:
        """Initialize the parser with regex patterns for JSON extraction."""
        # Common patterns for JSON in LLM responses
        self.json_patterns = [
            r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}",  # Simple JSON object
            r'XX\{(?:[^{}]|"(?:[^"\\]|\\.)*"|[^{}]*\{[^{}]*\}[^{}]*)*\}XX',  # Complex JSON with nested objects
            r"\{[^{}]*\}",  # Basic object pattern
            r"\{.*\}",  # Greedy pattern as last resort
        ]

        # Common prefixes/suffixes to strip
        self.strip_prefixes = [
            "```json\n",
            "```json",
            "json\n",
            "```\n",
            "Here is the JSON:\n",
            "JSON:\n",
            "Response:\n",
        ]
        self.strip_suffixes = ["\n```", "```", "\n", " "]

    def xǁRobustJSONParserǁ__init____mutmut_6(self) -> None:
        """Initialize the parser with regex patterns for JSON extraction."""
        # Common patterns for JSON in LLM responses
        self.json_patterns = [
            r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}",  # Simple JSON object
            r'\{(?:[^{}]|"(?:[^"\\]|\\.)*"|[^{}]*\{[^{}]*\}[^{}]*)*\}',  # Complex JSON with nested objects
            r"\{[^{}]*\}",  # Basic object pattern
            r"\{.*\}",  # Greedy pattern as last resort
        ]

        # Common prefixes/suffixes to strip
        self.strip_prefixes = [
            "```json\n",
            "```json",
            "json\n",
            "```\n",
            "Here is the JSON:\n",
            "JSON:\n",
            "Response:\n",
        ]
        self.strip_suffixes = ["\n```", "```", "\n", " "]

    def xǁRobustJSONParserǁ__init____mutmut_7(self) -> None:
        """Initialize the parser with regex patterns for JSON extraction."""
        # Common patterns for JSON in LLM responses
        self.json_patterns = [
            r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}",  # Simple JSON object
            r'\{(?:[^{}]|"(?:[^"\\]|\\.)*"|[^{}]*\{[^{}]*\}[^{}]*)*\}',  # Complex JSON with nested objects
            r"\{[^{}]*\}",  # Basic object pattern
            r"\{.*\}",  # Greedy pattern as last resort
        ]

        # Common prefixes/suffixes to strip
        self.strip_prefixes = [
            "```json\n",
            "```json",
            "json\n",
            "```\n",
            "Here is the JSON:\n",
            "JSON:\n",
            "Response:\n",
        ]
        self.strip_suffixes = ["\n```", "```", "\n", " "]

    def xǁRobustJSONParserǁ__init____mutmut_8(self) -> None:
        """Initialize the parser with regex patterns for JSON extraction."""
        # Common patterns for JSON in LLM responses
        self.json_patterns = [
            r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}",  # Simple JSON object
            r'\{(?:[^{}]|"(?:[^"\\]|\\.)*"|[^{}]*\{[^{}]*\}[^{}]*)*\}',  # Complex JSON with nested objects
            r"XX\{[^{}]*\}XX",  # Basic object pattern
            r"\{.*\}",  # Greedy pattern as last resort
        ]

        # Common prefixes/suffixes to strip
        self.strip_prefixes = [
            "```json\n",
            "```json",
            "json\n",
            "```\n",
            "Here is the JSON:\n",
            "JSON:\n",
            "Response:\n",
        ]
        self.strip_suffixes = ["\n```", "```", "\n", " "]

    def xǁRobustJSONParserǁ__init____mutmut_9(self) -> None:
        """Initialize the parser with regex patterns for JSON extraction."""
        # Common patterns for JSON in LLM responses
        self.json_patterns = [
            r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}",  # Simple JSON object
            r'\{(?:[^{}]|"(?:[^"\\]|\\.)*"|[^{}]*\{[^{}]*\}[^{}]*)*\}',  # Complex JSON with nested objects
            r"\{[^{}]*\}",  # Basic object pattern
            r"\{.*\}",  # Greedy pattern as last resort
        ]

        # Common prefixes/suffixes to strip
        self.strip_prefixes = [
            "```json\n",
            "```json",
            "json\n",
            "```\n",
            "Here is the JSON:\n",
            "JSON:\n",
            "Response:\n",
        ]
        self.strip_suffixes = ["\n```", "```", "\n", " "]

    def xǁRobustJSONParserǁ__init____mutmut_10(self) -> None:
        """Initialize the parser with regex patterns for JSON extraction."""
        # Common patterns for JSON in LLM responses
        self.json_patterns = [
            r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}",  # Simple JSON object
            r'\{(?:[^{}]|"(?:[^"\\]|\\.)*"|[^{}]*\{[^{}]*\}[^{}]*)*\}',  # Complex JSON with nested objects
            r"\{[^{}]*\}",  # Basic object pattern
            r"\{.*\}",  # Greedy pattern as last resort
        ]

        # Common prefixes/suffixes to strip
        self.strip_prefixes = [
            "```json\n",
            "```json",
            "json\n",
            "```\n",
            "Here is the JSON:\n",
            "JSON:\n",
            "Response:\n",
        ]
        self.strip_suffixes = ["\n```", "```", "\n", " "]

    def xǁRobustJSONParserǁ__init____mutmut_11(self) -> None:
        """Initialize the parser with regex patterns for JSON extraction."""
        # Common patterns for JSON in LLM responses
        self.json_patterns = [
            r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}",  # Simple JSON object
            r'\{(?:[^{}]|"(?:[^"\\]|\\.)*"|[^{}]*\{[^{}]*\}[^{}]*)*\}',  # Complex JSON with nested objects
            r"\{[^{}]*\}",  # Basic object pattern
            r"XX\{.*\}XX",  # Greedy pattern as last resort
        ]

        # Common prefixes/suffixes to strip
        self.strip_prefixes = [
            "```json\n",
            "```json",
            "json\n",
            "```\n",
            "Here is the JSON:\n",
            "JSON:\n",
            "Response:\n",
        ]
        self.strip_suffixes = ["\n```", "```", "\n", " "]

    def xǁRobustJSONParserǁ__init____mutmut_12(self) -> None:
        """Initialize the parser with regex patterns for JSON extraction."""
        # Common patterns for JSON in LLM responses
        self.json_patterns = [
            r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}",  # Simple JSON object
            r'\{(?:[^{}]|"(?:[^"\\]|\\.)*"|[^{}]*\{[^{}]*\}[^{}]*)*\}',  # Complex JSON with nested objects
            r"\{[^{}]*\}",  # Basic object pattern
            r"\{.*\}",  # Greedy pattern as last resort
        ]

        # Common prefixes/suffixes to strip
        self.strip_prefixes = [
            "```json\n",
            "```json",
            "json\n",
            "```\n",
            "Here is the JSON:\n",
            "JSON:\n",
            "Response:\n",
        ]
        self.strip_suffixes = ["\n```", "```", "\n", " "]

    def xǁRobustJSONParserǁ__init____mutmut_13(self) -> None:
        """Initialize the parser with regex patterns for JSON extraction."""
        # Common patterns for JSON in LLM responses
        self.json_patterns = [
            r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}",  # Simple JSON object
            r'\{(?:[^{}]|"(?:[^"\\]|\\.)*"|[^{}]*\{[^{}]*\}[^{}]*)*\}',  # Complex JSON with nested objects
            r"\{[^{}]*\}",  # Basic object pattern
            r"\{.*\}",  # Greedy pattern as last resort
        ]

        # Common prefixes/suffixes to strip
        self.strip_prefixes = [
            "```json\n",
            "```json",
            "json\n",
            "```\n",
            "Here is the JSON:\n",
            "JSON:\n",
            "Response:\n",
        ]
        self.strip_suffixes = ["\n```", "```", "\n", " "]

    def xǁRobustJSONParserǁ__init____mutmut_14(self) -> None:
        """Initialize the parser with regex patterns for JSON extraction."""
        # Common patterns for JSON in LLM responses
        self.json_patterns = [
            r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}",  # Simple JSON object
            r'\{(?:[^{}]|"(?:[^"\\]|\\.)*"|[^{}]*\{[^{}]*\}[^{}]*)*\}',  # Complex JSON with nested objects
            r"\{[^{}]*\}",  # Basic object pattern
            r"\{.*\}",  # Greedy pattern as last resort
        ]

        # Common prefixes/suffixes to strip
        self.strip_prefixes = None
        self.strip_suffixes = ["\n```", "```", "\n", " "]

    def xǁRobustJSONParserǁ__init____mutmut_15(self) -> None:
        """Initialize the parser with regex patterns for JSON extraction."""
        # Common patterns for JSON in LLM responses
        self.json_patterns = [
            r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}",  # Simple JSON object
            r'\{(?:[^{}]|"(?:[^"\\]|\\.)*"|[^{}]*\{[^{}]*\}[^{}]*)*\}',  # Complex JSON with nested objects
            r"\{[^{}]*\}",  # Basic object pattern
            r"\{.*\}",  # Greedy pattern as last resort
        ]

        # Common prefixes/suffixes to strip
        self.strip_prefixes = [
            "XX```json\nXX",
            "```json",
            "json\n",
            "```\n",
            "Here is the JSON:\n",
            "JSON:\n",
            "Response:\n",
        ]
        self.strip_suffixes = ["\n```", "```", "\n", " "]

    def xǁRobustJSONParserǁ__init____mutmut_16(self) -> None:
        """Initialize the parser with regex patterns for JSON extraction."""
        # Common patterns for JSON in LLM responses
        self.json_patterns = [
            r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}",  # Simple JSON object
            r'\{(?:[^{}]|"(?:[^"\\]|\\.)*"|[^{}]*\{[^{}]*\}[^{}]*)*\}',  # Complex JSON with nested objects
            r"\{[^{}]*\}",  # Basic object pattern
            r"\{.*\}",  # Greedy pattern as last resort
        ]

        # Common prefixes/suffixes to strip
        self.strip_prefixes = [
            "```JSON\n",
            "```json",
            "json\n",
            "```\n",
            "Here is the JSON:\n",
            "JSON:\n",
            "Response:\n",
        ]
        self.strip_suffixes = ["\n```", "```", "\n", " "]

    def xǁRobustJSONParserǁ__init____mutmut_17(self) -> None:
        """Initialize the parser with regex patterns for JSON extraction."""
        # Common patterns for JSON in LLM responses
        self.json_patterns = [
            r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}",  # Simple JSON object
            r'\{(?:[^{}]|"(?:[^"\\]|\\.)*"|[^{}]*\{[^{}]*\}[^{}]*)*\}',  # Complex JSON with nested objects
            r"\{[^{}]*\}",  # Basic object pattern
            r"\{.*\}",  # Greedy pattern as last resort
        ]

        # Common prefixes/suffixes to strip
        self.strip_prefixes = [
            "```json\n",
            "XX```jsonXX",
            "json\n",
            "```\n",
            "Here is the JSON:\n",
            "JSON:\n",
            "Response:\n",
        ]
        self.strip_suffixes = ["\n```", "```", "\n", " "]

    def xǁRobustJSONParserǁ__init____mutmut_18(self) -> None:
        """Initialize the parser with regex patterns for JSON extraction."""
        # Common patterns for JSON in LLM responses
        self.json_patterns = [
            r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}",  # Simple JSON object
            r'\{(?:[^{}]|"(?:[^"\\]|\\.)*"|[^{}]*\{[^{}]*\}[^{}]*)*\}',  # Complex JSON with nested objects
            r"\{[^{}]*\}",  # Basic object pattern
            r"\{.*\}",  # Greedy pattern as last resort
        ]

        # Common prefixes/suffixes to strip
        self.strip_prefixes = [
            "```json\n",
            "```JSON",
            "json\n",
            "```\n",
            "Here is the JSON:\n",
            "JSON:\n",
            "Response:\n",
        ]
        self.strip_suffixes = ["\n```", "```", "\n", " "]

    def xǁRobustJSONParserǁ__init____mutmut_19(self) -> None:
        """Initialize the parser with regex patterns for JSON extraction."""
        # Common patterns for JSON in LLM responses
        self.json_patterns = [
            r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}",  # Simple JSON object
            r'\{(?:[^{}]|"(?:[^"\\]|\\.)*"|[^{}]*\{[^{}]*\}[^{}]*)*\}',  # Complex JSON with nested objects
            r"\{[^{}]*\}",  # Basic object pattern
            r"\{.*\}",  # Greedy pattern as last resort
        ]

        # Common prefixes/suffixes to strip
        self.strip_prefixes = [
            "```json\n",
            "```json",
            "XXjson\nXX",
            "```\n",
            "Here is the JSON:\n",
            "JSON:\n",
            "Response:\n",
        ]
        self.strip_suffixes = ["\n```", "```", "\n", " "]

    def xǁRobustJSONParserǁ__init____mutmut_20(self) -> None:
        """Initialize the parser with regex patterns for JSON extraction."""
        # Common patterns for JSON in LLM responses
        self.json_patterns = [
            r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}",  # Simple JSON object
            r'\{(?:[^{}]|"(?:[^"\\]|\\.)*"|[^{}]*\{[^{}]*\}[^{}]*)*\}',  # Complex JSON with nested objects
            r"\{[^{}]*\}",  # Basic object pattern
            r"\{.*\}",  # Greedy pattern as last resort
        ]

        # Common prefixes/suffixes to strip
        self.strip_prefixes = [
            "```json\n",
            "```json",
            "JSON\n",
            "```\n",
            "Here is the JSON:\n",
            "JSON:\n",
            "Response:\n",
        ]
        self.strip_suffixes = ["\n```", "```", "\n", " "]

    def xǁRobustJSONParserǁ__init____mutmut_21(self) -> None:
        """Initialize the parser with regex patterns for JSON extraction."""
        # Common patterns for JSON in LLM responses
        self.json_patterns = [
            r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}",  # Simple JSON object
            r'\{(?:[^{}]|"(?:[^"\\]|\\.)*"|[^{}]*\{[^{}]*\}[^{}]*)*\}',  # Complex JSON with nested objects
            r"\{[^{}]*\}",  # Basic object pattern
            r"\{.*\}",  # Greedy pattern as last resort
        ]

        # Common prefixes/suffixes to strip
        self.strip_prefixes = [
            "```json\n",
            "```json",
            "json\n",
            "XX```\nXX",
            "Here is the JSON:\n",
            "JSON:\n",
            "Response:\n",
        ]
        self.strip_suffixes = ["\n```", "```", "\n", " "]

    def xǁRobustJSONParserǁ__init____mutmut_22(self) -> None:
        """Initialize the parser with regex patterns for JSON extraction."""
        # Common patterns for JSON in LLM responses
        self.json_patterns = [
            r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}",  # Simple JSON object
            r'\{(?:[^{}]|"(?:[^"\\]|\\.)*"|[^{}]*\{[^{}]*\}[^{}]*)*\}',  # Complex JSON with nested objects
            r"\{[^{}]*\}",  # Basic object pattern
            r"\{.*\}",  # Greedy pattern as last resort
        ]

        # Common prefixes/suffixes to strip
        self.strip_prefixes = [
            "```json\n",
            "```json",
            "json\n",
            "```\n",
            "XXHere is the JSON:\nXX",
            "JSON:\n",
            "Response:\n",
        ]
        self.strip_suffixes = ["\n```", "```", "\n", " "]

    def xǁRobustJSONParserǁ__init____mutmut_23(self) -> None:
        """Initialize the parser with regex patterns for JSON extraction."""
        # Common patterns for JSON in LLM responses
        self.json_patterns = [
            r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}",  # Simple JSON object
            r'\{(?:[^{}]|"(?:[^"\\]|\\.)*"|[^{}]*\{[^{}]*\}[^{}]*)*\}',  # Complex JSON with nested objects
            r"\{[^{}]*\}",  # Basic object pattern
            r"\{.*\}",  # Greedy pattern as last resort
        ]

        # Common prefixes/suffixes to strip
        self.strip_prefixes = [
            "```json\n",
            "```json",
            "json\n",
            "```\n",
            "here is the json:\n",
            "JSON:\n",
            "Response:\n",
        ]
        self.strip_suffixes = ["\n```", "```", "\n", " "]

    def xǁRobustJSONParserǁ__init____mutmut_24(self) -> None:
        """Initialize the parser with regex patterns for JSON extraction."""
        # Common patterns for JSON in LLM responses
        self.json_patterns = [
            r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}",  # Simple JSON object
            r'\{(?:[^{}]|"(?:[^"\\]|\\.)*"|[^{}]*\{[^{}]*\}[^{}]*)*\}',  # Complex JSON with nested objects
            r"\{[^{}]*\}",  # Basic object pattern
            r"\{.*\}",  # Greedy pattern as last resort
        ]

        # Common prefixes/suffixes to strip
        self.strip_prefixes = [
            "```json\n",
            "```json",
            "json\n",
            "```\n",
            "HERE IS THE JSON:\n",
            "JSON:\n",
            "Response:\n",
        ]
        self.strip_suffixes = ["\n```", "```", "\n", " "]

    def xǁRobustJSONParserǁ__init____mutmut_25(self) -> None:
        """Initialize the parser with regex patterns for JSON extraction."""
        # Common patterns for JSON in LLM responses
        self.json_patterns = [
            r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}",  # Simple JSON object
            r'\{(?:[^{}]|"(?:[^"\\]|\\.)*"|[^{}]*\{[^{}]*\}[^{}]*)*\}',  # Complex JSON with nested objects
            r"\{[^{}]*\}",  # Basic object pattern
            r"\{.*\}",  # Greedy pattern as last resort
        ]

        # Common prefixes/suffixes to strip
        self.strip_prefixes = [
            "```json\n",
            "```json",
            "json\n",
            "```\n",
            "Here is the JSON:\n",
            "XXJSON:\nXX",
            "Response:\n",
        ]
        self.strip_suffixes = ["\n```", "```", "\n", " "]

    def xǁRobustJSONParserǁ__init____mutmut_26(self) -> None:
        """Initialize the parser with regex patterns for JSON extraction."""
        # Common patterns for JSON in LLM responses
        self.json_patterns = [
            r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}",  # Simple JSON object
            r'\{(?:[^{}]|"(?:[^"\\]|\\.)*"|[^{}]*\{[^{}]*\}[^{}]*)*\}',  # Complex JSON with nested objects
            r"\{[^{}]*\}",  # Basic object pattern
            r"\{.*\}",  # Greedy pattern as last resort
        ]

        # Common prefixes/suffixes to strip
        self.strip_prefixes = [
            "```json\n",
            "```json",
            "json\n",
            "```\n",
            "Here is the JSON:\n",
            "json:\n",
            "Response:\n",
        ]
        self.strip_suffixes = ["\n```", "```", "\n", " "]

    def xǁRobustJSONParserǁ__init____mutmut_27(self) -> None:
        """Initialize the parser with regex patterns for JSON extraction."""
        # Common patterns for JSON in LLM responses
        self.json_patterns = [
            r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}",  # Simple JSON object
            r'\{(?:[^{}]|"(?:[^"\\]|\\.)*"|[^{}]*\{[^{}]*\}[^{}]*)*\}',  # Complex JSON with nested objects
            r"\{[^{}]*\}",  # Basic object pattern
            r"\{.*\}",  # Greedy pattern as last resort
        ]

        # Common prefixes/suffixes to strip
        self.strip_prefixes = [
            "```json\n",
            "```json",
            "json\n",
            "```\n",
            "Here is the JSON:\n",
            "JSON:\n",
            "XXResponse:\nXX",
        ]
        self.strip_suffixes = ["\n```", "```", "\n", " "]

    def xǁRobustJSONParserǁ__init____mutmut_28(self) -> None:
        """Initialize the parser with regex patterns for JSON extraction."""
        # Common patterns for JSON in LLM responses
        self.json_patterns = [
            r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}",  # Simple JSON object
            r'\{(?:[^{}]|"(?:[^"\\]|\\.)*"|[^{}]*\{[^{}]*\}[^{}]*)*\}',  # Complex JSON with nested objects
            r"\{[^{}]*\}",  # Basic object pattern
            r"\{.*\}",  # Greedy pattern as last resort
        ]

        # Common prefixes/suffixes to strip
        self.strip_prefixes = [
            "```json\n",
            "```json",
            "json\n",
            "```\n",
            "Here is the JSON:\n",
            "JSON:\n",
            "response:\n",
        ]
        self.strip_suffixes = ["\n```", "```", "\n", " "]

    def xǁRobustJSONParserǁ__init____mutmut_29(self) -> None:
        """Initialize the parser with regex patterns for JSON extraction."""
        # Common patterns for JSON in LLM responses
        self.json_patterns = [
            r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}",  # Simple JSON object
            r'\{(?:[^{}]|"(?:[^"\\]|\\.)*"|[^{}]*\{[^{}]*\}[^{}]*)*\}',  # Complex JSON with nested objects
            r"\{[^{}]*\}",  # Basic object pattern
            r"\{.*\}",  # Greedy pattern as last resort
        ]

        # Common prefixes/suffixes to strip
        self.strip_prefixes = [
            "```json\n",
            "```json",
            "json\n",
            "```\n",
            "Here is the JSON:\n",
            "JSON:\n",
            "RESPONSE:\n",
        ]
        self.strip_suffixes = ["\n```", "```", "\n", " "]

    def xǁRobustJSONParserǁ__init____mutmut_30(self) -> None:
        """Initialize the parser with regex patterns for JSON extraction."""
        # Common patterns for JSON in LLM responses
        self.json_patterns = [
            r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}",  # Simple JSON object
            r'\{(?:[^{}]|"(?:[^"\\]|\\.)*"|[^{}]*\{[^{}]*\}[^{}]*)*\}',  # Complex JSON with nested objects
            r"\{[^{}]*\}",  # Basic object pattern
            r"\{.*\}",  # Greedy pattern as last resort
        ]

        # Common prefixes/suffixes to strip
        self.strip_prefixes = [
            "```json\n",
            "```json",
            "json\n",
            "```\n",
            "Here is the JSON:\n",
            "JSON:\n",
            "Response:\n",
        ]
        self.strip_suffixes = None

    def xǁRobustJSONParserǁ__init____mutmut_31(self) -> None:
        """Initialize the parser with regex patterns for JSON extraction."""
        # Common patterns for JSON in LLM responses
        self.json_patterns = [
            r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}",  # Simple JSON object
            r'\{(?:[^{}]|"(?:[^"\\]|\\.)*"|[^{}]*\{[^{}]*\}[^{}]*)*\}',  # Complex JSON with nested objects
            r"\{[^{}]*\}",  # Basic object pattern
            r"\{.*\}",  # Greedy pattern as last resort
        ]

        # Common prefixes/suffixes to strip
        self.strip_prefixes = [
            "```json\n",
            "```json",
            "json\n",
            "```\n",
            "Here is the JSON:\n",
            "JSON:\n",
            "Response:\n",
        ]
        self.strip_suffixes = ["XX\n```XX", "```", "\n", " "]

    def xǁRobustJSONParserǁ__init____mutmut_32(self) -> None:
        """Initialize the parser with regex patterns for JSON extraction."""
        # Common patterns for JSON in LLM responses
        self.json_patterns = [
            r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}",  # Simple JSON object
            r'\{(?:[^{}]|"(?:[^"\\]|\\.)*"|[^{}]*\{[^{}]*\}[^{}]*)*\}',  # Complex JSON with nested objects
            r"\{[^{}]*\}",  # Basic object pattern
            r"\{.*\}",  # Greedy pattern as last resort
        ]

        # Common prefixes/suffixes to strip
        self.strip_prefixes = [
            "```json\n",
            "```json",
            "json\n",
            "```\n",
            "Here is the JSON:\n",
            "JSON:\n",
            "Response:\n",
        ]
        self.strip_suffixes = ["\n```", "XX```XX", "\n", " "]

    def xǁRobustJSONParserǁ__init____mutmut_33(self) -> None:
        """Initialize the parser with regex patterns for JSON extraction."""
        # Common patterns for JSON in LLM responses
        self.json_patterns = [
            r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}",  # Simple JSON object
            r'\{(?:[^{}]|"(?:[^"\\]|\\.)*"|[^{}]*\{[^{}]*\}[^{}]*)*\}',  # Complex JSON with nested objects
            r"\{[^{}]*\}",  # Basic object pattern
            r"\{.*\}",  # Greedy pattern as last resort
        ]

        # Common prefixes/suffixes to strip
        self.strip_prefixes = [
            "```json\n",
            "```json",
            "json\n",
            "```\n",
            "Here is the JSON:\n",
            "JSON:\n",
            "Response:\n",
        ]
        self.strip_suffixes = ["\n```", "```", "XX\nXX", " "]

    def xǁRobustJSONParserǁ__init____mutmut_34(self) -> None:
        """Initialize the parser with regex patterns for JSON extraction."""
        # Common patterns for JSON in LLM responses
        self.json_patterns = [
            r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}",  # Simple JSON object
            r'\{(?:[^{}]|"(?:[^"\\]|\\.)*"|[^{}]*\{[^{}]*\}[^{}]*)*\}',  # Complex JSON with nested objects
            r"\{[^{}]*\}",  # Basic object pattern
            r"\{.*\}",  # Greedy pattern as last resort
        ]

        # Common prefixes/suffixes to strip
        self.strip_prefixes = [
            "```json\n",
            "```json",
            "json\n",
            "```\n",
            "Here is the JSON:\n",
            "JSON:\n",
            "Response:\n",
        ]
        self.strip_suffixes = ["\n```", "```", "\n", "XX XX"]

    xǁRobustJSONParserǁ__init____mutmut_mutants: ClassVar[MutantDict] = {
        "xǁRobustJSONParserǁ__init____mutmut_1": xǁRobustJSONParserǁ__init____mutmut_1,
        "xǁRobustJSONParserǁ__init____mutmut_2": xǁRobustJSONParserǁ__init____mutmut_2,
        "xǁRobustJSONParserǁ__init____mutmut_3": xǁRobustJSONParserǁ__init____mutmut_3,
        "xǁRobustJSONParserǁ__init____mutmut_4": xǁRobustJSONParserǁ__init____mutmut_4,
        "xǁRobustJSONParserǁ__init____mutmut_5": xǁRobustJSONParserǁ__init____mutmut_5,
        "xǁRobustJSONParserǁ__init____mutmut_6": xǁRobustJSONParserǁ__init____mutmut_6,
        "xǁRobustJSONParserǁ__init____mutmut_7": xǁRobustJSONParserǁ__init____mutmut_7,
        "xǁRobustJSONParserǁ__init____mutmut_8": xǁRobustJSONParserǁ__init____mutmut_8,
        "xǁRobustJSONParserǁ__init____mutmut_9": xǁRobustJSONParserǁ__init____mutmut_9,
        "xǁRobustJSONParserǁ__init____mutmut_10": xǁRobustJSONParserǁ__init____mutmut_10,
        "xǁRobustJSONParserǁ__init____mutmut_11": xǁRobustJSONParserǁ__init____mutmut_11,
        "xǁRobustJSONParserǁ__init____mutmut_12": xǁRobustJSONParserǁ__init____mutmut_12,
        "xǁRobustJSONParserǁ__init____mutmut_13": xǁRobustJSONParserǁ__init____mutmut_13,
        "xǁRobustJSONParserǁ__init____mutmut_14": xǁRobustJSONParserǁ__init____mutmut_14,
        "xǁRobustJSONParserǁ__init____mutmut_15": xǁRobustJSONParserǁ__init____mutmut_15,
        "xǁRobustJSONParserǁ__init____mutmut_16": xǁRobustJSONParserǁ__init____mutmut_16,
        "xǁRobustJSONParserǁ__init____mutmut_17": xǁRobustJSONParserǁ__init____mutmut_17,
        "xǁRobustJSONParserǁ__init____mutmut_18": xǁRobustJSONParserǁ__init____mutmut_18,
        "xǁRobustJSONParserǁ__init____mutmut_19": xǁRobustJSONParserǁ__init____mutmut_19,
        "xǁRobustJSONParserǁ__init____mutmut_20": xǁRobustJSONParserǁ__init____mutmut_20,
        "xǁRobustJSONParserǁ__init____mutmut_21": xǁRobustJSONParserǁ__init____mutmut_21,
        "xǁRobustJSONParserǁ__init____mutmut_22": xǁRobustJSONParserǁ__init____mutmut_22,
        "xǁRobustJSONParserǁ__init____mutmut_23": xǁRobustJSONParserǁ__init____mutmut_23,
        "xǁRobustJSONParserǁ__init____mutmut_24": xǁRobustJSONParserǁ__init____mutmut_24,
        "xǁRobustJSONParserǁ__init____mutmut_25": xǁRobustJSONParserǁ__init____mutmut_25,
        "xǁRobustJSONParserǁ__init____mutmut_26": xǁRobustJSONParserǁ__init____mutmut_26,
        "xǁRobustJSONParserǁ__init____mutmut_27": xǁRobustJSONParserǁ__init____mutmut_27,
        "xǁRobustJSONParserǁ__init____mutmut_28": xǁRobustJSONParserǁ__init____mutmut_28,
        "xǁRobustJSONParserǁ__init____mutmut_29": xǁRobustJSONParserǁ__init____mutmut_29,
        "xǁRobustJSONParserǁ__init____mutmut_30": xǁRobustJSONParserǁ__init____mutmut_30,
        "xǁRobustJSONParserǁ__init____mutmut_31": xǁRobustJSONParserǁ__init____mutmut_31,
        "xǁRobustJSONParserǁ__init____mutmut_32": xǁRobustJSONParserǁ__init____mutmut_32,
        "xǁRobustJSONParserǁ__init____mutmut_33": xǁRobustJSONParserǁ__init____mutmut_33,
        "xǁRobustJSONParserǁ__init____mutmut_34": xǁRobustJSONParserǁ__init____mutmut_34,
    }

    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(
            object.__getattribute__(self, "xǁRobustJSONParserǁ__init____mutmut_orig"),
            object.__getattribute__(
                self, "xǁRobustJSONParserǁ__init____mutmut_mutants"
            ),
            args,
            kwargs,
            self,
        )
        return result

    __init__.__signature__ = _mutmut_signature(xǁRobustJSONParserǁ__init____mutmut_orig)
    xǁRobustJSONParserǁ__init____mutmut_orig.__name__ = "xǁRobustJSONParserǁ__init__"

    def xǁRobustJSONParserǁclean_llm_response__mutmut_orig(self, response: str) -> str:
        """
        Clean LLM response by removing common prefixes/suffixes and normalizing.

        Args:
            response: Raw LLM response text.

        Returns:
            Cleaned response text.
        """
        cleaned = response.strip()

        # Remove common markdown formatting
        if cleaned.startswith("```"):
            cleaned = cleaned.replace("```json", "").replace("```", "").strip()

        # Remove common prefixes
        for prefix in self.strip_prefixes:
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix) :].strip()
                break

        # Remove common suffixes
        for suffix in self.strip_suffixes:
            if cleaned.endswith(suffix):
                cleaned = cleaned[: -len(suffix)].strip()
                break

        return cleaned

    def xǁRobustJSONParserǁclean_llm_response__mutmut_1(self, response: str) -> str:
        """
        Clean LLM response by removing common prefixes/suffixes and normalizing.

        Args:
            response: Raw LLM response text.

        Returns:
            Cleaned response text.
        """
        cleaned = None

        # Remove common markdown formatting
        if cleaned.startswith("```"):
            cleaned = cleaned.replace("```json", "").replace("```", "").strip()

        # Remove common prefixes
        for prefix in self.strip_prefixes:
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix) :].strip()
                break

        # Remove common suffixes
        for suffix in self.strip_suffixes:
            if cleaned.endswith(suffix):
                cleaned = cleaned[: -len(suffix)].strip()
                break

        return cleaned

    def xǁRobustJSONParserǁclean_llm_response__mutmut_2(self, response: str) -> str:
        """
        Clean LLM response by removing common prefixes/suffixes and normalizing.

        Args:
            response: Raw LLM response text.

        Returns:
            Cleaned response text.
        """
        cleaned = response.strip()

        # Remove common markdown formatting
        if cleaned.startswith(None):
            cleaned = cleaned.replace("```json", "").replace("```", "").strip()

        # Remove common prefixes
        for prefix in self.strip_prefixes:
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix) :].strip()
                break

        # Remove common suffixes
        for suffix in self.strip_suffixes:
            if cleaned.endswith(suffix):
                cleaned = cleaned[: -len(suffix)].strip()
                break

        return cleaned

    def xǁRobustJSONParserǁclean_llm_response__mutmut_3(self, response: str) -> str:
        """
        Clean LLM response by removing common prefixes/suffixes and normalizing.

        Args:
            response: Raw LLM response text.

        Returns:
            Cleaned response text.
        """
        cleaned = response.strip()

        # Remove common markdown formatting
        if cleaned.startswith("XX```XX"):
            cleaned = cleaned.replace("```json", "").replace("```", "").strip()

        # Remove common prefixes
        for prefix in self.strip_prefixes:
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix) :].strip()
                break

        # Remove common suffixes
        for suffix in self.strip_suffixes:
            if cleaned.endswith(suffix):
                cleaned = cleaned[: -len(suffix)].strip()
                break

        return cleaned

    def xǁRobustJSONParserǁclean_llm_response__mutmut_4(self, response: str) -> str:
        """
        Clean LLM response by removing common prefixes/suffixes and normalizing.

        Args:
            response: Raw LLM response text.

        Returns:
            Cleaned response text.
        """
        cleaned = response.strip()

        # Remove common markdown formatting
        if cleaned.startswith("```"):
            cleaned = None

        # Remove common prefixes
        for prefix in self.strip_prefixes:
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix) :].strip()
                break

        # Remove common suffixes
        for suffix in self.strip_suffixes:
            if cleaned.endswith(suffix):
                cleaned = cleaned[: -len(suffix)].strip()
                break

        return cleaned

    def xǁRobustJSONParserǁclean_llm_response__mutmut_5(self, response: str) -> str:
        """
        Clean LLM response by removing common prefixes/suffixes and normalizing.

        Args:
            response: Raw LLM response text.

        Returns:
            Cleaned response text.
        """
        cleaned = response.strip()

        # Remove common markdown formatting
        if cleaned.startswith("```"):
            cleaned = cleaned.replace("```json", "").replace(None, "").strip()

        # Remove common prefixes
        for prefix in self.strip_prefixes:
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix) :].strip()
                break

        # Remove common suffixes
        for suffix in self.strip_suffixes:
            if cleaned.endswith(suffix):
                cleaned = cleaned[: -len(suffix)].strip()
                break

        return cleaned

    def xǁRobustJSONParserǁclean_llm_response__mutmut_6(self, response: str) -> str:
        """
        Clean LLM response by removing common prefixes/suffixes and normalizing.

        Args:
            response: Raw LLM response text.

        Returns:
            Cleaned response text.
        """
        cleaned = response.strip()

        # Remove common markdown formatting
        if cleaned.startswith("```"):
            cleaned = cleaned.replace("```json", "").replace("```", None).strip()

        # Remove common prefixes
        for prefix in self.strip_prefixes:
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix) :].strip()
                break

        # Remove common suffixes
        for suffix in self.strip_suffixes:
            if cleaned.endswith(suffix):
                cleaned = cleaned[: -len(suffix)].strip()
                break

        return cleaned

    def xǁRobustJSONParserǁclean_llm_response__mutmut_7(self, response: str) -> str:
        """
        Clean LLM response by removing common prefixes/suffixes and normalizing.

        Args:
            response: Raw LLM response text.

        Returns:
            Cleaned response text.
        """
        cleaned = response.strip()

        # Remove common markdown formatting
        if cleaned.startswith("```"):
            cleaned = cleaned.replace("```json", "").replace("").strip()

        # Remove common prefixes
        for prefix in self.strip_prefixes:
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix) :].strip()
                break

        # Remove common suffixes
        for suffix in self.strip_suffixes:
            if cleaned.endswith(suffix):
                cleaned = cleaned[: -len(suffix)].strip()
                break

        return cleaned

    def xǁRobustJSONParserǁclean_llm_response__mutmut_8(self, response: str) -> str:
        """
        Clean LLM response by removing common prefixes/suffixes and normalizing.

        Args:
            response: Raw LLM response text.

        Returns:
            Cleaned response text.
        """
        cleaned = response.strip()

        # Remove common markdown formatting
        if cleaned.startswith("```"):
            cleaned = (
                cleaned.replace("```json", "")
                .replace(
                    "```",
                )
                .strip()
            )

        # Remove common prefixes
        for prefix in self.strip_prefixes:
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix) :].strip()
                break

        # Remove common suffixes
        for suffix in self.strip_suffixes:
            if cleaned.endswith(suffix):
                cleaned = cleaned[: -len(suffix)].strip()
                break

        return cleaned

    def xǁRobustJSONParserǁclean_llm_response__mutmut_9(self, response: str) -> str:
        """
        Clean LLM response by removing common prefixes/suffixes and normalizing.

        Args:
            response: Raw LLM response text.

        Returns:
            Cleaned response text.
        """
        cleaned = response.strip()

        # Remove common markdown formatting
        if cleaned.startswith("```"):
            cleaned = cleaned.replace(None, "").replace("```", "").strip()

        # Remove common prefixes
        for prefix in self.strip_prefixes:
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix) :].strip()
                break

        # Remove common suffixes
        for suffix in self.strip_suffixes:
            if cleaned.endswith(suffix):
                cleaned = cleaned[: -len(suffix)].strip()
                break

        return cleaned

    def xǁRobustJSONParserǁclean_llm_response__mutmut_10(self, response: str) -> str:
        """
        Clean LLM response by removing common prefixes/suffixes and normalizing.

        Args:
            response: Raw LLM response text.

        Returns:
            Cleaned response text.
        """
        cleaned = response.strip()

        # Remove common markdown formatting
        if cleaned.startswith("```"):
            cleaned = cleaned.replace("```json", None).replace("```", "").strip()

        # Remove common prefixes
        for prefix in self.strip_prefixes:
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix) :].strip()
                break

        # Remove common suffixes
        for suffix in self.strip_suffixes:
            if cleaned.endswith(suffix):
                cleaned = cleaned[: -len(suffix)].strip()
                break

        return cleaned

    def xǁRobustJSONParserǁclean_llm_response__mutmut_11(self, response: str) -> str:
        """
        Clean LLM response by removing common prefixes/suffixes and normalizing.

        Args:
            response: Raw LLM response text.

        Returns:
            Cleaned response text.
        """
        cleaned = response.strip()

        # Remove common markdown formatting
        if cleaned.startswith("```"):
            cleaned = cleaned.replace("").replace("```", "").strip()

        # Remove common prefixes
        for prefix in self.strip_prefixes:
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix) :].strip()
                break

        # Remove common suffixes
        for suffix in self.strip_suffixes:
            if cleaned.endswith(suffix):
                cleaned = cleaned[: -len(suffix)].strip()
                break

        return cleaned

    def xǁRobustJSONParserǁclean_llm_response__mutmut_12(self, response: str) -> str:
        """
        Clean LLM response by removing common prefixes/suffixes and normalizing.

        Args:
            response: Raw LLM response text.

        Returns:
            Cleaned response text.
        """
        cleaned = response.strip()

        # Remove common markdown formatting
        if cleaned.startswith("```"):
            cleaned = (
                cleaned.replace(
                    "```json",
                )
                .replace("```", "")
                .strip()
            )

        # Remove common prefixes
        for prefix in self.strip_prefixes:
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix) :].strip()
                break

        # Remove common suffixes
        for suffix in self.strip_suffixes:
            if cleaned.endswith(suffix):
                cleaned = cleaned[: -len(suffix)].strip()
                break

        return cleaned

    def xǁRobustJSONParserǁclean_llm_response__mutmut_13(self, response: str) -> str:
        """
        Clean LLM response by removing common prefixes/suffixes and normalizing.

        Args:
            response: Raw LLM response text.

        Returns:
            Cleaned response text.
        """
        cleaned = response.strip()

        # Remove common markdown formatting
        if cleaned.startswith("```"):
            cleaned = cleaned.replace("XX```jsonXX", "").replace("```", "").strip()

        # Remove common prefixes
        for prefix in self.strip_prefixes:
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix) :].strip()
                break

        # Remove common suffixes
        for suffix in self.strip_suffixes:
            if cleaned.endswith(suffix):
                cleaned = cleaned[: -len(suffix)].strip()
                break

        return cleaned

    def xǁRobustJSONParserǁclean_llm_response__mutmut_14(self, response: str) -> str:
        """
        Clean LLM response by removing common prefixes/suffixes and normalizing.

        Args:
            response: Raw LLM response text.

        Returns:
            Cleaned response text.
        """
        cleaned = response.strip()

        # Remove common markdown formatting
        if cleaned.startswith("```"):
            cleaned = cleaned.replace("```JSON", "").replace("```", "").strip()

        # Remove common prefixes
        for prefix in self.strip_prefixes:
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix) :].strip()
                break

        # Remove common suffixes
        for suffix in self.strip_suffixes:
            if cleaned.endswith(suffix):
                cleaned = cleaned[: -len(suffix)].strip()
                break

        return cleaned

    def xǁRobustJSONParserǁclean_llm_response__mutmut_15(self, response: str) -> str:
        """
        Clean LLM response by removing common prefixes/suffixes and normalizing.

        Args:
            response: Raw LLM response text.

        Returns:
            Cleaned response text.
        """
        cleaned = response.strip()

        # Remove common markdown formatting
        if cleaned.startswith("```"):
            cleaned = cleaned.replace("```json", "XXXX").replace("```", "").strip()

        # Remove common prefixes
        for prefix in self.strip_prefixes:
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix) :].strip()
                break

        # Remove common suffixes
        for suffix in self.strip_suffixes:
            if cleaned.endswith(suffix):
                cleaned = cleaned[: -len(suffix)].strip()
                break

        return cleaned

    def xǁRobustJSONParserǁclean_llm_response__mutmut_16(self, response: str) -> str:
        """
        Clean LLM response by removing common prefixes/suffixes and normalizing.

        Args:
            response: Raw LLM response text.

        Returns:
            Cleaned response text.
        """
        cleaned = response.strip()

        # Remove common markdown formatting
        if cleaned.startswith("```"):
            cleaned = cleaned.replace("```json", "").replace("XX```XX", "").strip()

        # Remove common prefixes
        for prefix in self.strip_prefixes:
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix) :].strip()
                break

        # Remove common suffixes
        for suffix in self.strip_suffixes:
            if cleaned.endswith(suffix):
                cleaned = cleaned[: -len(suffix)].strip()
                break

        return cleaned

    def xǁRobustJSONParserǁclean_llm_response__mutmut_17(self, response: str) -> str:
        """
        Clean LLM response by removing common prefixes/suffixes and normalizing.

        Args:
            response: Raw LLM response text.

        Returns:
            Cleaned response text.
        """
        cleaned = response.strip()

        # Remove common markdown formatting
        if cleaned.startswith("```"):
            cleaned = cleaned.replace("```json", "").replace("```", "XXXX").strip()

        # Remove common prefixes
        for prefix in self.strip_prefixes:
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix) :].strip()
                break

        # Remove common suffixes
        for suffix in self.strip_suffixes:
            if cleaned.endswith(suffix):
                cleaned = cleaned[: -len(suffix)].strip()
                break

        return cleaned

    def xǁRobustJSONParserǁclean_llm_response__mutmut_18(self, response: str) -> str:
        """
        Clean LLM response by removing common prefixes/suffixes and normalizing.

        Args:
            response: Raw LLM response text.

        Returns:
            Cleaned response text.
        """
        cleaned = response.strip()

        # Remove common markdown formatting
        if cleaned.startswith("```"):
            cleaned = cleaned.replace("```json", "").replace("```", "").strip()

        # Remove common prefixes
        for prefix in self.strip_prefixes:
            if cleaned.startswith(None):
                cleaned = cleaned[len(prefix) :].strip()
                break

        # Remove common suffixes
        for suffix in self.strip_suffixes:
            if cleaned.endswith(suffix):
                cleaned = cleaned[: -len(suffix)].strip()
                break

        return cleaned

    def xǁRobustJSONParserǁclean_llm_response__mutmut_19(self, response: str) -> str:
        """
        Clean LLM response by removing common prefixes/suffixes and normalizing.

        Args:
            response: Raw LLM response text.

        Returns:
            Cleaned response text.
        """
        cleaned = response.strip()

        # Remove common markdown formatting
        if cleaned.startswith("```"):
            cleaned = cleaned.replace("```json", "").replace("```", "").strip()

        # Remove common prefixes
        for prefix in self.strip_prefixes:
            if cleaned.startswith(prefix):
                cleaned = None
                break

        # Remove common suffixes
        for suffix in self.strip_suffixes:
            if cleaned.endswith(suffix):
                cleaned = cleaned[: -len(suffix)].strip()
                break

        return cleaned

    def xǁRobustJSONParserǁclean_llm_response__mutmut_20(self, response: str) -> str:
        """
        Clean LLM response by removing common prefixes/suffixes and normalizing.

        Args:
            response: Raw LLM response text.

        Returns:
            Cleaned response text.
        """
        cleaned = response.strip()

        # Remove common markdown formatting
        if cleaned.startswith("```"):
            cleaned = cleaned.replace("```json", "").replace("```", "").strip()

        # Remove common prefixes
        for prefix in self.strip_prefixes:
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix) :].strip()
                return

        # Remove common suffixes
        for suffix in self.strip_suffixes:
            if cleaned.endswith(suffix):
                cleaned = cleaned[: -len(suffix)].strip()
                break

        return cleaned

    def xǁRobustJSONParserǁclean_llm_response__mutmut_21(self, response: str) -> str:
        """
        Clean LLM response by removing common prefixes/suffixes and normalizing.

        Args:
            response: Raw LLM response text.

        Returns:
            Cleaned response text.
        """
        cleaned = response.strip()

        # Remove common markdown formatting
        if cleaned.startswith("```"):
            cleaned = cleaned.replace("```json", "").replace("```", "").strip()

        # Remove common prefixes
        for prefix in self.strip_prefixes:
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix) :].strip()
                break

        # Remove common suffixes
        for suffix in self.strip_suffixes:
            if cleaned.endswith(None):
                cleaned = cleaned[: -len(suffix)].strip()
                break

        return cleaned

    def xǁRobustJSONParserǁclean_llm_response__mutmut_22(self, response: str) -> str:
        """
        Clean LLM response by removing common prefixes/suffixes and normalizing.

        Args:
            response: Raw LLM response text.

        Returns:
            Cleaned response text.
        """
        cleaned = response.strip()

        # Remove common markdown formatting
        if cleaned.startswith("```"):
            cleaned = cleaned.replace("```json", "").replace("```", "").strip()

        # Remove common prefixes
        for prefix in self.strip_prefixes:
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix) :].strip()
                break

        # Remove common suffixes
        for suffix in self.strip_suffixes:
            if cleaned.endswith(suffix):
                cleaned = None
                break

        return cleaned

    def xǁRobustJSONParserǁclean_llm_response__mutmut_23(self, response: str) -> str:
        """
        Clean LLM response by removing common prefixes/suffixes and normalizing.

        Args:
            response: Raw LLM response text.

        Returns:
            Cleaned response text.
        """
        cleaned = response.strip()

        # Remove common markdown formatting
        if cleaned.startswith("```"):
            cleaned = cleaned.replace("```json", "").replace("```", "").strip()

        # Remove common prefixes
        for prefix in self.strip_prefixes:
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix) :].strip()
                break

        # Remove common suffixes
        for suffix in self.strip_suffixes:
            if cleaned.endswith(suffix):
                cleaned = cleaned[: +len(suffix)].strip()
                break

        return cleaned

    def xǁRobustJSONParserǁclean_llm_response__mutmut_24(self, response: str) -> str:
        """
        Clean LLM response by removing common prefixes/suffixes and normalizing.

        Args:
            response: Raw LLM response text.

        Returns:
            Cleaned response text.
        """
        cleaned = response.strip()

        # Remove common markdown formatting
        if cleaned.startswith("```"):
            cleaned = cleaned.replace("```json", "").replace("```", "").strip()

        # Remove common prefixes
        for prefix in self.strip_prefixes:
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix) :].strip()
                break

        # Remove common suffixes
        for suffix in self.strip_suffixes:
            if cleaned.endswith(suffix):
                cleaned = cleaned[: -len(suffix)].strip()
                return

        return cleaned

    xǁRobustJSONParserǁclean_llm_response__mutmut_mutants: ClassVar[MutantDict] = {
        "xǁRobustJSONParserǁclean_llm_response__mutmut_1": xǁRobustJSONParserǁclean_llm_response__mutmut_1,
        "xǁRobustJSONParserǁclean_llm_response__mutmut_2": xǁRobustJSONParserǁclean_llm_response__mutmut_2,
        "xǁRobustJSONParserǁclean_llm_response__mutmut_3": xǁRobustJSONParserǁclean_llm_response__mutmut_3,
        "xǁRobustJSONParserǁclean_llm_response__mutmut_4": xǁRobustJSONParserǁclean_llm_response__mutmut_4,
        "xǁRobustJSONParserǁclean_llm_response__mutmut_5": xǁRobustJSONParserǁclean_llm_response__mutmut_5,
        "xǁRobustJSONParserǁclean_llm_response__mutmut_6": xǁRobustJSONParserǁclean_llm_response__mutmut_6,
        "xǁRobustJSONParserǁclean_llm_response__mutmut_7": xǁRobustJSONParserǁclean_llm_response__mutmut_7,
        "xǁRobustJSONParserǁclean_llm_response__mutmut_8": xǁRobustJSONParserǁclean_llm_response__mutmut_8,
        "xǁRobustJSONParserǁclean_llm_response__mutmut_9": xǁRobustJSONParserǁclean_llm_response__mutmut_9,
        "xǁRobustJSONParserǁclean_llm_response__mutmut_10": xǁRobustJSONParserǁclean_llm_response__mutmut_10,
        "xǁRobustJSONParserǁclean_llm_response__mutmut_11": xǁRobustJSONParserǁclean_llm_response__mutmut_11,
        "xǁRobustJSONParserǁclean_llm_response__mutmut_12": xǁRobustJSONParserǁclean_llm_response__mutmut_12,
        "xǁRobustJSONParserǁclean_llm_response__mutmut_13": xǁRobustJSONParserǁclean_llm_response__mutmut_13,
        "xǁRobustJSONParserǁclean_llm_response__mutmut_14": xǁRobustJSONParserǁclean_llm_response__mutmut_14,
        "xǁRobustJSONParserǁclean_llm_response__mutmut_15": xǁRobustJSONParserǁclean_llm_response__mutmut_15,
        "xǁRobustJSONParserǁclean_llm_response__mutmut_16": xǁRobustJSONParserǁclean_llm_response__mutmut_16,
        "xǁRobustJSONParserǁclean_llm_response__mutmut_17": xǁRobustJSONParserǁclean_llm_response__mutmut_17,
        "xǁRobustJSONParserǁclean_llm_response__mutmut_18": xǁRobustJSONParserǁclean_llm_response__mutmut_18,
        "xǁRobustJSONParserǁclean_llm_response__mutmut_19": xǁRobustJSONParserǁclean_llm_response__mutmut_19,
        "xǁRobustJSONParserǁclean_llm_response__mutmut_20": xǁRobustJSONParserǁclean_llm_response__mutmut_20,
        "xǁRobustJSONParserǁclean_llm_response__mutmut_21": xǁRobustJSONParserǁclean_llm_response__mutmut_21,
        "xǁRobustJSONParserǁclean_llm_response__mutmut_22": xǁRobustJSONParserǁclean_llm_response__mutmut_22,
        "xǁRobustJSONParserǁclean_llm_response__mutmut_23": xǁRobustJSONParserǁclean_llm_response__mutmut_23,
        "xǁRobustJSONParserǁclean_llm_response__mutmut_24": xǁRobustJSONParserǁclean_llm_response__mutmut_24,
    }

    def clean_llm_response(self, *args, **kwargs):
        result = _mutmut_trampoline(
            object.__getattribute__(
                self, "xǁRobustJSONParserǁclean_llm_response__mutmut_orig"
            ),
            object.__getattribute__(
                self, "xǁRobustJSONParserǁclean_llm_response__mutmut_mutants"
            ),
            args,
            kwargs,
            self,
        )
        return result

    clean_llm_response.__signature__ = _mutmut_signature(
        xǁRobustJSONParserǁclean_llm_response__mutmut_orig
    )
    xǁRobustJSONParserǁclean_llm_response__mutmut_orig.__name__ = (
        "xǁRobustJSONParserǁclean_llm_response"
    )

    def xǁRobustJSONParserǁextract_json_from_text__mutmut_orig(
        self, text: str
    ) -> List[str]:
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

    def xǁRobustJSONParserǁextract_json_from_text__mutmut_1(
        self, text: str
    ) -> List[str]:
        """
        Extract all JSON-like strings from text using multiple regex patterns.

        Args:
            text: Text to search for JSON objects.

        Returns:
            List of potential JSON strings found in the text.
        """
        candidates = None

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

    def xǁRobustJSONParserǁextract_json_from_text__mutmut_2(
        self, text: str
    ) -> List[str]:
        """
        Extract all JSON-like strings from text using multiple regex patterns.

        Args:
            text: Text to search for JSON objects.

        Returns:
            List of potential JSON strings found in the text.
        """
        candidates = []

        for pattern in self.json_patterns:
            matches = None
            candidates.extend(matches)

        # Remove duplicates while preserving order
        seen = set()
        unique_candidates = []
        for candidate in candidates:
            if candidate not in seen:
                seen.add(candidate)
                unique_candidates.append(candidate)

        return unique_candidates

    def xǁRobustJSONParserǁextract_json_from_text__mutmut_3(
        self, text: str
    ) -> List[str]:
        """
        Extract all JSON-like strings from text using multiple regex patterns.

        Args:
            text: Text to search for JSON objects.

        Returns:
            List of potential JSON strings found in the text.
        """
        candidates = []

        for pattern in self.json_patterns:
            matches = re.findall(None, text, re.DOTALL)
            candidates.extend(matches)

        # Remove duplicates while preserving order
        seen = set()
        unique_candidates = []
        for candidate in candidates:
            if candidate not in seen:
                seen.add(candidate)
                unique_candidates.append(candidate)

        return unique_candidates

    def xǁRobustJSONParserǁextract_json_from_text__mutmut_4(
        self, text: str
    ) -> List[str]:
        """
        Extract all JSON-like strings from text using multiple regex patterns.

        Args:
            text: Text to search for JSON objects.

        Returns:
            List of potential JSON strings found in the text.
        """
        candidates = []

        for pattern in self.json_patterns:
            matches = re.findall(pattern, None, re.DOTALL)
            candidates.extend(matches)

        # Remove duplicates while preserving order
        seen = set()
        unique_candidates = []
        for candidate in candidates:
            if candidate not in seen:
                seen.add(candidate)
                unique_candidates.append(candidate)

        return unique_candidates

    def xǁRobustJSONParserǁextract_json_from_text__mutmut_5(
        self, text: str
    ) -> List[str]:
        """
        Extract all JSON-like strings from text using multiple regex patterns.

        Args:
            text: Text to search for JSON objects.

        Returns:
            List of potential JSON strings found in the text.
        """
        candidates = []

        for pattern in self.json_patterns:
            matches = re.findall(pattern, text, None)
            candidates.extend(matches)

        # Remove duplicates while preserving order
        seen = set()
        unique_candidates = []
        for candidate in candidates:
            if candidate not in seen:
                seen.add(candidate)
                unique_candidates.append(candidate)

        return unique_candidates

    def xǁRobustJSONParserǁextract_json_from_text__mutmut_6(
        self, text: str
    ) -> List[str]:
        """
        Extract all JSON-like strings from text using multiple regex patterns.

        Args:
            text: Text to search for JSON objects.

        Returns:
            List of potential JSON strings found in the text.
        """
        candidates = []

        for pattern in self.json_patterns:
            matches = re.findall(text, re.DOTALL)
            candidates.extend(matches)

        # Remove duplicates while preserving order
        seen = set()
        unique_candidates = []
        for candidate in candidates:
            if candidate not in seen:
                seen.add(candidate)
                unique_candidates.append(candidate)

        return unique_candidates

    def xǁRobustJSONParserǁextract_json_from_text__mutmut_7(
        self, text: str
    ) -> List[str]:
        """
        Extract all JSON-like strings from text using multiple regex patterns.

        Args:
            text: Text to search for JSON objects.

        Returns:
            List of potential JSON strings found in the text.
        """
        candidates = []

        for pattern in self.json_patterns:
            matches = re.findall(pattern, re.DOTALL)
            candidates.extend(matches)

        # Remove duplicates while preserving order
        seen = set()
        unique_candidates = []
        for candidate in candidates:
            if candidate not in seen:
                seen.add(candidate)
                unique_candidates.append(candidate)

        return unique_candidates

    def xǁRobustJSONParserǁextract_json_from_text__mutmut_8(
        self, text: str
    ) -> List[str]:
        """
        Extract all JSON-like strings from text using multiple regex patterns.

        Args:
            text: Text to search for JSON objects.

        Returns:
            List of potential JSON strings found in the text.
        """
        candidates = []

        for pattern in self.json_patterns:
            matches = re.findall(
                pattern,
                text,
            )
            candidates.extend(matches)

        # Remove duplicates while preserving order
        seen = set()
        unique_candidates = []
        for candidate in candidates:
            if candidate not in seen:
                seen.add(candidate)
                unique_candidates.append(candidate)

        return unique_candidates

    def xǁRobustJSONParserǁextract_json_from_text__mutmut_9(
        self, text: str
    ) -> List[str]:
        """
        Extract all JSON-like strings from text using multiple regex patterns.

        Args:
            text: Text to search for JSON objects.

        Returns:
            List of potential JSON strings found in the text.
        """
        candidates = []

        for pattern in self.json_patterns:
            re.findall(pattern, text, re.DOTALL)
            candidates.extend(None)

        # Remove duplicates while preserving order
        seen = set()
        unique_candidates = []
        for candidate in candidates:
            if candidate not in seen:
                seen.add(candidate)
                unique_candidates.append(candidate)

        return unique_candidates

    def xǁRobustJSONParserǁextract_json_from_text__mutmut_10(
        self, text: str
    ) -> List[str]:
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
        seen = None
        unique_candidates = []
        for candidate in candidates:
            if candidate not in seen:
                seen.add(candidate)
                unique_candidates.append(candidate)

        return unique_candidates

    def xǁRobustJSONParserǁextract_json_from_text__mutmut_11(
        self, text: str
    ) -> List[str]:
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
        unique_candidates = None
        for candidate in candidates:
            if candidate not in seen:
                seen.add(candidate)
                unique_candidates.append(candidate)

        return unique_candidates

    def xǁRobustJSONParserǁextract_json_from_text__mutmut_12(
        self, text: str
    ) -> List[str]:
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
            if candidate in seen:
                seen.add(candidate)
                unique_candidates.append(candidate)

        return unique_candidates

    def xǁRobustJSONParserǁextract_json_from_text__mutmut_13(
        self, text: str
    ) -> List[str]:
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
                seen.add(None)
                unique_candidates.append(candidate)

        return unique_candidates

    def xǁRobustJSONParserǁextract_json_from_text__mutmut_14(
        self, text: str
    ) -> List[str]:
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
                unique_candidates.append(None)

        return unique_candidates

    xǁRobustJSONParserǁextract_json_from_text__mutmut_mutants: ClassVar[MutantDict] = {
        "xǁRobustJSONParserǁextract_json_from_text__mutmut_1": xǁRobustJSONParserǁextract_json_from_text__mutmut_1,
        "xǁRobustJSONParserǁextract_json_from_text__mutmut_2": xǁRobustJSONParserǁextract_json_from_text__mutmut_2,
        "xǁRobustJSONParserǁextract_json_from_text__mutmut_3": xǁRobustJSONParserǁextract_json_from_text__mutmut_3,
        "xǁRobustJSONParserǁextract_json_from_text__mutmut_4": xǁRobustJSONParserǁextract_json_from_text__mutmut_4,
        "xǁRobustJSONParserǁextract_json_from_text__mutmut_5": xǁRobustJSONParserǁextract_json_from_text__mutmut_5,
        "xǁRobustJSONParserǁextract_json_from_text__mutmut_6": xǁRobustJSONParserǁextract_json_from_text__mutmut_6,
        "xǁRobustJSONParserǁextract_json_from_text__mutmut_7": xǁRobustJSONParserǁextract_json_from_text__mutmut_7,
        "xǁRobustJSONParserǁextract_json_from_text__mutmut_8": xǁRobustJSONParserǁextract_json_from_text__mutmut_8,
        "xǁRobustJSONParserǁextract_json_from_text__mutmut_9": xǁRobustJSONParserǁextract_json_from_text__mutmut_9,
        "xǁRobustJSONParserǁextract_json_from_text__mutmut_10": xǁRobustJSONParserǁextract_json_from_text__mutmut_10,
        "xǁRobustJSONParserǁextract_json_from_text__mutmut_11": xǁRobustJSONParserǁextract_json_from_text__mutmut_11,
        "xǁRobustJSONParserǁextract_json_from_text__mutmut_12": xǁRobustJSONParserǁextract_json_from_text__mutmut_12,
        "xǁRobustJSONParserǁextract_json_from_text__mutmut_13": xǁRobustJSONParserǁextract_json_from_text__mutmut_13,
        "xǁRobustJSONParserǁextract_json_from_text__mutmut_14": xǁRobustJSONParserǁextract_json_from_text__mutmut_14,
    }

    def extract_json_from_text(self, *args, **kwargs):
        result = _mutmut_trampoline(
            object.__getattribute__(
                self, "xǁRobustJSONParserǁextract_json_from_text__mutmut_orig"
            ),
            object.__getattribute__(
                self, "xǁRobustJSONParserǁextract_json_from_text__mutmut_mutants"
            ),
            args,
            kwargs,
            self,
        )
        return result

    extract_json_from_text.__signature__ = _mutmut_signature(
        xǁRobustJSONParserǁextract_json_from_text__mutmut_orig
    )
    xǁRobustJSONParserǁextract_json_from_text__mutmut_orig.__name__ = (
        "xǁRobustJSONParserǁextract_json_from_text"
    )

    def xǁRobustJSONParserǁparse_json_safe__mutmut_orig(
        self, json_str: str
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
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
            logger.debug(
                f"Failed to parse JSON: {error_msg}. Input: {json_str[:100]}..."
            )
            return None, error_msg

    def xǁRobustJSONParserǁparse_json_safe__mutmut_1(
        self, json_str: str
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Safely parse a JSON string with comprehensive error handling.

        Args:
            json_str: JSON string to parse.

        Returns:
            Tuple of (parsed_dict, error_message). Parsed dict is None if parsing failed.
        """
        if not json_str and not json_str.strip():
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
            logger.debug(
                f"Failed to parse JSON: {error_msg}. Input: {json_str[:100]}..."
            )
            return None, error_msg

    def xǁRobustJSONParserǁparse_json_safe__mutmut_2(
        self, json_str: str
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Safely parse a JSON string with comprehensive error handling.

        Args:
            json_str: JSON string to parse.

        Returns:
            Tuple of (parsed_dict, error_message). Parsed dict is None if parsing failed.
        """
        if json_str or not json_str.strip():
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
            logger.debug(
                f"Failed to parse JSON: {error_msg}. Input: {json_str[:100]}..."
            )
            return None, error_msg

    def xǁRobustJSONParserǁparse_json_safe__mutmut_3(
        self, json_str: str
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Safely parse a JSON string with comprehensive error handling.

        Args:
            json_str: JSON string to parse.

        Returns:
            Tuple of (parsed_dict, error_message). Parsed dict is None if parsing failed.
        """
        if not json_str or json_str.strip():
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
            logger.debug(
                f"Failed to parse JSON: {error_msg}. Input: {json_str[:100]}..."
            )
            return None, error_msg

    def xǁRobustJSONParserǁparse_json_safe__mutmut_4(
        self, json_str: str
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Safely parse a JSON string with comprehensive error handling.

        Args:
            json_str: JSON string to parse.

        Returns:
            Tuple of (parsed_dict, error_message). Parsed dict is None if parsing failed.
        """
        if not json_str or not json_str.strip():
            return None, "XXEmpty JSON stringXX"

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
            logger.debug(
                f"Failed to parse JSON: {error_msg}. Input: {json_str[:100]}..."
            )
            return None, error_msg

    def xǁRobustJSONParserǁparse_json_safe__mutmut_5(
        self, json_str: str
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Safely parse a JSON string with comprehensive error handling.

        Args:
            json_str: JSON string to parse.

        Returns:
            Tuple of (parsed_dict, error_message). Parsed dict is None if parsing failed.
        """
        if not json_str or not json_str.strip():
            return None, "empty json string"

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
            logger.debug(
                f"Failed to parse JSON: {error_msg}. Input: {json_str[:100]}..."
            )
            return None, error_msg

    def xǁRobustJSONParserǁparse_json_safe__mutmut_6(
        self, json_str: str
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Safely parse a JSON string with comprehensive error handling.

        Args:
            json_str: JSON string to parse.

        Returns:
            Tuple of (parsed_dict, error_message). Parsed dict is None if parsing failed.
        """
        if not json_str or not json_str.strip():
            return None, "EMPTY JSON STRING"

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
            logger.debug(
                f"Failed to parse JSON: {error_msg}. Input: {json_str[:100]}..."
            )
            return None, error_msg

    def xǁRobustJSONParserǁparse_json_safe__mutmut_7(
        self, json_str: str
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
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
                    return orjson.loads(None), None
                except orjson.JSONDecodeError:
                    pass

            # Fall back to standard json library
            return json.loads(json_str), None

        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            error_msg = f"JSON decode error: {str(e)}"
            logger.debug(
                f"Failed to parse JSON: {error_msg}. Input: {json_str[:100]}..."
            )
            return None, error_msg

    def xǁRobustJSONParserǁparse_json_safe__mutmut_8(
        self, json_str: str
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
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
            return json.loads(None), None

        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            error_msg = f"JSON decode error: {str(e)}"
            logger.debug(
                f"Failed to parse JSON: {error_msg}. Input: {json_str[:100]}..."
            )
            return None, error_msg

    def xǁRobustJSONParserǁparse_json_safe__mutmut_9(
        self, json_str: str
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
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
            error_msg = None
            logger.debug(
                f"Failed to parse JSON: {error_msg}. Input: {json_str[:100]}..."
            )
            return None, error_msg

    def xǁRobustJSONParserǁparse_json_safe__mutmut_10(
        self, json_str: str
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
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
            error_msg = f"JSON decode error: {str(None)}"
            logger.debug(
                f"Failed to parse JSON: {error_msg}. Input: {json_str[:100]}..."
            )
            return None, error_msg

    def xǁRobustJSONParserǁparse_json_safe__mutmut_11(
        self, json_str: str
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
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
            logger.debug(None)
            return None, error_msg

    def xǁRobustJSONParserǁparse_json_safe__mutmut_12(
        self, json_str: str
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
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
            logger.debug(
                f"Failed to parse JSON: {error_msg}. Input: {json_str[:101]}..."
            )
            return None, error_msg

    xǁRobustJSONParserǁparse_json_safe__mutmut_mutants: ClassVar[MutantDict] = {
        "xǁRobustJSONParserǁparse_json_safe__mutmut_1": xǁRobustJSONParserǁparse_json_safe__mutmut_1,
        "xǁRobustJSONParserǁparse_json_safe__mutmut_2": xǁRobustJSONParserǁparse_json_safe__mutmut_2,
        "xǁRobustJSONParserǁparse_json_safe__mutmut_3": xǁRobustJSONParserǁparse_json_safe__mutmut_3,
        "xǁRobustJSONParserǁparse_json_safe__mutmut_4": xǁRobustJSONParserǁparse_json_safe__mutmut_4,
        "xǁRobustJSONParserǁparse_json_safe__mutmut_5": xǁRobustJSONParserǁparse_json_safe__mutmut_5,
        "xǁRobustJSONParserǁparse_json_safe__mutmut_6": xǁRobustJSONParserǁparse_json_safe__mutmut_6,
        "xǁRobustJSONParserǁparse_json_safe__mutmut_7": xǁRobustJSONParserǁparse_json_safe__mutmut_7,
        "xǁRobustJSONParserǁparse_json_safe__mutmut_8": xǁRobustJSONParserǁparse_json_safe__mutmut_8,
        "xǁRobustJSONParserǁparse_json_safe__mutmut_9": xǁRobustJSONParserǁparse_json_safe__mutmut_9,
        "xǁRobustJSONParserǁparse_json_safe__mutmut_10": xǁRobustJSONParserǁparse_json_safe__mutmut_10,
        "xǁRobustJSONParserǁparse_json_safe__mutmut_11": xǁRobustJSONParserǁparse_json_safe__mutmut_11,
        "xǁRobustJSONParserǁparse_json_safe__mutmut_12": xǁRobustJSONParserǁparse_json_safe__mutmut_12,
    }

    def parse_json_safe(self, *args, **kwargs):
        result = _mutmut_trampoline(
            object.__getattribute__(
                self, "xǁRobustJSONParserǁparse_json_safe__mutmut_orig"
            ),
            object.__getattribute__(
                self, "xǁRobustJSONParserǁparse_json_safe__mutmut_mutants"
            ),
            args,
            kwargs,
            self,
        )
        return result

    parse_json_safe.__signature__ = _mutmut_signature(
        xǁRobustJSONParserǁparse_json_safe__mutmut_orig
    )
    xǁRobustJSONParserǁparse_json_safe__mutmut_orig.__name__ = (
        "xǁRobustJSONParserǁparse_json_safe"
    )

    def xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_orig(
        self, json_str: str
    ) -> List[str]:
        """
        Attempt to fix common JSON formatting issues.

        Args:
            json_str: Malformed JSON string.

        Returns:
            List of potentially fixed JSON strings to try.
        """
        fixes = [json_str]  # Original first

        # Fix trailing commas
        fixed = re.sub(r",(\s*[}\]])", r"\1", json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Fix single quotes (though this might break some strings)
        if "'" in json_str and json_str.count("'") > json_str.count('"'):
            fixed = json_str.replace("'", '"')
            fixes.append(fixed)

        # Fix missing quotes around keys
        fixed = re.sub(r"(\w+):", r'"\1":', json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Try to balance braces if they're unbalanced
        open_braces = json_str.count("{")
        close_braces = json_str.count("}")
        if open_braces > close_braces:
            fixes.append(json_str + "}")
        elif close_braces > open_braces:
            fixes.append("{" + json_str)

        return fixes

    def xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_1(
        self, json_str: str
    ) -> List[str]:
        """
        Attempt to fix common JSON formatting issues.

        Args:
            json_str: Malformed JSON string.

        Returns:
            List of potentially fixed JSON strings to try.
        """
        fixes = None  # Original first

        # Fix trailing commas
        fixed = re.sub(r",(\s*[}\]])", r"\1", json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Fix single quotes (though this might break some strings)
        if "'" in json_str and json_str.count("'") > json_str.count('"'):
            fixed = json_str.replace("'", '"')
            fixes.append(fixed)

        # Fix missing quotes around keys
        fixed = re.sub(r"(\w+):", r'"\1":', json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Try to balance braces if they're unbalanced
        open_braces = json_str.count("{")
        close_braces = json_str.count("}")
        if open_braces > close_braces:
            fixes.append(json_str + "}")
        elif close_braces > open_braces:
            fixes.append("{" + json_str)

        return fixes

    def xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_2(
        self, json_str: str
    ) -> List[str]:
        """
        Attempt to fix common JSON formatting issues.

        Args:
            json_str: Malformed JSON string.

        Returns:
            List of potentially fixed JSON strings to try.
        """
        fixes = [json_str]  # Original first

        # Fix trailing commas
        fixed = None
        if fixed != json_str:
            fixes.append(fixed)

        # Fix single quotes (though this might break some strings)
        if "'" in json_str and json_str.count("'") > json_str.count('"'):
            fixed = json_str.replace("'", '"')
            fixes.append(fixed)

        # Fix missing quotes around keys
        fixed = re.sub(r"(\w+):", r'"\1":', json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Try to balance braces if they're unbalanced
        open_braces = json_str.count("{")
        close_braces = json_str.count("}")
        if open_braces > close_braces:
            fixes.append(json_str + "}")
        elif close_braces > open_braces:
            fixes.append("{" + json_str)

        return fixes

    def xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_3(
        self, json_str: str
    ) -> List[str]:
        """
        Attempt to fix common JSON formatting issues.

        Args:
            json_str: Malformed JSON string.

        Returns:
            List of potentially fixed JSON strings to try.
        """
        fixes = [json_str]  # Original first

        # Fix trailing commas
        fixed = re.sub(None, r"\1", json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Fix single quotes (though this might break some strings)
        if "'" in json_str and json_str.count("'") > json_str.count('"'):
            fixed = json_str.replace("'", '"')
            fixes.append(fixed)

        # Fix missing quotes around keys
        fixed = re.sub(r"(\w+):", r'"\1":', json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Try to balance braces if they're unbalanced
        open_braces = json_str.count("{")
        close_braces = json_str.count("}")
        if open_braces > close_braces:
            fixes.append(json_str + "}")
        elif close_braces > open_braces:
            fixes.append("{" + json_str)

        return fixes

    def xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_4(
        self, json_str: str
    ) -> List[str]:
        """
        Attempt to fix common JSON formatting issues.

        Args:
            json_str: Malformed JSON string.

        Returns:
            List of potentially fixed JSON strings to try.
        """
        fixes = [json_str]  # Original first

        # Fix trailing commas
        fixed = re.sub(r",(\s*[}\]])", None, json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Fix single quotes (though this might break some strings)
        if "'" in json_str and json_str.count("'") > json_str.count('"'):
            fixed = json_str.replace("'", '"')
            fixes.append(fixed)

        # Fix missing quotes around keys
        fixed = re.sub(r"(\w+):", r'"\1":', json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Try to balance braces if they're unbalanced
        open_braces = json_str.count("{")
        close_braces = json_str.count("}")
        if open_braces > close_braces:
            fixes.append(json_str + "}")
        elif close_braces > open_braces:
            fixes.append("{" + json_str)

        return fixes

    def xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_5(
        self, json_str: str
    ) -> List[str]:
        """
        Attempt to fix common JSON formatting issues.

        Args:
            json_str: Malformed JSON string.

        Returns:
            List of potentially fixed JSON strings to try.
        """
        fixes = [json_str]  # Original first

        # Fix trailing commas
        fixed = re.sub(r",(\s*[}\]])", r"\1", None)
        if fixed != json_str:
            fixes.append(fixed)

        # Fix single quotes (though this might break some strings)
        if "'" in json_str and json_str.count("'") > json_str.count('"'):
            fixed = json_str.replace("'", '"')
            fixes.append(fixed)

        # Fix missing quotes around keys
        fixed = re.sub(r"(\w+):", r'"\1":', json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Try to balance braces if they're unbalanced
        open_braces = json_str.count("{")
        close_braces = json_str.count("}")
        if open_braces > close_braces:
            fixes.append(json_str + "}")
        elif close_braces > open_braces:
            fixes.append("{" + json_str)

        return fixes

    def xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_6(
        self, json_str: str
    ) -> List[str]:
        """
        Attempt to fix common JSON formatting issues.

        Args:
            json_str: Malformed JSON string.

        Returns:
            List of potentially fixed JSON strings to try.
        """
        fixes = [json_str]  # Original first

        # Fix trailing commas
        fixed = re.sub(r"\1", json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Fix single quotes (though this might break some strings)
        if "'" in json_str and json_str.count("'") > json_str.count('"'):
            fixed = json_str.replace("'", '"')
            fixes.append(fixed)

        # Fix missing quotes around keys
        fixed = re.sub(r"(\w+):", r'"\1":', json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Try to balance braces if they're unbalanced
        open_braces = json_str.count("{")
        close_braces = json_str.count("}")
        if open_braces > close_braces:
            fixes.append(json_str + "}")
        elif close_braces > open_braces:
            fixes.append("{" + json_str)

        return fixes

    def xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_7(
        self, json_str: str
    ) -> List[str]:
        """
        Attempt to fix common JSON formatting issues.

        Args:
            json_str: Malformed JSON string.

        Returns:
            List of potentially fixed JSON strings to try.
        """
        fixes = [json_str]  # Original first

        # Fix trailing commas
        fixed = re.sub(r",(\s*[}\]])", json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Fix single quotes (though this might break some strings)
        if "'" in json_str and json_str.count("'") > json_str.count('"'):
            fixed = json_str.replace("'", '"')
            fixes.append(fixed)

        # Fix missing quotes around keys
        fixed = re.sub(r"(\w+):", r'"\1":', json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Try to balance braces if they're unbalanced
        open_braces = json_str.count("{")
        close_braces = json_str.count("}")
        if open_braces > close_braces:
            fixes.append(json_str + "}")
        elif close_braces > open_braces:
            fixes.append("{" + json_str)

        return fixes

    def xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_8(
        self, json_str: str
    ) -> List[str]:
        """
        Attempt to fix common JSON formatting issues.

        Args:
            json_str: Malformed JSON string.

        Returns:
            List of potentially fixed JSON strings to try.
        """
        fixes = [json_str]  # Original first

        # Fix trailing commas
        fixed = re.sub(
            r",(\s*[}\]])",
            r"\1",
        )
        if fixed != json_str:
            fixes.append(fixed)

        # Fix single quotes (though this might break some strings)
        if "'" in json_str and json_str.count("'") > json_str.count('"'):
            fixed = json_str.replace("'", '"')
            fixes.append(fixed)

        # Fix missing quotes around keys
        fixed = re.sub(r"(\w+):", r'"\1":', json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Try to balance braces if they're unbalanced
        open_braces = json_str.count("{")
        close_braces = json_str.count("}")
        if open_braces > close_braces:
            fixes.append(json_str + "}")
        elif close_braces > open_braces:
            fixes.append("{" + json_str)

        return fixes

    def xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_9(
        self, json_str: str
    ) -> List[str]:
        """
        Attempt to fix common JSON formatting issues.

        Args:
            json_str: Malformed JSON string.

        Returns:
            List of potentially fixed JSON strings to try.
        """
        fixes = [json_str]  # Original first

        # Fix trailing commas
        fixed = re.sub(r"XX,(\s*[}\]])XX", r"\1", json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Fix single quotes (though this might break some strings)
        if "'" in json_str and json_str.count("'") > json_str.count('"'):
            fixed = json_str.replace("'", '"')
            fixes.append(fixed)

        # Fix missing quotes around keys
        fixed = re.sub(r"(\w+):", r'"\1":', json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Try to balance braces if they're unbalanced
        open_braces = json_str.count("{")
        close_braces = json_str.count("}")
        if open_braces > close_braces:
            fixes.append(json_str + "}")
        elif close_braces > open_braces:
            fixes.append("{" + json_str)

        return fixes

    def xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_10(
        self, json_str: str
    ) -> List[str]:
        """
        Attempt to fix common JSON formatting issues.

        Args:
            json_str: Malformed JSON string.

        Returns:
            List of potentially fixed JSON strings to try.
        """
        fixes = [json_str]  # Original first

        # Fix trailing commas
        fixed = re.sub(r",(\s*[}\]])", r"\1", json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Fix single quotes (though this might break some strings)
        if "'" in json_str and json_str.count("'") > json_str.count('"'):
            fixed = json_str.replace("'", '"')
            fixes.append(fixed)

        # Fix missing quotes around keys
        fixed = re.sub(r"(\w+):", r'"\1":', json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Try to balance braces if they're unbalanced
        open_braces = json_str.count("{")
        close_braces = json_str.count("}")
        if open_braces > close_braces:
            fixes.append(json_str + "}")
        elif close_braces > open_braces:
            fixes.append("{" + json_str)

        return fixes

    def xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_11(
        self, json_str: str
    ) -> List[str]:
        """
        Attempt to fix common JSON formatting issues.

        Args:
            json_str: Malformed JSON string.

        Returns:
            List of potentially fixed JSON strings to try.
        """
        fixes = [json_str]  # Original first

        # Fix trailing commas
        fixed = re.sub(r",(\s*[}\]])", r"\1", json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Fix single quotes (though this might break some strings)
        if "'" in json_str and json_str.count("'") > json_str.count('"'):
            fixed = json_str.replace("'", '"')
            fixes.append(fixed)

        # Fix missing quotes around keys
        fixed = re.sub(r"(\w+):", r'"\1":', json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Try to balance braces if they're unbalanced
        open_braces = json_str.count("{")
        close_braces = json_str.count("}")
        if open_braces > close_braces:
            fixes.append(json_str + "}")
        elif close_braces > open_braces:
            fixes.append("{" + json_str)

        return fixes

    def xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_12(
        self, json_str: str
    ) -> List[str]:
        """
        Attempt to fix common JSON formatting issues.

        Args:
            json_str: Malformed JSON string.

        Returns:
            List of potentially fixed JSON strings to try.
        """
        fixes = [json_str]  # Original first

        # Fix trailing commas
        fixed = re.sub(r",(\s*[}\]])", r"XX\1XX", json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Fix single quotes (though this might break some strings)
        if "'" in json_str and json_str.count("'") > json_str.count('"'):
            fixed = json_str.replace("'", '"')
            fixes.append(fixed)

        # Fix missing quotes around keys
        fixed = re.sub(r"(\w+):", r'"\1":', json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Try to balance braces if they're unbalanced
        open_braces = json_str.count("{")
        close_braces = json_str.count("}")
        if open_braces > close_braces:
            fixes.append(json_str + "}")
        elif close_braces > open_braces:
            fixes.append("{" + json_str)

        return fixes

    def xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_13(
        self, json_str: str
    ) -> List[str]:
        """
        Attempt to fix common JSON formatting issues.

        Args:
            json_str: Malformed JSON string.

        Returns:
            List of potentially fixed JSON strings to try.
        """
        fixes = [json_str]  # Original first

        # Fix trailing commas
        fixed = re.sub(r",(\s*[}\]])", r"\1", json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Fix single quotes (though this might break some strings)
        if "'" in json_str and json_str.count("'") > json_str.count('"'):
            fixed = json_str.replace("'", '"')
            fixes.append(fixed)

        # Fix missing quotes around keys
        fixed = re.sub(r"(\w+):", r'"\1":', json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Try to balance braces if they're unbalanced
        open_braces = json_str.count("{")
        close_braces = json_str.count("}")
        if open_braces > close_braces:
            fixes.append(json_str + "}")
        elif close_braces > open_braces:
            fixes.append("{" + json_str)

        return fixes

    def xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_14(
        self, json_str: str
    ) -> List[str]:
        """
        Attempt to fix common JSON formatting issues.

        Args:
            json_str: Malformed JSON string.

        Returns:
            List of potentially fixed JSON strings to try.
        """
        fixes = [json_str]  # Original first

        # Fix trailing commas
        fixed = re.sub(r",(\s*[}\]])", r"\1", json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Fix single quotes (though this might break some strings)
        if "'" in json_str and json_str.count("'") > json_str.count('"'):
            fixed = json_str.replace("'", '"')
            fixes.append(fixed)

        # Fix missing quotes around keys
        fixed = re.sub(r"(\w+):", r'"\1":', json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Try to balance braces if they're unbalanced
        open_braces = json_str.count("{")
        close_braces = json_str.count("}")
        if open_braces > close_braces:
            fixes.append(json_str + "}")
        elif close_braces > open_braces:
            fixes.append("{" + json_str)

        return fixes

    def xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_15(
        self, json_str: str
    ) -> List[str]:
        """
        Attempt to fix common JSON formatting issues.

        Args:
            json_str: Malformed JSON string.

        Returns:
            List of potentially fixed JSON strings to try.
        """
        fixes = [json_str]  # Original first

        # Fix trailing commas
        fixed = re.sub(r",(\s*[}\]])", r"\1", json_str)
        if fixed == json_str:
            fixes.append(fixed)

        # Fix single quotes (though this might break some strings)
        if "'" in json_str and json_str.count("'") > json_str.count('"'):
            fixed = json_str.replace("'", '"')
            fixes.append(fixed)

        # Fix missing quotes around keys
        fixed = re.sub(r"(\w+):", r'"\1":', json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Try to balance braces if they're unbalanced
        open_braces = json_str.count("{")
        close_braces = json_str.count("}")
        if open_braces > close_braces:
            fixes.append(json_str + "}")
        elif close_braces > open_braces:
            fixes.append("{" + json_str)

        return fixes

    def xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_16(
        self, json_str: str
    ) -> List[str]:
        """
        Attempt to fix common JSON formatting issues.

        Args:
            json_str: Malformed JSON string.

        Returns:
            List of potentially fixed JSON strings to try.
        """
        fixes = [json_str]  # Original first

        # Fix trailing commas
        fixed = re.sub(r",(\s*[}\]])", r"\1", json_str)
        if fixed != json_str:
            fixes.append(None)

        # Fix single quotes (though this might break some strings)
        if "'" in json_str and json_str.count("'") > json_str.count('"'):
            fixed = json_str.replace("'", '"')
            fixes.append(fixed)

        # Fix missing quotes around keys
        fixed = re.sub(r"(\w+):", r'"\1":', json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Try to balance braces if they're unbalanced
        open_braces = json_str.count("{")
        close_braces = json_str.count("}")
        if open_braces > close_braces:
            fixes.append(json_str + "}")
        elif close_braces > open_braces:
            fixes.append("{" + json_str)

        return fixes

    def xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_17(
        self, json_str: str
    ) -> List[str]:
        """
        Attempt to fix common JSON formatting issues.

        Args:
            json_str: Malformed JSON string.

        Returns:
            List of potentially fixed JSON strings to try.
        """
        fixes = [json_str]  # Original first

        # Fix trailing commas
        fixed = re.sub(r",(\s*[}\]])", r"\1", json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Fix single quotes (though this might break some strings)
        if "'" in json_str or json_str.count("'") > json_str.count('"'):
            fixed = json_str.replace("'", '"')
            fixes.append(fixed)

        # Fix missing quotes around keys
        fixed = re.sub(r"(\w+):", r'"\1":', json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Try to balance braces if they're unbalanced
        open_braces = json_str.count("{")
        close_braces = json_str.count("}")
        if open_braces > close_braces:
            fixes.append(json_str + "}")
        elif close_braces > open_braces:
            fixes.append("{" + json_str)

        return fixes

    def xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_18(
        self, json_str: str
    ) -> List[str]:
        """
        Attempt to fix common JSON formatting issues.

        Args:
            json_str: Malformed JSON string.

        Returns:
            List of potentially fixed JSON strings to try.
        """
        fixes = [json_str]  # Original first

        # Fix trailing commas
        fixed = re.sub(r",(\s*[}\]])", r"\1", json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Fix single quotes (though this might break some strings)
        if "XX'XX" in json_str and json_str.count("'") > json_str.count('"'):
            fixed = json_str.replace("'", '"')
            fixes.append(fixed)

        # Fix missing quotes around keys
        fixed = re.sub(r"(\w+):", r'"\1":', json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Try to balance braces if they're unbalanced
        open_braces = json_str.count("{")
        close_braces = json_str.count("}")
        if open_braces > close_braces:
            fixes.append(json_str + "}")
        elif close_braces > open_braces:
            fixes.append("{" + json_str)

        return fixes

    def xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_19(
        self, json_str: str
    ) -> List[str]:
        """
        Attempt to fix common JSON formatting issues.

        Args:
            json_str: Malformed JSON string.

        Returns:
            List of potentially fixed JSON strings to try.
        """
        fixes = [json_str]  # Original first

        # Fix trailing commas
        fixed = re.sub(r",(\s*[}\]])", r"\1", json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Fix single quotes (though this might break some strings)
        if "'" not in json_str and json_str.count("'") > json_str.count('"'):
            fixed = json_str.replace("'", '"')
            fixes.append(fixed)

        # Fix missing quotes around keys
        fixed = re.sub(r"(\w+):", r'"\1":', json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Try to balance braces if they're unbalanced
        open_braces = json_str.count("{")
        close_braces = json_str.count("}")
        if open_braces > close_braces:
            fixes.append(json_str + "}")
        elif close_braces > open_braces:
            fixes.append("{" + json_str)

        return fixes

    def xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_20(
        self, json_str: str
    ) -> List[str]:
        """
        Attempt to fix common JSON formatting issues.

        Args:
            json_str: Malformed JSON string.

        Returns:
            List of potentially fixed JSON strings to try.
        """
        fixes = [json_str]  # Original first

        # Fix trailing commas
        fixed = re.sub(r",(\s*[}\]])", r"\1", json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Fix single quotes (though this might break some strings)
        if "'" in json_str and json_str.count(None) > json_str.count('"'):
            fixed = json_str.replace("'", '"')
            fixes.append(fixed)

        # Fix missing quotes around keys
        fixed = re.sub(r"(\w+):", r'"\1":', json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Try to balance braces if they're unbalanced
        open_braces = json_str.count("{")
        close_braces = json_str.count("}")
        if open_braces > close_braces:
            fixes.append(json_str + "}")
        elif close_braces > open_braces:
            fixes.append("{" + json_str)

        return fixes

    def xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_21(
        self, json_str: str
    ) -> List[str]:
        """
        Attempt to fix common JSON formatting issues.

        Args:
            json_str: Malformed JSON string.

        Returns:
            List of potentially fixed JSON strings to try.
        """
        fixes = [json_str]  # Original first

        # Fix trailing commas
        fixed = re.sub(r",(\s*[}\]])", r"\1", json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Fix single quotes (though this might break some strings)
        if "'" in json_str and json_str.count("XX'XX") > json_str.count('"'):
            fixed = json_str.replace("'", '"')
            fixes.append(fixed)

        # Fix missing quotes around keys
        fixed = re.sub(r"(\w+):", r'"\1":', json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Try to balance braces if they're unbalanced
        open_braces = json_str.count("{")
        close_braces = json_str.count("}")
        if open_braces > close_braces:
            fixes.append(json_str + "}")
        elif close_braces > open_braces:
            fixes.append("{" + json_str)

        return fixes

    def xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_22(
        self, json_str: str
    ) -> List[str]:
        """
        Attempt to fix common JSON formatting issues.

        Args:
            json_str: Malformed JSON string.

        Returns:
            List of potentially fixed JSON strings to try.
        """
        fixes = [json_str]  # Original first

        # Fix trailing commas
        fixed = re.sub(r",(\s*[}\]])", r"\1", json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Fix single quotes (though this might break some strings)
        if "'" in json_str and json_str.count("'") >= json_str.count('"'):
            fixed = json_str.replace("'", '"')
            fixes.append(fixed)

        # Fix missing quotes around keys
        fixed = re.sub(r"(\w+):", r'"\1":', json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Try to balance braces if they're unbalanced
        open_braces = json_str.count("{")
        close_braces = json_str.count("}")
        if open_braces > close_braces:
            fixes.append(json_str + "}")
        elif close_braces > open_braces:
            fixes.append("{" + json_str)

        return fixes

    def xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_23(
        self, json_str: str
    ) -> List[str]:
        """
        Attempt to fix common JSON formatting issues.

        Args:
            json_str: Malformed JSON string.

        Returns:
            List of potentially fixed JSON strings to try.
        """
        fixes = [json_str]  # Original first

        # Fix trailing commas
        fixed = re.sub(r",(\s*[}\]])", r"\1", json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Fix single quotes (though this might break some strings)
        if "'" in json_str and json_str.count("'") > json_str.count(None):
            fixed = json_str.replace("'", '"')
            fixes.append(fixed)

        # Fix missing quotes around keys
        fixed = re.sub(r"(\w+):", r'"\1":', json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Try to balance braces if they're unbalanced
        open_braces = json_str.count("{")
        close_braces = json_str.count("}")
        if open_braces > close_braces:
            fixes.append(json_str + "}")
        elif close_braces > open_braces:
            fixes.append("{" + json_str)

        return fixes

    def xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_24(
        self, json_str: str
    ) -> List[str]:
        """
        Attempt to fix common JSON formatting issues.

        Args:
            json_str: Malformed JSON string.

        Returns:
            List of potentially fixed JSON strings to try.
        """
        fixes = [json_str]  # Original first

        # Fix trailing commas
        fixed = re.sub(r",(\s*[}\]])", r"\1", json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Fix single quotes (though this might break some strings)
        if "'" in json_str and json_str.count("'") > json_str.count('XX"XX'):
            fixed = json_str.replace("'", '"')
            fixes.append(fixed)

        # Fix missing quotes around keys
        fixed = re.sub(r"(\w+):", r'"\1":', json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Try to balance braces if they're unbalanced
        open_braces = json_str.count("{")
        close_braces = json_str.count("}")
        if open_braces > close_braces:
            fixes.append(json_str + "}")
        elif close_braces > open_braces:
            fixes.append("{" + json_str)

        return fixes

    def xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_25(
        self, json_str: str
    ) -> List[str]:
        """
        Attempt to fix common JSON formatting issues.

        Args:
            json_str: Malformed JSON string.

        Returns:
            List of potentially fixed JSON strings to try.
        """
        fixes = [json_str]  # Original first

        # Fix trailing commas
        fixed = re.sub(r",(\s*[}\]])", r"\1", json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Fix single quotes (though this might break some strings)
        if "'" in json_str and json_str.count("'") > json_str.count('"'):
            fixed = None
            fixes.append(fixed)

        # Fix missing quotes around keys
        fixed = re.sub(r"(\w+):", r'"\1":', json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Try to balance braces if they're unbalanced
        open_braces = json_str.count("{")
        close_braces = json_str.count("}")
        if open_braces > close_braces:
            fixes.append(json_str + "}")
        elif close_braces > open_braces:
            fixes.append("{" + json_str)

        return fixes

    def xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_26(
        self, json_str: str
    ) -> List[str]:
        """
        Attempt to fix common JSON formatting issues.

        Args:
            json_str: Malformed JSON string.

        Returns:
            List of potentially fixed JSON strings to try.
        """
        fixes = [json_str]  # Original first

        # Fix trailing commas
        fixed = re.sub(r",(\s*[}\]])", r"\1", json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Fix single quotes (though this might break some strings)
        if "'" in json_str and json_str.count("'") > json_str.count('"'):
            fixed = json_str.replace(None, '"')
            fixes.append(fixed)

        # Fix missing quotes around keys
        fixed = re.sub(r"(\w+):", r'"\1":', json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Try to balance braces if they're unbalanced
        open_braces = json_str.count("{")
        close_braces = json_str.count("}")
        if open_braces > close_braces:
            fixes.append(json_str + "}")
        elif close_braces > open_braces:
            fixes.append("{" + json_str)

        return fixes

    def xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_27(
        self, json_str: str
    ) -> List[str]:
        """
        Attempt to fix common JSON formatting issues.

        Args:
            json_str: Malformed JSON string.

        Returns:
            List of potentially fixed JSON strings to try.
        """
        fixes = [json_str]  # Original first

        # Fix trailing commas
        fixed = re.sub(r",(\s*[}\]])", r"\1", json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Fix single quotes (though this might break some strings)
        if "'" in json_str and json_str.count("'") > json_str.count('"'):
            fixed = json_str.replace("'", None)
            fixes.append(fixed)

        # Fix missing quotes around keys
        fixed = re.sub(r"(\w+):", r'"\1":', json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Try to balance braces if they're unbalanced
        open_braces = json_str.count("{")
        close_braces = json_str.count("}")
        if open_braces > close_braces:
            fixes.append(json_str + "}")
        elif close_braces > open_braces:
            fixes.append("{" + json_str)

        return fixes

    def xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_28(
        self, json_str: str
    ) -> List[str]:
        """
        Attempt to fix common JSON formatting issues.

        Args:
            json_str: Malformed JSON string.

        Returns:
            List of potentially fixed JSON strings to try.
        """
        fixes = [json_str]  # Original first

        # Fix trailing commas
        fixed = re.sub(r",(\s*[}\]])", r"\1", json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Fix single quotes (though this might break some strings)
        if "'" in json_str and json_str.count("'") > json_str.count('"'):
            fixed = json_str.replace('"')
            fixes.append(fixed)

        # Fix missing quotes around keys
        fixed = re.sub(r"(\w+):", r'"\1":', json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Try to balance braces if they're unbalanced
        open_braces = json_str.count("{")
        close_braces = json_str.count("}")
        if open_braces > close_braces:
            fixes.append(json_str + "}")
        elif close_braces > open_braces:
            fixes.append("{" + json_str)

        return fixes

    def xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_29(
        self, json_str: str
    ) -> List[str]:
        """
        Attempt to fix common JSON formatting issues.

        Args:
            json_str: Malformed JSON string.

        Returns:
            List of potentially fixed JSON strings to try.
        """
        fixes = [json_str]  # Original first

        # Fix trailing commas
        fixed = re.sub(r",(\s*[}\]])", r"\1", json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Fix single quotes (though this might break some strings)
        if "'" in json_str and json_str.count("'") > json_str.count('"'):
            fixed = json_str.replace(
                "'",
            )
            fixes.append(fixed)

        # Fix missing quotes around keys
        fixed = re.sub(r"(\w+):", r'"\1":', json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Try to balance braces if they're unbalanced
        open_braces = json_str.count("{")
        close_braces = json_str.count("}")
        if open_braces > close_braces:
            fixes.append(json_str + "}")
        elif close_braces > open_braces:
            fixes.append("{" + json_str)

        return fixes

    def xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_30(
        self, json_str: str
    ) -> List[str]:
        """
        Attempt to fix common JSON formatting issues.

        Args:
            json_str: Malformed JSON string.

        Returns:
            List of potentially fixed JSON strings to try.
        """
        fixes = [json_str]  # Original first

        # Fix trailing commas
        fixed = re.sub(r",(\s*[}\]])", r"\1", json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Fix single quotes (though this might break some strings)
        if "'" in json_str and json_str.count("'") > json_str.count('"'):
            fixed = json_str.replace("XX'XX", '"')
            fixes.append(fixed)

        # Fix missing quotes around keys
        fixed = re.sub(r"(\w+):", r'"\1":', json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Try to balance braces if they're unbalanced
        open_braces = json_str.count("{")
        close_braces = json_str.count("}")
        if open_braces > close_braces:
            fixes.append(json_str + "}")
        elif close_braces > open_braces:
            fixes.append("{" + json_str)

        return fixes

    def xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_31(
        self, json_str: str
    ) -> List[str]:
        """
        Attempt to fix common JSON formatting issues.

        Args:
            json_str: Malformed JSON string.

        Returns:
            List of potentially fixed JSON strings to try.
        """
        fixes = [json_str]  # Original first

        # Fix trailing commas
        fixed = re.sub(r",(\s*[}\]])", r"\1", json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Fix single quotes (though this might break some strings)
        if "'" in json_str and json_str.count("'") > json_str.count('"'):
            fixed = json_str.replace("'", 'XX"XX')
            fixes.append(fixed)

        # Fix missing quotes around keys
        fixed = re.sub(r"(\w+):", r'"\1":', json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Try to balance braces if they're unbalanced
        open_braces = json_str.count("{")
        close_braces = json_str.count("}")
        if open_braces > close_braces:
            fixes.append(json_str + "}")
        elif close_braces > open_braces:
            fixes.append("{" + json_str)

        return fixes

    def xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_32(
        self, json_str: str
    ) -> List[str]:
        """
        Attempt to fix common JSON formatting issues.

        Args:
            json_str: Malformed JSON string.

        Returns:
            List of potentially fixed JSON strings to try.
        """
        fixes = [json_str]  # Original first

        # Fix trailing commas
        fixed = re.sub(r",(\s*[}\]])", r"\1", json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Fix single quotes (though this might break some strings)
        if "'" in json_str and json_str.count("'") > json_str.count('"'):
            fixed = json_str.replace("'", '"')
            fixes.append(None)

        # Fix missing quotes around keys
        fixed = re.sub(r"(\w+):", r'"\1":', json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Try to balance braces if they're unbalanced
        open_braces = json_str.count("{")
        close_braces = json_str.count("}")
        if open_braces > close_braces:
            fixes.append(json_str + "}")
        elif close_braces > open_braces:
            fixes.append("{" + json_str)

        return fixes

    def xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_33(
        self, json_str: str
    ) -> List[str]:
        """
        Attempt to fix common JSON formatting issues.

        Args:
            json_str: Malformed JSON string.

        Returns:
            List of potentially fixed JSON strings to try.
        """
        fixes = [json_str]  # Original first

        # Fix trailing commas
        fixed = re.sub(r",(\s*[}\]])", r"\1", json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Fix single quotes (though this might break some strings)
        if "'" in json_str and json_str.count("'") > json_str.count('"'):
            fixed = json_str.replace("'", '"')
            fixes.append(fixed)

        # Fix missing quotes around keys
        fixed = None
        if fixed != json_str:
            fixes.append(fixed)

        # Try to balance braces if they're unbalanced
        open_braces = json_str.count("{")
        close_braces = json_str.count("}")
        if open_braces > close_braces:
            fixes.append(json_str + "}")
        elif close_braces > open_braces:
            fixes.append("{" + json_str)

        return fixes

    def xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_34(
        self, json_str: str
    ) -> List[str]:
        """
        Attempt to fix common JSON formatting issues.

        Args:
            json_str: Malformed JSON string.

        Returns:
            List of potentially fixed JSON strings to try.
        """
        fixes = [json_str]  # Original first

        # Fix trailing commas
        fixed = re.sub(r",(\s*[}\]])", r"\1", json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Fix single quotes (though this might break some strings)
        if "'" in json_str and json_str.count("'") > json_str.count('"'):
            fixed = json_str.replace("'", '"')
            fixes.append(fixed)

        # Fix missing quotes around keys
        fixed = re.sub(None, r'"\1":', json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Try to balance braces if they're unbalanced
        open_braces = json_str.count("{")
        close_braces = json_str.count("}")
        if open_braces > close_braces:
            fixes.append(json_str + "}")
        elif close_braces > open_braces:
            fixes.append("{" + json_str)

        return fixes

    def xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_35(
        self, json_str: str
    ) -> List[str]:
        """
        Attempt to fix common JSON formatting issues.

        Args:
            json_str: Malformed JSON string.

        Returns:
            List of potentially fixed JSON strings to try.
        """
        fixes = [json_str]  # Original first

        # Fix trailing commas
        fixed = re.sub(r",(\s*[}\]])", r"\1", json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Fix single quotes (though this might break some strings)
        if "'" in json_str and json_str.count("'") > json_str.count('"'):
            fixed = json_str.replace("'", '"')
            fixes.append(fixed)

        # Fix missing quotes around keys
        fixed = re.sub(r"(\w+):", None, json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Try to balance braces if they're unbalanced
        open_braces = json_str.count("{")
        close_braces = json_str.count("}")
        if open_braces > close_braces:
            fixes.append(json_str + "}")
        elif close_braces > open_braces:
            fixes.append("{" + json_str)

        return fixes

    def xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_36(
        self, json_str: str
    ) -> List[str]:
        """
        Attempt to fix common JSON formatting issues.

        Args:
            json_str: Malformed JSON string.

        Returns:
            List of potentially fixed JSON strings to try.
        """
        fixes = [json_str]  # Original first

        # Fix trailing commas
        fixed = re.sub(r",(\s*[}\]])", r"\1", json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Fix single quotes (though this might break some strings)
        if "'" in json_str and json_str.count("'") > json_str.count('"'):
            fixed = json_str.replace("'", '"')
            fixes.append(fixed)

        # Fix missing quotes around keys
        fixed = re.sub(r"(\w+):", r'"\1":', None)
        if fixed != json_str:
            fixes.append(fixed)

        # Try to balance braces if they're unbalanced
        open_braces = json_str.count("{")
        close_braces = json_str.count("}")
        if open_braces > close_braces:
            fixes.append(json_str + "}")
        elif close_braces > open_braces:
            fixes.append("{" + json_str)

        return fixes

    def xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_37(
        self, json_str: str
    ) -> List[str]:
        """
        Attempt to fix common JSON formatting issues.

        Args:
            json_str: Malformed JSON string.

        Returns:
            List of potentially fixed JSON strings to try.
        """
        fixes = [json_str]  # Original first

        # Fix trailing commas
        fixed = re.sub(r",(\s*[}\]])", r"\1", json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Fix single quotes (though this might break some strings)
        if "'" in json_str and json_str.count("'") > json_str.count('"'):
            fixed = json_str.replace("'", '"')
            fixes.append(fixed)

        # Fix missing quotes around keys
        fixed = re.sub(r'"\1":', json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Try to balance braces if they're unbalanced
        open_braces = json_str.count("{")
        close_braces = json_str.count("}")
        if open_braces > close_braces:
            fixes.append(json_str + "}")
        elif close_braces > open_braces:
            fixes.append("{" + json_str)

        return fixes

    def xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_38(
        self, json_str: str
    ) -> List[str]:
        """
        Attempt to fix common JSON formatting issues.

        Args:
            json_str: Malformed JSON string.

        Returns:
            List of potentially fixed JSON strings to try.
        """
        fixes = [json_str]  # Original first

        # Fix trailing commas
        fixed = re.sub(r",(\s*[}\]])", r"\1", json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Fix single quotes (though this might break some strings)
        if "'" in json_str and json_str.count("'") > json_str.count('"'):
            fixed = json_str.replace("'", '"')
            fixes.append(fixed)

        # Fix missing quotes around keys
        fixed = re.sub(r"(\w+):", json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Try to balance braces if they're unbalanced
        open_braces = json_str.count("{")
        close_braces = json_str.count("}")
        if open_braces > close_braces:
            fixes.append(json_str + "}")
        elif close_braces > open_braces:
            fixes.append("{" + json_str)

        return fixes

    def xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_39(
        self, json_str: str
    ) -> List[str]:
        """
        Attempt to fix common JSON formatting issues.

        Args:
            json_str: Malformed JSON string.

        Returns:
            List of potentially fixed JSON strings to try.
        """
        fixes = [json_str]  # Original first

        # Fix trailing commas
        fixed = re.sub(r",(\s*[}\]])", r"\1", json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Fix single quotes (though this might break some strings)
        if "'" in json_str and json_str.count("'") > json_str.count('"'):
            fixed = json_str.replace("'", '"')
            fixes.append(fixed)

        # Fix missing quotes around keys
        fixed = re.sub(
            r"(\w+):",
            r'"\1":',
        )
        if fixed != json_str:
            fixes.append(fixed)

        # Try to balance braces if they're unbalanced
        open_braces = json_str.count("{")
        close_braces = json_str.count("}")
        if open_braces > close_braces:
            fixes.append(json_str + "}")
        elif close_braces > open_braces:
            fixes.append("{" + json_str)

        return fixes

    def xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_40(
        self, json_str: str
    ) -> List[str]:
        """
        Attempt to fix common JSON formatting issues.

        Args:
            json_str: Malformed JSON string.

        Returns:
            List of potentially fixed JSON strings to try.
        """
        fixes = [json_str]  # Original first

        # Fix trailing commas
        fixed = re.sub(r",(\s*[}\]])", r"\1", json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Fix single quotes (though this might break some strings)
        if "'" in json_str and json_str.count("'") > json_str.count('"'):
            fixed = json_str.replace("'", '"')
            fixes.append(fixed)

        # Fix missing quotes around keys
        fixed = re.sub(r"XX(\w+):XX", r'"\1":', json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Try to balance braces if they're unbalanced
        open_braces = json_str.count("{")
        close_braces = json_str.count("}")
        if open_braces > close_braces:
            fixes.append(json_str + "}")
        elif close_braces > open_braces:
            fixes.append("{" + json_str)

        return fixes

    def xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_41(
        self, json_str: str
    ) -> List[str]:
        """
        Attempt to fix common JSON formatting issues.

        Args:
            json_str: Malformed JSON string.

        Returns:
            List of potentially fixed JSON strings to try.
        """
        fixes = [json_str]  # Original first

        # Fix trailing commas
        fixed = re.sub(r",(\s*[}\]])", r"\1", json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Fix single quotes (though this might break some strings)
        if "'" in json_str and json_str.count("'") > json_str.count('"'):
            fixed = json_str.replace("'", '"')
            fixes.append(fixed)

        # Fix missing quotes around keys
        fixed = re.sub(r"(\w+):", r'"\1":', json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Try to balance braces if they're unbalanced
        open_braces = json_str.count("{")
        close_braces = json_str.count("}")
        if open_braces > close_braces:
            fixes.append(json_str + "}")
        elif close_braces > open_braces:
            fixes.append("{" + json_str)

        return fixes

    def xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_42(
        self, json_str: str
    ) -> List[str]:
        """
        Attempt to fix common JSON formatting issues.

        Args:
            json_str: Malformed JSON string.

        Returns:
            List of potentially fixed JSON strings to try.
        """
        fixes = [json_str]  # Original first

        # Fix trailing commas
        fixed = re.sub(r",(\s*[}\]])", r"\1", json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Fix single quotes (though this might break some strings)
        if "'" in json_str and json_str.count("'") > json_str.count('"'):
            fixed = json_str.replace("'", '"')
            fixes.append(fixed)

        # Fix missing quotes around keys
        fixed = re.sub(r"(\w+):", r'"\1":', json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Try to balance braces if they're unbalanced
        open_braces = json_str.count("{")
        close_braces = json_str.count("}")
        if open_braces > close_braces:
            fixes.append(json_str + "}")
        elif close_braces > open_braces:
            fixes.append("{" + json_str)

        return fixes

    def xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_43(
        self, json_str: str
    ) -> List[str]:
        """
        Attempt to fix common JSON formatting issues.

        Args:
            json_str: Malformed JSON string.

        Returns:
            List of potentially fixed JSON strings to try.
        """
        fixes = [json_str]  # Original first

        # Fix trailing commas
        fixed = re.sub(r",(\s*[}\]])", r"\1", json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Fix single quotes (though this might break some strings)
        if "'" in json_str and json_str.count("'") > json_str.count('"'):
            fixed = json_str.replace("'", '"')
            fixes.append(fixed)

        # Fix missing quotes around keys
        fixed = re.sub(r"(\w+):", r'XX"\1":XX', json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Try to balance braces if they're unbalanced
        open_braces = json_str.count("{")
        close_braces = json_str.count("}")
        if open_braces > close_braces:
            fixes.append(json_str + "}")
        elif close_braces > open_braces:
            fixes.append("{" + json_str)

        return fixes

    def xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_44(
        self, json_str: str
    ) -> List[str]:
        """
        Attempt to fix common JSON formatting issues.

        Args:
            json_str: Malformed JSON string.

        Returns:
            List of potentially fixed JSON strings to try.
        """
        fixes = [json_str]  # Original first

        # Fix trailing commas
        fixed = re.sub(r",(\s*[}\]])", r"\1", json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Fix single quotes (though this might break some strings)
        if "'" in json_str and json_str.count("'") > json_str.count('"'):
            fixed = json_str.replace("'", '"')
            fixes.append(fixed)

        # Fix missing quotes around keys
        fixed = re.sub(r"(\w+):", r'"\1":', json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Try to balance braces if they're unbalanced
        open_braces = json_str.count("{")
        close_braces = json_str.count("}")
        if open_braces > close_braces:
            fixes.append(json_str + "}")
        elif close_braces > open_braces:
            fixes.append("{" + json_str)

        return fixes

    def xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_45(
        self, json_str: str
    ) -> List[str]:
        """
        Attempt to fix common JSON formatting issues.

        Args:
            json_str: Malformed JSON string.

        Returns:
            List of potentially fixed JSON strings to try.
        """
        fixes = [json_str]  # Original first

        # Fix trailing commas
        fixed = re.sub(r",(\s*[}\]])", r"\1", json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Fix single quotes (though this might break some strings)
        if "'" in json_str and json_str.count("'") > json_str.count('"'):
            fixed = json_str.replace("'", '"')
            fixes.append(fixed)

        # Fix missing quotes around keys
        fixed = re.sub(r"(\w+):", r'"\1":', json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Try to balance braces if they're unbalanced
        open_braces = json_str.count("{")
        close_braces = json_str.count("}")
        if open_braces > close_braces:
            fixes.append(json_str + "}")
        elif close_braces > open_braces:
            fixes.append("{" + json_str)

        return fixes

    def xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_46(
        self, json_str: str
    ) -> List[str]:
        """
        Attempt to fix common JSON formatting issues.

        Args:
            json_str: Malformed JSON string.

        Returns:
            List of potentially fixed JSON strings to try.
        """
        fixes = [json_str]  # Original first

        # Fix trailing commas
        fixed = re.sub(r",(\s*[}\]])", r"\1", json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Fix single quotes (though this might break some strings)
        if "'" in json_str and json_str.count("'") > json_str.count('"'):
            fixed = json_str.replace("'", '"')
            fixes.append(fixed)

        # Fix missing quotes around keys
        fixed = re.sub(r"(\w+):", r'"\1":', json_str)
        if fixed == json_str:
            fixes.append(fixed)

        # Try to balance braces if they're unbalanced
        open_braces = json_str.count("{")
        close_braces = json_str.count("}")
        if open_braces > close_braces:
            fixes.append(json_str + "}")
        elif close_braces > open_braces:
            fixes.append("{" + json_str)

        return fixes

    def xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_47(
        self, json_str: str
    ) -> List[str]:
        """
        Attempt to fix common JSON formatting issues.

        Args:
            json_str: Malformed JSON string.

        Returns:
            List of potentially fixed JSON strings to try.
        """
        fixes = [json_str]  # Original first

        # Fix trailing commas
        fixed = re.sub(r",(\s*[}\]])", r"\1", json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Fix single quotes (though this might break some strings)
        if "'" in json_str and json_str.count("'") > json_str.count('"'):
            fixed = json_str.replace("'", '"')
            fixes.append(fixed)

        # Fix missing quotes around keys
        fixed = re.sub(r"(\w+):", r'"\1":', json_str)
        if fixed != json_str:
            fixes.append(None)

        # Try to balance braces if they're unbalanced
        open_braces = json_str.count("{")
        close_braces = json_str.count("}")
        if open_braces > close_braces:
            fixes.append(json_str + "}")
        elif close_braces > open_braces:
            fixes.append("{" + json_str)

        return fixes

    def xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_48(
        self, json_str: str
    ) -> List[str]:
        """
        Attempt to fix common JSON formatting issues.

        Args:
            json_str: Malformed JSON string.

        Returns:
            List of potentially fixed JSON strings to try.
        """
        fixes = [json_str]  # Original first

        # Fix trailing commas
        fixed = re.sub(r",(\s*[}\]])", r"\1", json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Fix single quotes (though this might break some strings)
        if "'" in json_str and json_str.count("'") > json_str.count('"'):
            fixed = json_str.replace("'", '"')
            fixes.append(fixed)

        # Fix missing quotes around keys
        fixed = re.sub(r"(\w+):", r'"\1":', json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Try to balance braces if they're unbalanced
        open_braces = None
        close_braces = json_str.count("}")
        if open_braces > close_braces:
            fixes.append(json_str + "}")
        elif close_braces > open_braces:
            fixes.append("{" + json_str)

        return fixes

    def xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_49(
        self, json_str: str
    ) -> List[str]:
        """
        Attempt to fix common JSON formatting issues.

        Args:
            json_str: Malformed JSON string.

        Returns:
            List of potentially fixed JSON strings to try.
        """
        fixes = [json_str]  # Original first

        # Fix trailing commas
        fixed = re.sub(r",(\s*[}\]])", r"\1", json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Fix single quotes (though this might break some strings)
        if "'" in json_str and json_str.count("'") > json_str.count('"'):
            fixed = json_str.replace("'", '"')
            fixes.append(fixed)

        # Fix missing quotes around keys
        fixed = re.sub(r"(\w+):", r'"\1":', json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Try to balance braces if they're unbalanced
        open_braces = json_str.count(None)
        close_braces = json_str.count("}")
        if open_braces > close_braces:
            fixes.append(json_str + "}")
        elif close_braces > open_braces:
            fixes.append("{" + json_str)

        return fixes

    def xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_50(
        self, json_str: str
    ) -> List[str]:
        """
        Attempt to fix common JSON formatting issues.

        Args:
            json_str: Malformed JSON string.

        Returns:
            List of potentially fixed JSON strings to try.
        """
        fixes = [json_str]  # Original first

        # Fix trailing commas
        fixed = re.sub(r",(\s*[}\]])", r"\1", json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Fix single quotes (though this might break some strings)
        if "'" in json_str and json_str.count("'") > json_str.count('"'):
            fixed = json_str.replace("'", '"')
            fixes.append(fixed)

        # Fix missing quotes around keys
        fixed = re.sub(r"(\w+):", r'"\1":', json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Try to balance braces if they're unbalanced
        open_braces = json_str.count("XX{XX")
        close_braces = json_str.count("}")
        if open_braces > close_braces:
            fixes.append(json_str + "}")
        elif close_braces > open_braces:
            fixes.append("{" + json_str)

        return fixes

    def xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_51(
        self, json_str: str
    ) -> List[str]:
        """
        Attempt to fix common JSON formatting issues.

        Args:
            json_str: Malformed JSON string.

        Returns:
            List of potentially fixed JSON strings to try.
        """
        fixes = [json_str]  # Original first

        # Fix trailing commas
        fixed = re.sub(r",(\s*[}\]])", r"\1", json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Fix single quotes (though this might break some strings)
        if "'" in json_str and json_str.count("'") > json_str.count('"'):
            fixed = json_str.replace("'", '"')
            fixes.append(fixed)

        # Fix missing quotes around keys
        fixed = re.sub(r"(\w+):", r'"\1":', json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Try to balance braces if they're unbalanced
        open_braces = json_str.count("{")
        close_braces = None
        if open_braces > close_braces:
            fixes.append(json_str + "}")
        elif close_braces > open_braces:
            fixes.append("{" + json_str)

        return fixes

    def xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_52(
        self, json_str: str
    ) -> List[str]:
        """
        Attempt to fix common JSON formatting issues.

        Args:
            json_str: Malformed JSON string.

        Returns:
            List of potentially fixed JSON strings to try.
        """
        fixes = [json_str]  # Original first

        # Fix trailing commas
        fixed = re.sub(r",(\s*[}\]])", r"\1", json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Fix single quotes (though this might break some strings)
        if "'" in json_str and json_str.count("'") > json_str.count('"'):
            fixed = json_str.replace("'", '"')
            fixes.append(fixed)

        # Fix missing quotes around keys
        fixed = re.sub(r"(\w+):", r'"\1":', json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Try to balance braces if they're unbalanced
        open_braces = json_str.count("{")
        close_braces = json_str.count(None)
        if open_braces > close_braces:
            fixes.append(json_str + "}")
        elif close_braces > open_braces:
            fixes.append("{" + json_str)

        return fixes

    def xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_53(
        self, json_str: str
    ) -> List[str]:
        """
        Attempt to fix common JSON formatting issues.

        Args:
            json_str: Malformed JSON string.

        Returns:
            List of potentially fixed JSON strings to try.
        """
        fixes = [json_str]  # Original first

        # Fix trailing commas
        fixed = re.sub(r",(\s*[}\]])", r"\1", json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Fix single quotes (though this might break some strings)
        if "'" in json_str and json_str.count("'") > json_str.count('"'):
            fixed = json_str.replace("'", '"')
            fixes.append(fixed)

        # Fix missing quotes around keys
        fixed = re.sub(r"(\w+):", r'"\1":', json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Try to balance braces if they're unbalanced
        open_braces = json_str.count("{")
        close_braces = json_str.count("XX}XX")
        if open_braces > close_braces:
            fixes.append(json_str + "}")
        elif close_braces > open_braces:
            fixes.append("{" + json_str)

        return fixes

    def xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_54(
        self, json_str: str
    ) -> List[str]:
        """
        Attempt to fix common JSON formatting issues.

        Args:
            json_str: Malformed JSON string.

        Returns:
            List of potentially fixed JSON strings to try.
        """
        fixes = [json_str]  # Original first

        # Fix trailing commas
        fixed = re.sub(r",(\s*[}\]])", r"\1", json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Fix single quotes (though this might break some strings)
        if "'" in json_str and json_str.count("'") > json_str.count('"'):
            fixed = json_str.replace("'", '"')
            fixes.append(fixed)

        # Fix missing quotes around keys
        fixed = re.sub(r"(\w+):", r'"\1":', json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Try to balance braces if they're unbalanced
        open_braces = json_str.count("{")
        close_braces = json_str.count("}")
        if open_braces >= close_braces:
            fixes.append(json_str + "}")
        elif close_braces > open_braces:
            fixes.append("{" + json_str)

        return fixes

    def xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_55(
        self, json_str: str
    ) -> List[str]:
        """
        Attempt to fix common JSON formatting issues.

        Args:
            json_str: Malformed JSON string.

        Returns:
            List of potentially fixed JSON strings to try.
        """
        fixes = [json_str]  # Original first

        # Fix trailing commas
        fixed = re.sub(r",(\s*[}\]])", r"\1", json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Fix single quotes (though this might break some strings)
        if "'" in json_str and json_str.count("'") > json_str.count('"'):
            fixed = json_str.replace("'", '"')
            fixes.append(fixed)

        # Fix missing quotes around keys
        fixed = re.sub(r"(\w+):", r'"\1":', json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Try to balance braces if they're unbalanced
        open_braces = json_str.count("{")
        close_braces = json_str.count("}")
        if open_braces > close_braces:
            fixes.append(None)
        elif close_braces > open_braces:
            fixes.append("{" + json_str)

        return fixes

    def xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_56(
        self, json_str: str
    ) -> List[str]:
        """
        Attempt to fix common JSON formatting issues.

        Args:
            json_str: Malformed JSON string.

        Returns:
            List of potentially fixed JSON strings to try.
        """
        fixes = [json_str]  # Original first

        # Fix trailing commas
        fixed = re.sub(r",(\s*[}\]])", r"\1", json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Fix single quotes (though this might break some strings)
        if "'" in json_str and json_str.count("'") > json_str.count('"'):
            fixed = json_str.replace("'", '"')
            fixes.append(fixed)

        # Fix missing quotes around keys
        fixed = re.sub(r"(\w+):", r'"\1":', json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Try to balance braces if they're unbalanced
        open_braces = json_str.count("{")
        close_braces = json_str.count("}")
        if open_braces > close_braces:
            fixes.append(json_str - "}")
        elif close_braces > open_braces:
            fixes.append("{" + json_str)

        return fixes

    def xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_57(
        self, json_str: str
    ) -> List[str]:
        """
        Attempt to fix common JSON formatting issues.

        Args:
            json_str: Malformed JSON string.

        Returns:
            List of potentially fixed JSON strings to try.
        """
        fixes = [json_str]  # Original first

        # Fix trailing commas
        fixed = re.sub(r",(\s*[}\]])", r"\1", json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Fix single quotes (though this might break some strings)
        if "'" in json_str and json_str.count("'") > json_str.count('"'):
            fixed = json_str.replace("'", '"')
            fixes.append(fixed)

        # Fix missing quotes around keys
        fixed = re.sub(r"(\w+):", r'"\1":', json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Try to balance braces if they're unbalanced
        open_braces = json_str.count("{")
        close_braces = json_str.count("}")
        if open_braces > close_braces:
            fixes.append(json_str + "XX}XX")
        elif close_braces > open_braces:
            fixes.append("{" + json_str)

        return fixes

    def xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_58(
        self, json_str: str
    ) -> List[str]:
        """
        Attempt to fix common JSON formatting issues.

        Args:
            json_str: Malformed JSON string.

        Returns:
            List of potentially fixed JSON strings to try.
        """
        fixes = [json_str]  # Original first

        # Fix trailing commas
        fixed = re.sub(r",(\s*[}\]])", r"\1", json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Fix single quotes (though this might break some strings)
        if "'" in json_str and json_str.count("'") > json_str.count('"'):
            fixed = json_str.replace("'", '"')
            fixes.append(fixed)

        # Fix missing quotes around keys
        fixed = re.sub(r"(\w+):", r'"\1":', json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Try to balance braces if they're unbalanced
        open_braces = json_str.count("{")
        close_braces = json_str.count("}")
        if open_braces > close_braces:
            fixes.append(json_str + "}")
        elif close_braces >= open_braces:
            fixes.append("{" + json_str)

        return fixes

    def xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_59(
        self, json_str: str
    ) -> List[str]:
        """
        Attempt to fix common JSON formatting issues.

        Args:
            json_str: Malformed JSON string.

        Returns:
            List of potentially fixed JSON strings to try.
        """
        fixes = [json_str]  # Original first

        # Fix trailing commas
        fixed = re.sub(r",(\s*[}\]])", r"\1", json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Fix single quotes (though this might break some strings)
        if "'" in json_str and json_str.count("'") > json_str.count('"'):
            fixed = json_str.replace("'", '"')
            fixes.append(fixed)

        # Fix missing quotes around keys
        fixed = re.sub(r"(\w+):", r'"\1":', json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Try to balance braces if they're unbalanced
        open_braces = json_str.count("{")
        close_braces = json_str.count("}")
        if open_braces > close_braces:
            fixes.append(json_str + "}")
        elif close_braces > open_braces:
            fixes.append(None)

        return fixes

    def xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_60(
        self, json_str: str
    ) -> List[str]:
        """
        Attempt to fix common JSON formatting issues.

        Args:
            json_str: Malformed JSON string.

        Returns:
            List of potentially fixed JSON strings to try.
        """
        fixes = [json_str]  # Original first

        # Fix trailing commas
        fixed = re.sub(r",(\s*[}\]])", r"\1", json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Fix single quotes (though this might break some strings)
        if "'" in json_str and json_str.count("'") > json_str.count('"'):
            fixed = json_str.replace("'", '"')
            fixes.append(fixed)

        # Fix missing quotes around keys
        fixed = re.sub(r"(\w+):", r'"\1":', json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Try to balance braces if they're unbalanced
        open_braces = json_str.count("{")
        close_braces = json_str.count("}")
        if open_braces > close_braces:
            fixes.append(json_str + "}")
        elif close_braces > open_braces:
            fixes.append("{" - json_str)

        return fixes

    def xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_61(
        self, json_str: str
    ) -> List[str]:
        """
        Attempt to fix common JSON formatting issues.

        Args:
            json_str: Malformed JSON string.

        Returns:
            List of potentially fixed JSON strings to try.
        """
        fixes = [json_str]  # Original first

        # Fix trailing commas
        fixed = re.sub(r",(\s*[}\]])", r"\1", json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Fix single quotes (though this might break some strings)
        if "'" in json_str and json_str.count("'") > json_str.count('"'):
            fixed = json_str.replace("'", '"')
            fixes.append(fixed)

        # Fix missing quotes around keys
        fixed = re.sub(r"(\w+):", r'"\1":', json_str)
        if fixed != json_str:
            fixes.append(fixed)

        # Try to balance braces if they're unbalanced
        open_braces = json_str.count("{")
        close_braces = json_str.count("}")
        if open_braces > close_braces:
            fixes.append(json_str + "}")
        elif close_braces > open_braces:
            fixes.append("XX{XX" + json_str)

        return fixes

    xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_mutants: ClassVar[
        MutantDict
    ] = {
        "xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_1": xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_1,
        "xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_2": xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_2,
        "xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_3": xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_3,
        "xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_4": xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_4,
        "xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_5": xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_5,
        "xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_6": xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_6,
        "xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_7": xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_7,
        "xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_8": xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_8,
        "xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_9": xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_9,
        "xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_10": xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_10,
        "xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_11": xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_11,
        "xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_12": xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_12,
        "xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_13": xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_13,
        "xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_14": xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_14,
        "xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_15": xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_15,
        "xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_16": xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_16,
        "xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_17": xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_17,
        "xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_18": xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_18,
        "xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_19": xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_19,
        "xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_20": xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_20,
        "xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_21": xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_21,
        "xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_22": xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_22,
        "xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_23": xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_23,
        "xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_24": xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_24,
        "xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_25": xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_25,
        "xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_26": xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_26,
        "xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_27": xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_27,
        "xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_28": xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_28,
        "xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_29": xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_29,
        "xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_30": xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_30,
        "xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_31": xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_31,
        "xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_32": xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_32,
        "xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_33": xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_33,
        "xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_34": xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_34,
        "xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_35": xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_35,
        "xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_36": xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_36,
        "xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_37": xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_37,
        "xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_38": xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_38,
        "xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_39": xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_39,
        "xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_40": xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_40,
        "xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_41": xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_41,
        "xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_42": xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_42,
        "xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_43": xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_43,
        "xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_44": xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_44,
        "xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_45": xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_45,
        "xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_46": xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_46,
        "xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_47": xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_47,
        "xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_48": xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_48,
        "xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_49": xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_49,
        "xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_50": xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_50,
        "xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_51": xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_51,
        "xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_52": xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_52,
        "xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_53": xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_53,
        "xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_54": xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_54,
        "xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_55": xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_55,
        "xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_56": xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_56,
        "xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_57": xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_57,
        "xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_58": xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_58,
        "xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_59": xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_59,
        "xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_60": xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_60,
        "xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_61": xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_61,
    }

    def try_fix_common_json_issues(self, *args, **kwargs):
        result = _mutmut_trampoline(
            object.__getattribute__(
                self, "xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_orig"
            ),
            object.__getattribute__(
                self, "xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_mutants"
            ),
            args,
            kwargs,
            self,
        )
        return result

    try_fix_common_json_issues.__signature__ = _mutmut_signature(
        xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_orig
    )
    xǁRobustJSONParserǁtry_fix_common_json_issues__mutmut_orig.__name__ = (
        "xǁRobustJSONParserǁtry_fix_common_json_issues"
    )

    def xǁRobustJSONParserǁextract_and_parse_json__mutmut_orig(
        self, text: str, max_candidates: int = 5
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Extract and parse JSON from LLM response with multiple fallback strategies.

        Args:
            text: Text containing JSON response from LLM.
            max_candidates: Maximum number of JSON candidates to try.

        Returns:
            Tuple of (parsed_json, error_message). Returns None, error_msg if all parsing fails.
        """
        if not text or not text.strip():
            logger.debug("JSON parsing failed: Empty response text")
            return None, "Empty response text"

        # Clean the response
        cleaned_text = self.clean_llm_response(text)
        if not cleaned_text:
            logger.debug("JSON parsing failed: Response became empty after cleaning")
            return None, "Response became empty after cleaning"

        # Try parsing the cleaned text directly first
        parsed, error = self.parse_json_safe(cleaned_text)
        if parsed is not None:
            logger.debug("JSON parsing succeeded with direct parsing")
            return parsed, None

        # Extract JSON candidates from the cleaned text
        candidates = self.extract_json_from_text(cleaned_text)

        # Limit candidates to avoid excessive processing
        candidates = candidates[:max_candidates]
        logger.debug(f"Extracted {len(candidates)} JSON candidates from response")

        # Try each candidate
        for i, candidate in enumerate(candidates):
            logger.debug(f"Trying candidate {i + 1}: {candidate[:100]}...")
            # Try the candidate as-is
            parsed, error = self.parse_json_safe(candidate)
            if parsed is not None:
                logger.debug(f"JSON parsing succeeded with candidate {i + 1}")
                return parsed, None

            # Try to fix common issues
            fixed_candidates = self.try_fix_common_json_issues(candidate)
            for j, fixed in enumerate(fixed_candidates):
                if fixed != candidate:  # Only try if different
                    logger.debug(
                        f"Trying fixed candidate {i + 1}.{j + 1}: {fixed[:100]}..."
                    )
                    parsed, error = self.parse_json_safe(fixed)
                    if parsed is not None:
                        logger.debug(
                            f"JSON parsing succeeded with fixed candidate {i + 1}.{j + 1}"
                        )
                        return parsed, None

        # If all parsing failed, return the best error message
        error_msg = f"Failed to extract valid JSON from response. Tried {len(candidates)} candidates."
        logger.warning(
            f"JSON parsing failed: {error_msg}. Original text: {text[:200]}..."
        )
        return None, error_msg

    def xǁRobustJSONParserǁextract_and_parse_json__mutmut_1(
        self, text: str, max_candidates: int = 6
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Extract and parse JSON from LLM response with multiple fallback strategies.

        Args:
            text: Text containing JSON response from LLM.
            max_candidates: Maximum number of JSON candidates to try.

        Returns:
            Tuple of (parsed_json, error_message). Returns None, error_msg if all parsing fails.
        """
        if not text or not text.strip():
            logger.debug("JSON parsing failed: Empty response text")
            return None, "Empty response text"

        # Clean the response
        cleaned_text = self.clean_llm_response(text)
        if not cleaned_text:
            logger.debug("JSON parsing failed: Response became empty after cleaning")
            return None, "Response became empty after cleaning"

        # Try parsing the cleaned text directly first
        parsed, error = self.parse_json_safe(cleaned_text)
        if parsed is not None:
            logger.debug("JSON parsing succeeded with direct parsing")
            return parsed, None

        # Extract JSON candidates from the cleaned text
        candidates = self.extract_json_from_text(cleaned_text)

        # Limit candidates to avoid excessive processing
        candidates = candidates[:max_candidates]
        logger.debug(f"Extracted {len(candidates)} JSON candidates from response")

        # Try each candidate
        for i, candidate in enumerate(candidates):
            logger.debug(f"Trying candidate {i + 1}: {candidate[:100]}...")
            # Try the candidate as-is
            parsed, error = self.parse_json_safe(candidate)
            if parsed is not None:
                logger.debug(f"JSON parsing succeeded with candidate {i + 1}")
                return parsed, None

            # Try to fix common issues
            fixed_candidates = self.try_fix_common_json_issues(candidate)
            for j, fixed in enumerate(fixed_candidates):
                if fixed != candidate:  # Only try if different
                    logger.debug(
                        f"Trying fixed candidate {i + 1}.{j + 1}: {fixed[:100]}..."
                    )
                    parsed, error = self.parse_json_safe(fixed)
                    if parsed is not None:
                        logger.debug(
                            f"JSON parsing succeeded with fixed candidate {i + 1}.{j + 1}"
                        )
                        return parsed, None

        # If all parsing failed, return the best error message
        error_msg = f"Failed to extract valid JSON from response. Tried {len(candidates)} candidates."
        logger.warning(
            f"JSON parsing failed: {error_msg}. Original text: {text[:200]}..."
        )
        return None, error_msg

    def xǁRobustJSONParserǁextract_and_parse_json__mutmut_2(
        self, text: str, max_candidates: int = 5
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Extract and parse JSON from LLM response with multiple fallback strategies.

        Args:
            text: Text containing JSON response from LLM.
            max_candidates: Maximum number of JSON candidates to try.

        Returns:
            Tuple of (parsed_json, error_message). Returns None, error_msg if all parsing fails.
        """
        if not text and not text.strip():
            logger.debug("JSON parsing failed: Empty response text")
            return None, "Empty response text"

        # Clean the response
        cleaned_text = self.clean_llm_response(text)
        if not cleaned_text:
            logger.debug("JSON parsing failed: Response became empty after cleaning")
            return None, "Response became empty after cleaning"

        # Try parsing the cleaned text directly first
        parsed, error = self.parse_json_safe(cleaned_text)
        if parsed is not None:
            logger.debug("JSON parsing succeeded with direct parsing")
            return parsed, None

        # Extract JSON candidates from the cleaned text
        candidates = self.extract_json_from_text(cleaned_text)

        # Limit candidates to avoid excessive processing
        candidates = candidates[:max_candidates]
        logger.debug(f"Extracted {len(candidates)} JSON candidates from response")

        # Try each candidate
        for i, candidate in enumerate(candidates):
            logger.debug(f"Trying candidate {i + 1}: {candidate[:100]}...")
            # Try the candidate as-is
            parsed, error = self.parse_json_safe(candidate)
            if parsed is not None:
                logger.debug(f"JSON parsing succeeded with candidate {i + 1}")
                return parsed, None

            # Try to fix common issues
            fixed_candidates = self.try_fix_common_json_issues(candidate)
            for j, fixed in enumerate(fixed_candidates):
                if fixed != candidate:  # Only try if different
                    logger.debug(
                        f"Trying fixed candidate {i + 1}.{j + 1}: {fixed[:100]}..."
                    )
                    parsed, error = self.parse_json_safe(fixed)
                    if parsed is not None:
                        logger.debug(
                            f"JSON parsing succeeded with fixed candidate {i + 1}.{j + 1}"
                        )
                        return parsed, None

        # If all parsing failed, return the best error message
        error_msg = f"Failed to extract valid JSON from response. Tried {len(candidates)} candidates."
        logger.warning(
            f"JSON parsing failed: {error_msg}. Original text: {text[:200]}..."
        )
        return None, error_msg

    def xǁRobustJSONParserǁextract_and_parse_json__mutmut_3(
        self, text: str, max_candidates: int = 5
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Extract and parse JSON from LLM response with multiple fallback strategies.

        Args:
            text: Text containing JSON response from LLM.
            max_candidates: Maximum number of JSON candidates to try.

        Returns:
            Tuple of (parsed_json, error_message). Returns None, error_msg if all parsing fails.
        """
        if text or not text.strip():
            logger.debug("JSON parsing failed: Empty response text")
            return None, "Empty response text"

        # Clean the response
        cleaned_text = self.clean_llm_response(text)
        if not cleaned_text:
            logger.debug("JSON parsing failed: Response became empty after cleaning")
            return None, "Response became empty after cleaning"

        # Try parsing the cleaned text directly first
        parsed, error = self.parse_json_safe(cleaned_text)
        if parsed is not None:
            logger.debug("JSON parsing succeeded with direct parsing")
            return parsed, None

        # Extract JSON candidates from the cleaned text
        candidates = self.extract_json_from_text(cleaned_text)

        # Limit candidates to avoid excessive processing
        candidates = candidates[:max_candidates]
        logger.debug(f"Extracted {len(candidates)} JSON candidates from response")

        # Try each candidate
        for i, candidate in enumerate(candidates):
            logger.debug(f"Trying candidate {i + 1}: {candidate[:100]}...")
            # Try the candidate as-is
            parsed, error = self.parse_json_safe(candidate)
            if parsed is not None:
                logger.debug(f"JSON parsing succeeded with candidate {i + 1}")
                return parsed, None

            # Try to fix common issues
            fixed_candidates = self.try_fix_common_json_issues(candidate)
            for j, fixed in enumerate(fixed_candidates):
                if fixed != candidate:  # Only try if different
                    logger.debug(
                        f"Trying fixed candidate {i + 1}.{j + 1}: {fixed[:100]}..."
                    )
                    parsed, error = self.parse_json_safe(fixed)
                    if parsed is not None:
                        logger.debug(
                            f"JSON parsing succeeded with fixed candidate {i + 1}.{j + 1}"
                        )
                        return parsed, None

        # If all parsing failed, return the best error message
        error_msg = f"Failed to extract valid JSON from response. Tried {len(candidates)} candidates."
        logger.warning(
            f"JSON parsing failed: {error_msg}. Original text: {text[:200]}..."
        )
        return None, error_msg

    def xǁRobustJSONParserǁextract_and_parse_json__mutmut_4(
        self, text: str, max_candidates: int = 5
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Extract and parse JSON from LLM response with multiple fallback strategies.

        Args:
            text: Text containing JSON response from LLM.
            max_candidates: Maximum number of JSON candidates to try.

        Returns:
            Tuple of (parsed_json, error_message). Returns None, error_msg if all parsing fails.
        """
        if not text or text.strip():
            logger.debug("JSON parsing failed: Empty response text")
            return None, "Empty response text"

        # Clean the response
        cleaned_text = self.clean_llm_response(text)
        if not cleaned_text:
            logger.debug("JSON parsing failed: Response became empty after cleaning")
            return None, "Response became empty after cleaning"

        # Try parsing the cleaned text directly first
        parsed, error = self.parse_json_safe(cleaned_text)
        if parsed is not None:
            logger.debug("JSON parsing succeeded with direct parsing")
            return parsed, None

        # Extract JSON candidates from the cleaned text
        candidates = self.extract_json_from_text(cleaned_text)

        # Limit candidates to avoid excessive processing
        candidates = candidates[:max_candidates]
        logger.debug(f"Extracted {len(candidates)} JSON candidates from response")

        # Try each candidate
        for i, candidate in enumerate(candidates):
            logger.debug(f"Trying candidate {i + 1}: {candidate[:100]}...")
            # Try the candidate as-is
            parsed, error = self.parse_json_safe(candidate)
            if parsed is not None:
                logger.debug(f"JSON parsing succeeded with candidate {i + 1}")
                return parsed, None

            # Try to fix common issues
            fixed_candidates = self.try_fix_common_json_issues(candidate)
            for j, fixed in enumerate(fixed_candidates):
                if fixed != candidate:  # Only try if different
                    logger.debug(
                        f"Trying fixed candidate {i + 1}.{j + 1}: {fixed[:100]}..."
                    )
                    parsed, error = self.parse_json_safe(fixed)
                    if parsed is not None:
                        logger.debug(
                            f"JSON parsing succeeded with fixed candidate {i + 1}.{j + 1}"
                        )
                        return parsed, None

        # If all parsing failed, return the best error message
        error_msg = f"Failed to extract valid JSON from response. Tried {len(candidates)} candidates."
        logger.warning(
            f"JSON parsing failed: {error_msg}. Original text: {text[:200]}..."
        )
        return None, error_msg

    def xǁRobustJSONParserǁextract_and_parse_json__mutmut_5(
        self, text: str, max_candidates: int = 5
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Extract and parse JSON from LLM response with multiple fallback strategies.

        Args:
            text: Text containing JSON response from LLM.
            max_candidates: Maximum number of JSON candidates to try.

        Returns:
            Tuple of (parsed_json, error_message). Returns None, error_msg if all parsing fails.
        """
        if not text or not text.strip():
            logger.debug(None)
            return None, "Empty response text"

        # Clean the response
        cleaned_text = self.clean_llm_response(text)
        if not cleaned_text:
            logger.debug("JSON parsing failed: Response became empty after cleaning")
            return None, "Response became empty after cleaning"

        # Try parsing the cleaned text directly first
        parsed, error = self.parse_json_safe(cleaned_text)
        if parsed is not None:
            logger.debug("JSON parsing succeeded with direct parsing")
            return parsed, None

        # Extract JSON candidates from the cleaned text
        candidates = self.extract_json_from_text(cleaned_text)

        # Limit candidates to avoid excessive processing
        candidates = candidates[:max_candidates]
        logger.debug(f"Extracted {len(candidates)} JSON candidates from response")

        # Try each candidate
        for i, candidate in enumerate(candidates):
            logger.debug(f"Trying candidate {i + 1}: {candidate[:100]}...")
            # Try the candidate as-is
            parsed, error = self.parse_json_safe(candidate)
            if parsed is not None:
                logger.debug(f"JSON parsing succeeded with candidate {i + 1}")
                return parsed, None

            # Try to fix common issues
            fixed_candidates = self.try_fix_common_json_issues(candidate)
            for j, fixed in enumerate(fixed_candidates):
                if fixed != candidate:  # Only try if different
                    logger.debug(
                        f"Trying fixed candidate {i + 1}.{j + 1}: {fixed[:100]}..."
                    )
                    parsed, error = self.parse_json_safe(fixed)
                    if parsed is not None:
                        logger.debug(
                            f"JSON parsing succeeded with fixed candidate {i + 1}.{j + 1}"
                        )
                        return parsed, None

        # If all parsing failed, return the best error message
        error_msg = f"Failed to extract valid JSON from response. Tried {len(candidates)} candidates."
        logger.warning(
            f"JSON parsing failed: {error_msg}. Original text: {text[:200]}..."
        )
        return None, error_msg

    def xǁRobustJSONParserǁextract_and_parse_json__mutmut_6(
        self, text: str, max_candidates: int = 5
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Extract and parse JSON from LLM response with multiple fallback strategies.

        Args:
            text: Text containing JSON response from LLM.
            max_candidates: Maximum number of JSON candidates to try.

        Returns:
            Tuple of (parsed_json, error_message). Returns None, error_msg if all parsing fails.
        """
        if not text or not text.strip():
            logger.debug("XXJSON parsing failed: Empty response textXX")
            return None, "Empty response text"

        # Clean the response
        cleaned_text = self.clean_llm_response(text)
        if not cleaned_text:
            logger.debug("JSON parsing failed: Response became empty after cleaning")
            return None, "Response became empty after cleaning"

        # Try parsing the cleaned text directly first
        parsed, error = self.parse_json_safe(cleaned_text)
        if parsed is not None:
            logger.debug("JSON parsing succeeded with direct parsing")
            return parsed, None

        # Extract JSON candidates from the cleaned text
        candidates = self.extract_json_from_text(cleaned_text)

        # Limit candidates to avoid excessive processing
        candidates = candidates[:max_candidates]
        logger.debug(f"Extracted {len(candidates)} JSON candidates from response")

        # Try each candidate
        for i, candidate in enumerate(candidates):
            logger.debug(f"Trying candidate {i + 1}: {candidate[:100]}...")
            # Try the candidate as-is
            parsed, error = self.parse_json_safe(candidate)
            if parsed is not None:
                logger.debug(f"JSON parsing succeeded with candidate {i + 1}")
                return parsed, None

            # Try to fix common issues
            fixed_candidates = self.try_fix_common_json_issues(candidate)
            for j, fixed in enumerate(fixed_candidates):
                if fixed != candidate:  # Only try if different
                    logger.debug(
                        f"Trying fixed candidate {i + 1}.{j + 1}: {fixed[:100]}..."
                    )
                    parsed, error = self.parse_json_safe(fixed)
                    if parsed is not None:
                        logger.debug(
                            f"JSON parsing succeeded with fixed candidate {i + 1}.{j + 1}"
                        )
                        return parsed, None

        # If all parsing failed, return the best error message
        error_msg = f"Failed to extract valid JSON from response. Tried {len(candidates)} candidates."
        logger.warning(
            f"JSON parsing failed: {error_msg}. Original text: {text[:200]}..."
        )
        return None, error_msg

    def xǁRobustJSONParserǁextract_and_parse_json__mutmut_7(
        self, text: str, max_candidates: int = 5
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Extract and parse JSON from LLM response with multiple fallback strategies.

        Args:
            text: Text containing JSON response from LLM.
            max_candidates: Maximum number of JSON candidates to try.

        Returns:
            Tuple of (parsed_json, error_message). Returns None, error_msg if all parsing fails.
        """
        if not text or not text.strip():
            logger.debug("json parsing failed: empty response text")
            return None, "Empty response text"

        # Clean the response
        cleaned_text = self.clean_llm_response(text)
        if not cleaned_text:
            logger.debug("JSON parsing failed: Response became empty after cleaning")
            return None, "Response became empty after cleaning"

        # Try parsing the cleaned text directly first
        parsed, error = self.parse_json_safe(cleaned_text)
        if parsed is not None:
            logger.debug("JSON parsing succeeded with direct parsing")
            return parsed, None

        # Extract JSON candidates from the cleaned text
        candidates = self.extract_json_from_text(cleaned_text)

        # Limit candidates to avoid excessive processing
        candidates = candidates[:max_candidates]
        logger.debug(f"Extracted {len(candidates)} JSON candidates from response")

        # Try each candidate
        for i, candidate in enumerate(candidates):
            logger.debug(f"Trying candidate {i + 1}: {candidate[:100]}...")
            # Try the candidate as-is
            parsed, error = self.parse_json_safe(candidate)
            if parsed is not None:
                logger.debug(f"JSON parsing succeeded with candidate {i + 1}")
                return parsed, None

            # Try to fix common issues
            fixed_candidates = self.try_fix_common_json_issues(candidate)
            for j, fixed in enumerate(fixed_candidates):
                if fixed != candidate:  # Only try if different
                    logger.debug(
                        f"Trying fixed candidate {i + 1}.{j + 1}: {fixed[:100]}..."
                    )
                    parsed, error = self.parse_json_safe(fixed)
                    if parsed is not None:
                        logger.debug(
                            f"JSON parsing succeeded with fixed candidate {i + 1}.{j + 1}"
                        )
                        return parsed, None

        # If all parsing failed, return the best error message
        error_msg = f"Failed to extract valid JSON from response. Tried {len(candidates)} candidates."
        logger.warning(
            f"JSON parsing failed: {error_msg}. Original text: {text[:200]}..."
        )
        return None, error_msg

    def xǁRobustJSONParserǁextract_and_parse_json__mutmut_8(
        self, text: str, max_candidates: int = 5
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Extract and parse JSON from LLM response with multiple fallback strategies.

        Args:
            text: Text containing JSON response from LLM.
            max_candidates: Maximum number of JSON candidates to try.

        Returns:
            Tuple of (parsed_json, error_message). Returns None, error_msg if all parsing fails.
        """
        if not text or not text.strip():
            logger.debug("JSON PARSING FAILED: EMPTY RESPONSE TEXT")
            return None, "Empty response text"

        # Clean the response
        cleaned_text = self.clean_llm_response(text)
        if not cleaned_text:
            logger.debug("JSON parsing failed: Response became empty after cleaning")
            return None, "Response became empty after cleaning"

        # Try parsing the cleaned text directly first
        parsed, error = self.parse_json_safe(cleaned_text)
        if parsed is not None:
            logger.debug("JSON parsing succeeded with direct parsing")
            return parsed, None

        # Extract JSON candidates from the cleaned text
        candidates = self.extract_json_from_text(cleaned_text)

        # Limit candidates to avoid excessive processing
        candidates = candidates[:max_candidates]
        logger.debug(f"Extracted {len(candidates)} JSON candidates from response")

        # Try each candidate
        for i, candidate in enumerate(candidates):
            logger.debug(f"Trying candidate {i + 1}: {candidate[:100]}...")
            # Try the candidate as-is
            parsed, error = self.parse_json_safe(candidate)
            if parsed is not None:
                logger.debug(f"JSON parsing succeeded with candidate {i + 1}")
                return parsed, None

            # Try to fix common issues
            fixed_candidates = self.try_fix_common_json_issues(candidate)
            for j, fixed in enumerate(fixed_candidates):
                if fixed != candidate:  # Only try if different
                    logger.debug(
                        f"Trying fixed candidate {i + 1}.{j + 1}: {fixed[:100]}..."
                    )
                    parsed, error = self.parse_json_safe(fixed)
                    if parsed is not None:
                        logger.debug(
                            f"JSON parsing succeeded with fixed candidate {i + 1}.{j + 1}"
                        )
                        return parsed, None

        # If all parsing failed, return the best error message
        error_msg = f"Failed to extract valid JSON from response. Tried {len(candidates)} candidates."
        logger.warning(
            f"JSON parsing failed: {error_msg}. Original text: {text[:200]}..."
        )
        return None, error_msg

    def xǁRobustJSONParserǁextract_and_parse_json__mutmut_9(
        self, text: str, max_candidates: int = 5
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Extract and parse JSON from LLM response with multiple fallback strategies.

        Args:
            text: Text containing JSON response from LLM.
            max_candidates: Maximum number of JSON candidates to try.

        Returns:
            Tuple of (parsed_json, error_message). Returns None, error_msg if all parsing fails.
        """
        if not text or not text.strip():
            logger.debug("JSON parsing failed: Empty response text")
            return None, "XXEmpty response textXX"

        # Clean the response
        cleaned_text = self.clean_llm_response(text)
        if not cleaned_text:
            logger.debug("JSON parsing failed: Response became empty after cleaning")
            return None, "Response became empty after cleaning"

        # Try parsing the cleaned text directly first
        parsed, error = self.parse_json_safe(cleaned_text)
        if parsed is not None:
            logger.debug("JSON parsing succeeded with direct parsing")
            return parsed, None

        # Extract JSON candidates from the cleaned text
        candidates = self.extract_json_from_text(cleaned_text)

        # Limit candidates to avoid excessive processing
        candidates = candidates[:max_candidates]
        logger.debug(f"Extracted {len(candidates)} JSON candidates from response")

        # Try each candidate
        for i, candidate in enumerate(candidates):
            logger.debug(f"Trying candidate {i + 1}: {candidate[:100]}...")
            # Try the candidate as-is
            parsed, error = self.parse_json_safe(candidate)
            if parsed is not None:
                logger.debug(f"JSON parsing succeeded with candidate {i + 1}")
                return parsed, None

            # Try to fix common issues
            fixed_candidates = self.try_fix_common_json_issues(candidate)
            for j, fixed in enumerate(fixed_candidates):
                if fixed != candidate:  # Only try if different
                    logger.debug(
                        f"Trying fixed candidate {i + 1}.{j + 1}: {fixed[:100]}..."
                    )
                    parsed, error = self.parse_json_safe(fixed)
                    if parsed is not None:
                        logger.debug(
                            f"JSON parsing succeeded with fixed candidate {i + 1}.{j + 1}"
                        )
                        return parsed, None

        # If all parsing failed, return the best error message
        error_msg = f"Failed to extract valid JSON from response. Tried {len(candidates)} candidates."
        logger.warning(
            f"JSON parsing failed: {error_msg}. Original text: {text[:200]}..."
        )
        return None, error_msg

    def xǁRobustJSONParserǁextract_and_parse_json__mutmut_10(
        self, text: str, max_candidates: int = 5
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Extract and parse JSON from LLM response with multiple fallback strategies.

        Args:
            text: Text containing JSON response from LLM.
            max_candidates: Maximum number of JSON candidates to try.

        Returns:
            Tuple of (parsed_json, error_message). Returns None, error_msg if all parsing fails.
        """
        if not text or not text.strip():
            logger.debug("JSON parsing failed: Empty response text")
            return None, "empty response text"

        # Clean the response
        cleaned_text = self.clean_llm_response(text)
        if not cleaned_text:
            logger.debug("JSON parsing failed: Response became empty after cleaning")
            return None, "Response became empty after cleaning"

        # Try parsing the cleaned text directly first
        parsed, error = self.parse_json_safe(cleaned_text)
        if parsed is not None:
            logger.debug("JSON parsing succeeded with direct parsing")
            return parsed, None

        # Extract JSON candidates from the cleaned text
        candidates = self.extract_json_from_text(cleaned_text)

        # Limit candidates to avoid excessive processing
        candidates = candidates[:max_candidates]
        logger.debug(f"Extracted {len(candidates)} JSON candidates from response")

        # Try each candidate
        for i, candidate in enumerate(candidates):
            logger.debug(f"Trying candidate {i + 1}: {candidate[:100]}...")
            # Try the candidate as-is
            parsed, error = self.parse_json_safe(candidate)
            if parsed is not None:
                logger.debug(f"JSON parsing succeeded with candidate {i + 1}")
                return parsed, None

            # Try to fix common issues
            fixed_candidates = self.try_fix_common_json_issues(candidate)
            for j, fixed in enumerate(fixed_candidates):
                if fixed != candidate:  # Only try if different
                    logger.debug(
                        f"Trying fixed candidate {i + 1}.{j + 1}: {fixed[:100]}..."
                    )
                    parsed, error = self.parse_json_safe(fixed)
                    if parsed is not None:
                        logger.debug(
                            f"JSON parsing succeeded with fixed candidate {i + 1}.{j + 1}"
                        )
                        return parsed, None

        # If all parsing failed, return the best error message
        error_msg = f"Failed to extract valid JSON from response. Tried {len(candidates)} candidates."
        logger.warning(
            f"JSON parsing failed: {error_msg}. Original text: {text[:200]}..."
        )
        return None, error_msg

    def xǁRobustJSONParserǁextract_and_parse_json__mutmut_11(
        self, text: str, max_candidates: int = 5
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Extract and parse JSON from LLM response with multiple fallback strategies.

        Args:
            text: Text containing JSON response from LLM.
            max_candidates: Maximum number of JSON candidates to try.

        Returns:
            Tuple of (parsed_json, error_message). Returns None, error_msg if all parsing fails.
        """
        if not text or not text.strip():
            logger.debug("JSON parsing failed: Empty response text")
            return None, "EMPTY RESPONSE TEXT"

        # Clean the response
        cleaned_text = self.clean_llm_response(text)
        if not cleaned_text:
            logger.debug("JSON parsing failed: Response became empty after cleaning")
            return None, "Response became empty after cleaning"

        # Try parsing the cleaned text directly first
        parsed, error = self.parse_json_safe(cleaned_text)
        if parsed is not None:
            logger.debug("JSON parsing succeeded with direct parsing")
            return parsed, None

        # Extract JSON candidates from the cleaned text
        candidates = self.extract_json_from_text(cleaned_text)

        # Limit candidates to avoid excessive processing
        candidates = candidates[:max_candidates]
        logger.debug(f"Extracted {len(candidates)} JSON candidates from response")

        # Try each candidate
        for i, candidate in enumerate(candidates):
            logger.debug(f"Trying candidate {i + 1}: {candidate[:100]}...")
            # Try the candidate as-is
            parsed, error = self.parse_json_safe(candidate)
            if parsed is not None:
                logger.debug(f"JSON parsing succeeded with candidate {i + 1}")
                return parsed, None

            # Try to fix common issues
            fixed_candidates = self.try_fix_common_json_issues(candidate)
            for j, fixed in enumerate(fixed_candidates):
                if fixed != candidate:  # Only try if different
                    logger.debug(
                        f"Trying fixed candidate {i + 1}.{j + 1}: {fixed[:100]}..."
                    )
                    parsed, error = self.parse_json_safe(fixed)
                    if parsed is not None:
                        logger.debug(
                            f"JSON parsing succeeded with fixed candidate {i + 1}.{j + 1}"
                        )
                        return parsed, None

        # If all parsing failed, return the best error message
        error_msg = f"Failed to extract valid JSON from response. Tried {len(candidates)} candidates."
        logger.warning(
            f"JSON parsing failed: {error_msg}. Original text: {text[:200]}..."
        )
        return None, error_msg

    def xǁRobustJSONParserǁextract_and_parse_json__mutmut_12(
        self, text: str, max_candidates: int = 5
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Extract and parse JSON from LLM response with multiple fallback strategies.

        Args:
            text: Text containing JSON response from LLM.
            max_candidates: Maximum number of JSON candidates to try.

        Returns:
            Tuple of (parsed_json, error_message). Returns None, error_msg if all parsing fails.
        """
        if not text or not text.strip():
            logger.debug("JSON parsing failed: Empty response text")
            return None, "Empty response text"

        # Clean the response
        cleaned_text = None
        if not cleaned_text:
            logger.debug("JSON parsing failed: Response became empty after cleaning")
            return None, "Response became empty after cleaning"

        # Try parsing the cleaned text directly first
        parsed, error = self.parse_json_safe(cleaned_text)
        if parsed is not None:
            logger.debug("JSON parsing succeeded with direct parsing")
            return parsed, None

        # Extract JSON candidates from the cleaned text
        candidates = self.extract_json_from_text(cleaned_text)

        # Limit candidates to avoid excessive processing
        candidates = candidates[:max_candidates]
        logger.debug(f"Extracted {len(candidates)} JSON candidates from response")

        # Try each candidate
        for i, candidate in enumerate(candidates):
            logger.debug(f"Trying candidate {i + 1}: {candidate[:100]}...")
            # Try the candidate as-is
            parsed, error = self.parse_json_safe(candidate)
            if parsed is not None:
                logger.debug(f"JSON parsing succeeded with candidate {i + 1}")
                return parsed, None

            # Try to fix common issues
            fixed_candidates = self.try_fix_common_json_issues(candidate)
            for j, fixed in enumerate(fixed_candidates):
                if fixed != candidate:  # Only try if different
                    logger.debug(
                        f"Trying fixed candidate {i + 1}.{j + 1}: {fixed[:100]}..."
                    )
                    parsed, error = self.parse_json_safe(fixed)
                    if parsed is not None:
                        logger.debug(
                            f"JSON parsing succeeded with fixed candidate {i + 1}.{j + 1}"
                        )
                        return parsed, None

        # If all parsing failed, return the best error message
        error_msg = f"Failed to extract valid JSON from response. Tried {len(candidates)} candidates."
        logger.warning(
            f"JSON parsing failed: {error_msg}. Original text: {text[:200]}..."
        )
        return None, error_msg

    def xǁRobustJSONParserǁextract_and_parse_json__mutmut_13(
        self, text: str, max_candidates: int = 5
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Extract and parse JSON from LLM response with multiple fallback strategies.

        Args:
            text: Text containing JSON response from LLM.
            max_candidates: Maximum number of JSON candidates to try.

        Returns:
            Tuple of (parsed_json, error_message). Returns None, error_msg if all parsing fails.
        """
        if not text or not text.strip():
            logger.debug("JSON parsing failed: Empty response text")
            return None, "Empty response text"

        # Clean the response
        cleaned_text = self.clean_llm_response(None)
        if not cleaned_text:
            logger.debug("JSON parsing failed: Response became empty after cleaning")
            return None, "Response became empty after cleaning"

        # Try parsing the cleaned text directly first
        parsed, error = self.parse_json_safe(cleaned_text)
        if parsed is not None:
            logger.debug("JSON parsing succeeded with direct parsing")
            return parsed, None

        # Extract JSON candidates from the cleaned text
        candidates = self.extract_json_from_text(cleaned_text)

        # Limit candidates to avoid excessive processing
        candidates = candidates[:max_candidates]
        logger.debug(f"Extracted {len(candidates)} JSON candidates from response")

        # Try each candidate
        for i, candidate in enumerate(candidates):
            logger.debug(f"Trying candidate {i + 1}: {candidate[:100]}...")
            # Try the candidate as-is
            parsed, error = self.parse_json_safe(candidate)
            if parsed is not None:
                logger.debug(f"JSON parsing succeeded with candidate {i + 1}")
                return parsed, None

            # Try to fix common issues
            fixed_candidates = self.try_fix_common_json_issues(candidate)
            for j, fixed in enumerate(fixed_candidates):
                if fixed != candidate:  # Only try if different
                    logger.debug(
                        f"Trying fixed candidate {i + 1}.{j + 1}: {fixed[:100]}..."
                    )
                    parsed, error = self.parse_json_safe(fixed)
                    if parsed is not None:
                        logger.debug(
                            f"JSON parsing succeeded with fixed candidate {i + 1}.{j + 1}"
                        )
                        return parsed, None

        # If all parsing failed, return the best error message
        error_msg = f"Failed to extract valid JSON from response. Tried {len(candidates)} candidates."
        logger.warning(
            f"JSON parsing failed: {error_msg}. Original text: {text[:200]}..."
        )
        return None, error_msg

    def xǁRobustJSONParserǁextract_and_parse_json__mutmut_14(
        self, text: str, max_candidates: int = 5
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Extract and parse JSON from LLM response with multiple fallback strategies.

        Args:
            text: Text containing JSON response from LLM.
            max_candidates: Maximum number of JSON candidates to try.

        Returns:
            Tuple of (parsed_json, error_message). Returns None, error_msg if all parsing fails.
        """
        if not text or not text.strip():
            logger.debug("JSON parsing failed: Empty response text")
            return None, "Empty response text"

        # Clean the response
        cleaned_text = self.clean_llm_response(text)
        if cleaned_text:
            logger.debug("JSON parsing failed: Response became empty after cleaning")
            return None, "Response became empty after cleaning"

        # Try parsing the cleaned text directly first
        parsed, error = self.parse_json_safe(cleaned_text)
        if parsed is not None:
            logger.debug("JSON parsing succeeded with direct parsing")
            return parsed, None

        # Extract JSON candidates from the cleaned text
        candidates = self.extract_json_from_text(cleaned_text)

        # Limit candidates to avoid excessive processing
        candidates = candidates[:max_candidates]
        logger.debug(f"Extracted {len(candidates)} JSON candidates from response")

        # Try each candidate
        for i, candidate in enumerate(candidates):
            logger.debug(f"Trying candidate {i + 1}: {candidate[:100]}...")
            # Try the candidate as-is
            parsed, error = self.parse_json_safe(candidate)
            if parsed is not None:
                logger.debug(f"JSON parsing succeeded with candidate {i + 1}")
                return parsed, None

            # Try to fix common issues
            fixed_candidates = self.try_fix_common_json_issues(candidate)
            for j, fixed in enumerate(fixed_candidates):
                if fixed != candidate:  # Only try if different
                    logger.debug(
                        f"Trying fixed candidate {i + 1}.{j + 1}: {fixed[:100]}..."
                    )
                    parsed, error = self.parse_json_safe(fixed)
                    if parsed is not None:
                        logger.debug(
                            f"JSON parsing succeeded with fixed candidate {i + 1}.{j + 1}"
                        )
                        return parsed, None

        # If all parsing failed, return the best error message
        error_msg = f"Failed to extract valid JSON from response. Tried {len(candidates)} candidates."
        logger.warning(
            f"JSON parsing failed: {error_msg}. Original text: {text[:200]}..."
        )
        return None, error_msg

    def xǁRobustJSONParserǁextract_and_parse_json__mutmut_15(
        self, text: str, max_candidates: int = 5
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Extract and parse JSON from LLM response with multiple fallback strategies.

        Args:
            text: Text containing JSON response from LLM.
            max_candidates: Maximum number of JSON candidates to try.

        Returns:
            Tuple of (parsed_json, error_message). Returns None, error_msg if all parsing fails.
        """
        if not text or not text.strip():
            logger.debug("JSON parsing failed: Empty response text")
            return None, "Empty response text"

        # Clean the response
        cleaned_text = self.clean_llm_response(text)
        if not cleaned_text:
            logger.debug(None)
            return None, "Response became empty after cleaning"

        # Try parsing the cleaned text directly first
        parsed, error = self.parse_json_safe(cleaned_text)
        if parsed is not None:
            logger.debug("JSON parsing succeeded with direct parsing")
            return parsed, None

        # Extract JSON candidates from the cleaned text
        candidates = self.extract_json_from_text(cleaned_text)

        # Limit candidates to avoid excessive processing
        candidates = candidates[:max_candidates]
        logger.debug(f"Extracted {len(candidates)} JSON candidates from response")

        # Try each candidate
        for i, candidate in enumerate(candidates):
            logger.debug(f"Trying candidate {i + 1}: {candidate[:100]}...")
            # Try the candidate as-is
            parsed, error = self.parse_json_safe(candidate)
            if parsed is not None:
                logger.debug(f"JSON parsing succeeded with candidate {i + 1}")
                return parsed, None

            # Try to fix common issues
            fixed_candidates = self.try_fix_common_json_issues(candidate)
            for j, fixed in enumerate(fixed_candidates):
                if fixed != candidate:  # Only try if different
                    logger.debug(
                        f"Trying fixed candidate {i + 1}.{j + 1}: {fixed[:100]}..."
                    )
                    parsed, error = self.parse_json_safe(fixed)
                    if parsed is not None:
                        logger.debug(
                            f"JSON parsing succeeded with fixed candidate {i + 1}.{j + 1}"
                        )
                        return parsed, None

        # If all parsing failed, return the best error message
        error_msg = f"Failed to extract valid JSON from response. Tried {len(candidates)} candidates."
        logger.warning(
            f"JSON parsing failed: {error_msg}. Original text: {text[:200]}..."
        )
        return None, error_msg

    def xǁRobustJSONParserǁextract_and_parse_json__mutmut_16(
        self, text: str, max_candidates: int = 5
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Extract and parse JSON from LLM response with multiple fallback strategies.

        Args:
            text: Text containing JSON response from LLM.
            max_candidates: Maximum number of JSON candidates to try.

        Returns:
            Tuple of (parsed_json, error_message). Returns None, error_msg if all parsing fails.
        """
        if not text or not text.strip():
            logger.debug("JSON parsing failed: Empty response text")
            return None, "Empty response text"

        # Clean the response
        cleaned_text = self.clean_llm_response(text)
        if not cleaned_text:
            logger.debug(
                "XXJSON parsing failed: Response became empty after cleaningXX"
            )
            return None, "Response became empty after cleaning"

        # Try parsing the cleaned text directly first
        parsed, error = self.parse_json_safe(cleaned_text)
        if parsed is not None:
            logger.debug("JSON parsing succeeded with direct parsing")
            return parsed, None

        # Extract JSON candidates from the cleaned text
        candidates = self.extract_json_from_text(cleaned_text)

        # Limit candidates to avoid excessive processing
        candidates = candidates[:max_candidates]
        logger.debug(f"Extracted {len(candidates)} JSON candidates from response")

        # Try each candidate
        for i, candidate in enumerate(candidates):
            logger.debug(f"Trying candidate {i + 1}: {candidate[:100]}...")
            # Try the candidate as-is
            parsed, error = self.parse_json_safe(candidate)
            if parsed is not None:
                logger.debug(f"JSON parsing succeeded with candidate {i + 1}")
                return parsed, None

            # Try to fix common issues
            fixed_candidates = self.try_fix_common_json_issues(candidate)
            for j, fixed in enumerate(fixed_candidates):
                if fixed != candidate:  # Only try if different
                    logger.debug(
                        f"Trying fixed candidate {i + 1}.{j + 1}: {fixed[:100]}..."
                    )
                    parsed, error = self.parse_json_safe(fixed)
                    if parsed is not None:
                        logger.debug(
                            f"JSON parsing succeeded with fixed candidate {i + 1}.{j + 1}"
                        )
                        return parsed, None

        # If all parsing failed, return the best error message
        error_msg = f"Failed to extract valid JSON from response. Tried {len(candidates)} candidates."
        logger.warning(
            f"JSON parsing failed: {error_msg}. Original text: {text[:200]}..."
        )
        return None, error_msg

    def xǁRobustJSONParserǁextract_and_parse_json__mutmut_17(
        self, text: str, max_candidates: int = 5
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Extract and parse JSON from LLM response with multiple fallback strategies.

        Args:
            text: Text containing JSON response from LLM.
            max_candidates: Maximum number of JSON candidates to try.

        Returns:
            Tuple of (parsed_json, error_message). Returns None, error_msg if all parsing fails.
        """
        if not text or not text.strip():
            logger.debug("JSON parsing failed: Empty response text")
            return None, "Empty response text"

        # Clean the response
        cleaned_text = self.clean_llm_response(text)
        if not cleaned_text:
            logger.debug("json parsing failed: response became empty after cleaning")
            return None, "Response became empty after cleaning"

        # Try parsing the cleaned text directly first
        parsed, error = self.parse_json_safe(cleaned_text)
        if parsed is not None:
            logger.debug("JSON parsing succeeded with direct parsing")
            return parsed, None

        # Extract JSON candidates from the cleaned text
        candidates = self.extract_json_from_text(cleaned_text)

        # Limit candidates to avoid excessive processing
        candidates = candidates[:max_candidates]
        logger.debug(f"Extracted {len(candidates)} JSON candidates from response")

        # Try each candidate
        for i, candidate in enumerate(candidates):
            logger.debug(f"Trying candidate {i + 1}: {candidate[:100]}...")
            # Try the candidate as-is
            parsed, error = self.parse_json_safe(candidate)
            if parsed is not None:
                logger.debug(f"JSON parsing succeeded with candidate {i + 1}")
                return parsed, None

            # Try to fix common issues
            fixed_candidates = self.try_fix_common_json_issues(candidate)
            for j, fixed in enumerate(fixed_candidates):
                if fixed != candidate:  # Only try if different
                    logger.debug(
                        f"Trying fixed candidate {i + 1}.{j + 1}: {fixed[:100]}..."
                    )
                    parsed, error = self.parse_json_safe(fixed)
                    if parsed is not None:
                        logger.debug(
                            f"JSON parsing succeeded with fixed candidate {i + 1}.{j + 1}"
                        )
                        return parsed, None

        # If all parsing failed, return the best error message
        error_msg = f"Failed to extract valid JSON from response. Tried {len(candidates)} candidates."
        logger.warning(
            f"JSON parsing failed: {error_msg}. Original text: {text[:200]}..."
        )
        return None, error_msg

    def xǁRobustJSONParserǁextract_and_parse_json__mutmut_18(
        self, text: str, max_candidates: int = 5
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Extract and parse JSON from LLM response with multiple fallback strategies.

        Args:
            text: Text containing JSON response from LLM.
            max_candidates: Maximum number of JSON candidates to try.

        Returns:
            Tuple of (parsed_json, error_message). Returns None, error_msg if all parsing fails.
        """
        if not text or not text.strip():
            logger.debug("JSON parsing failed: Empty response text")
            return None, "Empty response text"

        # Clean the response
        cleaned_text = self.clean_llm_response(text)
        if not cleaned_text:
            logger.debug("JSON PARSING FAILED: RESPONSE BECAME EMPTY AFTER CLEANING")
            return None, "Response became empty after cleaning"

        # Try parsing the cleaned text directly first
        parsed, error = self.parse_json_safe(cleaned_text)
        if parsed is not None:
            logger.debug("JSON parsing succeeded with direct parsing")
            return parsed, None

        # Extract JSON candidates from the cleaned text
        candidates = self.extract_json_from_text(cleaned_text)

        # Limit candidates to avoid excessive processing
        candidates = candidates[:max_candidates]
        logger.debug(f"Extracted {len(candidates)} JSON candidates from response")

        # Try each candidate
        for i, candidate in enumerate(candidates):
            logger.debug(f"Trying candidate {i + 1}: {candidate[:100]}...")
            # Try the candidate as-is
            parsed, error = self.parse_json_safe(candidate)
            if parsed is not None:
                logger.debug(f"JSON parsing succeeded with candidate {i + 1}")
                return parsed, None

            # Try to fix common issues
            fixed_candidates = self.try_fix_common_json_issues(candidate)
            for j, fixed in enumerate(fixed_candidates):
                if fixed != candidate:  # Only try if different
                    logger.debug(
                        f"Trying fixed candidate {i + 1}.{j + 1}: {fixed[:100]}..."
                    )
                    parsed, error = self.parse_json_safe(fixed)
                    if parsed is not None:
                        logger.debug(
                            f"JSON parsing succeeded with fixed candidate {i + 1}.{j + 1}"
                        )
                        return parsed, None

        # If all parsing failed, return the best error message
        error_msg = f"Failed to extract valid JSON from response. Tried {len(candidates)} candidates."
        logger.warning(
            f"JSON parsing failed: {error_msg}. Original text: {text[:200]}..."
        )
        return None, error_msg

    def xǁRobustJSONParserǁextract_and_parse_json__mutmut_19(
        self, text: str, max_candidates: int = 5
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Extract and parse JSON from LLM response with multiple fallback strategies.

        Args:
            text: Text containing JSON response from LLM.
            max_candidates: Maximum number of JSON candidates to try.

        Returns:
            Tuple of (parsed_json, error_message). Returns None, error_msg if all parsing fails.
        """
        if not text or not text.strip():
            logger.debug("JSON parsing failed: Empty response text")
            return None, "Empty response text"

        # Clean the response
        cleaned_text = self.clean_llm_response(text)
        if not cleaned_text:
            logger.debug("JSON parsing failed: Response became empty after cleaning")
            return None, "XXResponse became empty after cleaningXX"

        # Try parsing the cleaned text directly first
        parsed, error = self.parse_json_safe(cleaned_text)
        if parsed is not None:
            logger.debug("JSON parsing succeeded with direct parsing")
            return parsed, None

        # Extract JSON candidates from the cleaned text
        candidates = self.extract_json_from_text(cleaned_text)

        # Limit candidates to avoid excessive processing
        candidates = candidates[:max_candidates]
        logger.debug(f"Extracted {len(candidates)} JSON candidates from response")

        # Try each candidate
        for i, candidate in enumerate(candidates):
            logger.debug(f"Trying candidate {i + 1}: {candidate[:100]}...")
            # Try the candidate as-is
            parsed, error = self.parse_json_safe(candidate)
            if parsed is not None:
                logger.debug(f"JSON parsing succeeded with candidate {i + 1}")
                return parsed, None

            # Try to fix common issues
            fixed_candidates = self.try_fix_common_json_issues(candidate)
            for j, fixed in enumerate(fixed_candidates):
                if fixed != candidate:  # Only try if different
                    logger.debug(
                        f"Trying fixed candidate {i + 1}.{j + 1}: {fixed[:100]}..."
                    )
                    parsed, error = self.parse_json_safe(fixed)
                    if parsed is not None:
                        logger.debug(
                            f"JSON parsing succeeded with fixed candidate {i + 1}.{j + 1}"
                        )
                        return parsed, None

        # If all parsing failed, return the best error message
        error_msg = f"Failed to extract valid JSON from response. Tried {len(candidates)} candidates."
        logger.warning(
            f"JSON parsing failed: {error_msg}. Original text: {text[:200]}..."
        )
        return None, error_msg

    def xǁRobustJSONParserǁextract_and_parse_json__mutmut_20(
        self, text: str, max_candidates: int = 5
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Extract and parse JSON from LLM response with multiple fallback strategies.

        Args:
            text: Text containing JSON response from LLM.
            max_candidates: Maximum number of JSON candidates to try.

        Returns:
            Tuple of (parsed_json, error_message). Returns None, error_msg if all parsing fails.
        """
        if not text or not text.strip():
            logger.debug("JSON parsing failed: Empty response text")
            return None, "Empty response text"

        # Clean the response
        cleaned_text = self.clean_llm_response(text)
        if not cleaned_text:
            logger.debug("JSON parsing failed: Response became empty after cleaning")
            return None, "response became empty after cleaning"

        # Try parsing the cleaned text directly first
        parsed, error = self.parse_json_safe(cleaned_text)
        if parsed is not None:
            logger.debug("JSON parsing succeeded with direct parsing")
            return parsed, None

        # Extract JSON candidates from the cleaned text
        candidates = self.extract_json_from_text(cleaned_text)

        # Limit candidates to avoid excessive processing
        candidates = candidates[:max_candidates]
        logger.debug(f"Extracted {len(candidates)} JSON candidates from response")

        # Try each candidate
        for i, candidate in enumerate(candidates):
            logger.debug(f"Trying candidate {i + 1}: {candidate[:100]}...")
            # Try the candidate as-is
            parsed, error = self.parse_json_safe(candidate)
            if parsed is not None:
                logger.debug(f"JSON parsing succeeded with candidate {i + 1}")
                return parsed, None

            # Try to fix common issues
            fixed_candidates = self.try_fix_common_json_issues(candidate)
            for j, fixed in enumerate(fixed_candidates):
                if fixed != candidate:  # Only try if different
                    logger.debug(
                        f"Trying fixed candidate {i + 1}.{j + 1}: {fixed[:100]}..."
                    )
                    parsed, error = self.parse_json_safe(fixed)
                    if parsed is not None:
                        logger.debug(
                            f"JSON parsing succeeded with fixed candidate {i + 1}.{j + 1}"
                        )
                        return parsed, None

        # If all parsing failed, return the best error message
        error_msg = f"Failed to extract valid JSON from response. Tried {len(candidates)} candidates."
        logger.warning(
            f"JSON parsing failed: {error_msg}. Original text: {text[:200]}..."
        )
        return None, error_msg

    def xǁRobustJSONParserǁextract_and_parse_json__mutmut_21(
        self, text: str, max_candidates: int = 5
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Extract and parse JSON from LLM response with multiple fallback strategies.

        Args:
            text: Text containing JSON response from LLM.
            max_candidates: Maximum number of JSON candidates to try.

        Returns:
            Tuple of (parsed_json, error_message). Returns None, error_msg if all parsing fails.
        """
        if not text or not text.strip():
            logger.debug("JSON parsing failed: Empty response text")
            return None, "Empty response text"

        # Clean the response
        cleaned_text = self.clean_llm_response(text)
        if not cleaned_text:
            logger.debug("JSON parsing failed: Response became empty after cleaning")
            return None, "RESPONSE BECAME EMPTY AFTER CLEANING"

        # Try parsing the cleaned text directly first
        parsed, error = self.parse_json_safe(cleaned_text)
        if parsed is not None:
            logger.debug("JSON parsing succeeded with direct parsing")
            return parsed, None

        # Extract JSON candidates from the cleaned text
        candidates = self.extract_json_from_text(cleaned_text)

        # Limit candidates to avoid excessive processing
        candidates = candidates[:max_candidates]
        logger.debug(f"Extracted {len(candidates)} JSON candidates from response")

        # Try each candidate
        for i, candidate in enumerate(candidates):
            logger.debug(f"Trying candidate {i + 1}: {candidate[:100]}...")
            # Try the candidate as-is
            parsed, error = self.parse_json_safe(candidate)
            if parsed is not None:
                logger.debug(f"JSON parsing succeeded with candidate {i + 1}")
                return parsed, None

            # Try to fix common issues
            fixed_candidates = self.try_fix_common_json_issues(candidate)
            for j, fixed in enumerate(fixed_candidates):
                if fixed != candidate:  # Only try if different
                    logger.debug(
                        f"Trying fixed candidate {i + 1}.{j + 1}: {fixed[:100]}..."
                    )
                    parsed, error = self.parse_json_safe(fixed)
                    if parsed is not None:
                        logger.debug(
                            f"JSON parsing succeeded with fixed candidate {i + 1}.{j + 1}"
                        )
                        return parsed, None

        # If all parsing failed, return the best error message
        error_msg = f"Failed to extract valid JSON from response. Tried {len(candidates)} candidates."
        logger.warning(
            f"JSON parsing failed: {error_msg}. Original text: {text[:200]}..."
        )
        return None, error_msg

    def xǁRobustJSONParserǁextract_and_parse_json__mutmut_22(
        self, text: str, max_candidates: int = 5
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Extract and parse JSON from LLM response with multiple fallback strategies.

        Args:
            text: Text containing JSON response from LLM.
            max_candidates: Maximum number of JSON candidates to try.

        Returns:
            Tuple of (parsed_json, error_message). Returns None, error_msg if all parsing fails.
        """
        if not text or not text.strip():
            logger.debug("JSON parsing failed: Empty response text")
            return None, "Empty response text"

        # Clean the response
        cleaned_text = self.clean_llm_response(text)
        if not cleaned_text:
            logger.debug("JSON parsing failed: Response became empty after cleaning")
            return None, "Response became empty after cleaning"

        # Try parsing the cleaned text directly first
        parsed, error = None
        if parsed is not None:
            logger.debug("JSON parsing succeeded with direct parsing")
            return parsed, None

        # Extract JSON candidates from the cleaned text
        candidates = self.extract_json_from_text(cleaned_text)

        # Limit candidates to avoid excessive processing
        candidates = candidates[:max_candidates]
        logger.debug(f"Extracted {len(candidates)} JSON candidates from response")

        # Try each candidate
        for i, candidate in enumerate(candidates):
            logger.debug(f"Trying candidate {i + 1}: {candidate[:100]}...")
            # Try the candidate as-is
            parsed, error = self.parse_json_safe(candidate)
            if parsed is not None:
                logger.debug(f"JSON parsing succeeded with candidate {i + 1}")
                return parsed, None

            # Try to fix common issues
            fixed_candidates = self.try_fix_common_json_issues(candidate)
            for j, fixed in enumerate(fixed_candidates):
                if fixed != candidate:  # Only try if different
                    logger.debug(
                        f"Trying fixed candidate {i + 1}.{j + 1}: {fixed[:100]}..."
                    )
                    parsed, error = self.parse_json_safe(fixed)
                    if parsed is not None:
                        logger.debug(
                            f"JSON parsing succeeded with fixed candidate {i + 1}.{j + 1}"
                        )
                        return parsed, None

        # If all parsing failed, return the best error message
        error_msg = f"Failed to extract valid JSON from response. Tried {len(candidates)} candidates."
        logger.warning(
            f"JSON parsing failed: {error_msg}. Original text: {text[:200]}..."
        )
        return None, error_msg

    def xǁRobustJSONParserǁextract_and_parse_json__mutmut_23(
        self, text: str, max_candidates: int = 5
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Extract and parse JSON from LLM response with multiple fallback strategies.

        Args:
            text: Text containing JSON response from LLM.
            max_candidates: Maximum number of JSON candidates to try.

        Returns:
            Tuple of (parsed_json, error_message). Returns None, error_msg if all parsing fails.
        """
        if not text or not text.strip():
            logger.debug("JSON parsing failed: Empty response text")
            return None, "Empty response text"

        # Clean the response
        cleaned_text = self.clean_llm_response(text)
        if not cleaned_text:
            logger.debug("JSON parsing failed: Response became empty after cleaning")
            return None, "Response became empty after cleaning"

        # Try parsing the cleaned text directly first
        parsed, error = self.parse_json_safe(None)
        if parsed is not None:
            logger.debug("JSON parsing succeeded with direct parsing")
            return parsed, None

        # Extract JSON candidates from the cleaned text
        candidates = self.extract_json_from_text(cleaned_text)

        # Limit candidates to avoid excessive processing
        candidates = candidates[:max_candidates]
        logger.debug(f"Extracted {len(candidates)} JSON candidates from response")

        # Try each candidate
        for i, candidate in enumerate(candidates):
            logger.debug(f"Trying candidate {i + 1}: {candidate[:100]}...")
            # Try the candidate as-is
            parsed, error = self.parse_json_safe(candidate)
            if parsed is not None:
                logger.debug(f"JSON parsing succeeded with candidate {i + 1}")
                return parsed, None

            # Try to fix common issues
            fixed_candidates = self.try_fix_common_json_issues(candidate)
            for j, fixed in enumerate(fixed_candidates):
                if fixed != candidate:  # Only try if different
                    logger.debug(
                        f"Trying fixed candidate {i + 1}.{j + 1}: {fixed[:100]}..."
                    )
                    parsed, error = self.parse_json_safe(fixed)
                    if parsed is not None:
                        logger.debug(
                            f"JSON parsing succeeded with fixed candidate {i + 1}.{j + 1}"
                        )
                        return parsed, None

        # If all parsing failed, return the best error message
        error_msg = f"Failed to extract valid JSON from response. Tried {len(candidates)} candidates."
        logger.warning(
            f"JSON parsing failed: {error_msg}. Original text: {text[:200]}..."
        )
        return None, error_msg

    def xǁRobustJSONParserǁextract_and_parse_json__mutmut_24(
        self, text: str, max_candidates: int = 5
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Extract and parse JSON from LLM response with multiple fallback strategies.

        Args:
            text: Text containing JSON response from LLM.
            max_candidates: Maximum number of JSON candidates to try.

        Returns:
            Tuple of (parsed_json, error_message). Returns None, error_msg if all parsing fails.
        """
        if not text or not text.strip():
            logger.debug("JSON parsing failed: Empty response text")
            return None, "Empty response text"

        # Clean the response
        cleaned_text = self.clean_llm_response(text)
        if not cleaned_text:
            logger.debug("JSON parsing failed: Response became empty after cleaning")
            return None, "Response became empty after cleaning"

        # Try parsing the cleaned text directly first
        parsed, error = self.parse_json_safe(cleaned_text)
        if parsed is None:
            logger.debug("JSON parsing succeeded with direct parsing")
            return parsed, None

        # Extract JSON candidates from the cleaned text
        candidates = self.extract_json_from_text(cleaned_text)

        # Limit candidates to avoid excessive processing
        candidates = candidates[:max_candidates]
        logger.debug(f"Extracted {len(candidates)} JSON candidates from response")

        # Try each candidate
        for i, candidate in enumerate(candidates):
            logger.debug(f"Trying candidate {i + 1}: {candidate[:100]}...")
            # Try the candidate as-is
            parsed, error = self.parse_json_safe(candidate)
            if parsed is not None:
                logger.debug(f"JSON parsing succeeded with candidate {i + 1}")
                return parsed, None

            # Try to fix common issues
            fixed_candidates = self.try_fix_common_json_issues(candidate)
            for j, fixed in enumerate(fixed_candidates):
                if fixed != candidate:  # Only try if different
                    logger.debug(
                        f"Trying fixed candidate {i + 1}.{j + 1}: {fixed[:100]}..."
                    )
                    parsed, error = self.parse_json_safe(fixed)
                    if parsed is not None:
                        logger.debug(
                            f"JSON parsing succeeded with fixed candidate {i + 1}.{j + 1}"
                        )
                        return parsed, None

        # If all parsing failed, return the best error message
        error_msg = f"Failed to extract valid JSON from response. Tried {len(candidates)} candidates."
        logger.warning(
            f"JSON parsing failed: {error_msg}. Original text: {text[:200]}..."
        )
        return None, error_msg

    def xǁRobustJSONParserǁextract_and_parse_json__mutmut_25(
        self, text: str, max_candidates: int = 5
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Extract and parse JSON from LLM response with multiple fallback strategies.

        Args:
            text: Text containing JSON response from LLM.
            max_candidates: Maximum number of JSON candidates to try.

        Returns:
            Tuple of (parsed_json, error_message). Returns None, error_msg if all parsing fails.
        """
        if not text or not text.strip():
            logger.debug("JSON parsing failed: Empty response text")
            return None, "Empty response text"

        # Clean the response
        cleaned_text = self.clean_llm_response(text)
        if not cleaned_text:
            logger.debug("JSON parsing failed: Response became empty after cleaning")
            return None, "Response became empty after cleaning"

        # Try parsing the cleaned text directly first
        parsed, error = self.parse_json_safe(cleaned_text)
        if parsed is not None:
            logger.debug(None)
            return parsed, None

        # Extract JSON candidates from the cleaned text
        candidates = self.extract_json_from_text(cleaned_text)

        # Limit candidates to avoid excessive processing
        candidates = candidates[:max_candidates]
        logger.debug(f"Extracted {len(candidates)} JSON candidates from response")

        # Try each candidate
        for i, candidate in enumerate(candidates):
            logger.debug(f"Trying candidate {i + 1}: {candidate[:100]}...")
            # Try the candidate as-is
            parsed, error = self.parse_json_safe(candidate)
            if parsed is not None:
                logger.debug(f"JSON parsing succeeded with candidate {i + 1}")
                return parsed, None

            # Try to fix common issues
            fixed_candidates = self.try_fix_common_json_issues(candidate)
            for j, fixed in enumerate(fixed_candidates):
                if fixed != candidate:  # Only try if different
                    logger.debug(
                        f"Trying fixed candidate {i + 1}.{j + 1}: {fixed[:100]}..."
                    )
                    parsed, error = self.parse_json_safe(fixed)
                    if parsed is not None:
                        logger.debug(
                            f"JSON parsing succeeded with fixed candidate {i + 1}.{j + 1}"
                        )
                        return parsed, None

        # If all parsing failed, return the best error message
        error_msg = f"Failed to extract valid JSON from response. Tried {len(candidates)} candidates."
        logger.warning(
            f"JSON parsing failed: {error_msg}. Original text: {text[:200]}..."
        )
        return None, error_msg

    def xǁRobustJSONParserǁextract_and_parse_json__mutmut_26(
        self, text: str, max_candidates: int = 5
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Extract and parse JSON from LLM response with multiple fallback strategies.

        Args:
            text: Text containing JSON response from LLM.
            max_candidates: Maximum number of JSON candidates to try.

        Returns:
            Tuple of (parsed_json, error_message). Returns None, error_msg if all parsing fails.
        """
        if not text or not text.strip():
            logger.debug("JSON parsing failed: Empty response text")
            return None, "Empty response text"

        # Clean the response
        cleaned_text = self.clean_llm_response(text)
        if not cleaned_text:
            logger.debug("JSON parsing failed: Response became empty after cleaning")
            return None, "Response became empty after cleaning"

        # Try parsing the cleaned text directly first
        parsed, error = self.parse_json_safe(cleaned_text)
        if parsed is not None:
            logger.debug("XXJSON parsing succeeded with direct parsingXX")
            return parsed, None

        # Extract JSON candidates from the cleaned text
        candidates = self.extract_json_from_text(cleaned_text)

        # Limit candidates to avoid excessive processing
        candidates = candidates[:max_candidates]
        logger.debug(f"Extracted {len(candidates)} JSON candidates from response")

        # Try each candidate
        for i, candidate in enumerate(candidates):
            logger.debug(f"Trying candidate {i + 1}: {candidate[:100]}...")
            # Try the candidate as-is
            parsed, error = self.parse_json_safe(candidate)
            if parsed is not None:
                logger.debug(f"JSON parsing succeeded with candidate {i + 1}")
                return parsed, None

            # Try to fix common issues
            fixed_candidates = self.try_fix_common_json_issues(candidate)
            for j, fixed in enumerate(fixed_candidates):
                if fixed != candidate:  # Only try if different
                    logger.debug(
                        f"Trying fixed candidate {i + 1}.{j + 1}: {fixed[:100]}..."
                    )
                    parsed, error = self.parse_json_safe(fixed)
                    if parsed is not None:
                        logger.debug(
                            f"JSON parsing succeeded with fixed candidate {i + 1}.{j + 1}"
                        )
                        return parsed, None

        # If all parsing failed, return the best error message
        error_msg = f"Failed to extract valid JSON from response. Tried {len(candidates)} candidates."
        logger.warning(
            f"JSON parsing failed: {error_msg}. Original text: {text[:200]}..."
        )
        return None, error_msg

    def xǁRobustJSONParserǁextract_and_parse_json__mutmut_27(
        self, text: str, max_candidates: int = 5
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Extract and parse JSON from LLM response with multiple fallback strategies.

        Args:
            text: Text containing JSON response from LLM.
            max_candidates: Maximum number of JSON candidates to try.

        Returns:
            Tuple of (parsed_json, error_message). Returns None, error_msg if all parsing fails.
        """
        if not text or not text.strip():
            logger.debug("JSON parsing failed: Empty response text")
            return None, "Empty response text"

        # Clean the response
        cleaned_text = self.clean_llm_response(text)
        if not cleaned_text:
            logger.debug("JSON parsing failed: Response became empty after cleaning")
            return None, "Response became empty after cleaning"

        # Try parsing the cleaned text directly first
        parsed, error = self.parse_json_safe(cleaned_text)
        if parsed is not None:
            logger.debug("json parsing succeeded with direct parsing")
            return parsed, None

        # Extract JSON candidates from the cleaned text
        candidates = self.extract_json_from_text(cleaned_text)

        # Limit candidates to avoid excessive processing
        candidates = candidates[:max_candidates]
        logger.debug(f"Extracted {len(candidates)} JSON candidates from response")

        # Try each candidate
        for i, candidate in enumerate(candidates):
            logger.debug(f"Trying candidate {i + 1}: {candidate[:100]}...")
            # Try the candidate as-is
            parsed, error = self.parse_json_safe(candidate)
            if parsed is not None:
                logger.debug(f"JSON parsing succeeded with candidate {i + 1}")
                return parsed, None

            # Try to fix common issues
            fixed_candidates = self.try_fix_common_json_issues(candidate)
            for j, fixed in enumerate(fixed_candidates):
                if fixed != candidate:  # Only try if different
                    logger.debug(
                        f"Trying fixed candidate {i + 1}.{j + 1}: {fixed[:100]}..."
                    )
                    parsed, error = self.parse_json_safe(fixed)
                    if parsed is not None:
                        logger.debug(
                            f"JSON parsing succeeded with fixed candidate {i + 1}.{j + 1}"
                        )
                        return parsed, None

        # If all parsing failed, return the best error message
        error_msg = f"Failed to extract valid JSON from response. Tried {len(candidates)} candidates."
        logger.warning(
            f"JSON parsing failed: {error_msg}. Original text: {text[:200]}..."
        )
        return None, error_msg

    def xǁRobustJSONParserǁextract_and_parse_json__mutmut_28(
        self, text: str, max_candidates: int = 5
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Extract and parse JSON from LLM response with multiple fallback strategies.

        Args:
            text: Text containing JSON response from LLM.
            max_candidates: Maximum number of JSON candidates to try.

        Returns:
            Tuple of (parsed_json, error_message). Returns None, error_msg if all parsing fails.
        """
        if not text or not text.strip():
            logger.debug("JSON parsing failed: Empty response text")
            return None, "Empty response text"

        # Clean the response
        cleaned_text = self.clean_llm_response(text)
        if not cleaned_text:
            logger.debug("JSON parsing failed: Response became empty after cleaning")
            return None, "Response became empty after cleaning"

        # Try parsing the cleaned text directly first
        parsed, error = self.parse_json_safe(cleaned_text)
        if parsed is not None:
            logger.debug("JSON PARSING SUCCEEDED WITH DIRECT PARSING")
            return parsed, None

        # Extract JSON candidates from the cleaned text
        candidates = self.extract_json_from_text(cleaned_text)

        # Limit candidates to avoid excessive processing
        candidates = candidates[:max_candidates]
        logger.debug(f"Extracted {len(candidates)} JSON candidates from response")

        # Try each candidate
        for i, candidate in enumerate(candidates):
            logger.debug(f"Trying candidate {i + 1}: {candidate[:100]}...")
            # Try the candidate as-is
            parsed, error = self.parse_json_safe(candidate)
            if parsed is not None:
                logger.debug(f"JSON parsing succeeded with candidate {i + 1}")
                return parsed, None

            # Try to fix common issues
            fixed_candidates = self.try_fix_common_json_issues(candidate)
            for j, fixed in enumerate(fixed_candidates):
                if fixed != candidate:  # Only try if different
                    logger.debug(
                        f"Trying fixed candidate {i + 1}.{j + 1}: {fixed[:100]}..."
                    )
                    parsed, error = self.parse_json_safe(fixed)
                    if parsed is not None:
                        logger.debug(
                            f"JSON parsing succeeded with fixed candidate {i + 1}.{j + 1}"
                        )
                        return parsed, None

        # If all parsing failed, return the best error message
        error_msg = f"Failed to extract valid JSON from response. Tried {len(candidates)} candidates."
        logger.warning(
            f"JSON parsing failed: {error_msg}. Original text: {text[:200]}..."
        )
        return None, error_msg

    def xǁRobustJSONParserǁextract_and_parse_json__mutmut_29(
        self, text: str, max_candidates: int = 5
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Extract and parse JSON from LLM response with multiple fallback strategies.

        Args:
            text: Text containing JSON response from LLM.
            max_candidates: Maximum number of JSON candidates to try.

        Returns:
            Tuple of (parsed_json, error_message). Returns None, error_msg if all parsing fails.
        """
        if not text or not text.strip():
            logger.debug("JSON parsing failed: Empty response text")
            return None, "Empty response text"

        # Clean the response
        cleaned_text = self.clean_llm_response(text)
        if not cleaned_text:
            logger.debug("JSON parsing failed: Response became empty after cleaning")
            return None, "Response became empty after cleaning"

        # Try parsing the cleaned text directly first
        parsed, error = self.parse_json_safe(cleaned_text)
        if parsed is not None:
            logger.debug("JSON parsing succeeded with direct parsing")
            return parsed, None

        # Extract JSON candidates from the cleaned text
        candidates = None

        # Limit candidates to avoid excessive processing
        candidates = candidates[:max_candidates]
        logger.debug(f"Extracted {len(candidates)} JSON candidates from response")

        # Try each candidate
        for i, candidate in enumerate(candidates):
            logger.debug(f"Trying candidate {i + 1}: {candidate[:100]}...")
            # Try the candidate as-is
            parsed, error = self.parse_json_safe(candidate)
            if parsed is not None:
                logger.debug(f"JSON parsing succeeded with candidate {i + 1}")
                return parsed, None

            # Try to fix common issues
            fixed_candidates = self.try_fix_common_json_issues(candidate)
            for j, fixed in enumerate(fixed_candidates):
                if fixed != candidate:  # Only try if different
                    logger.debug(
                        f"Trying fixed candidate {i + 1}.{j + 1}: {fixed[:100]}..."
                    )
                    parsed, error = self.parse_json_safe(fixed)
                    if parsed is not None:
                        logger.debug(
                            f"JSON parsing succeeded with fixed candidate {i + 1}.{j + 1}"
                        )
                        return parsed, None

        # If all parsing failed, return the best error message
        error_msg = f"Failed to extract valid JSON from response. Tried {len(candidates)} candidates."
        logger.warning(
            f"JSON parsing failed: {error_msg}. Original text: {text[:200]}..."
        )
        return None, error_msg

    def xǁRobustJSONParserǁextract_and_parse_json__mutmut_30(
        self, text: str, max_candidates: int = 5
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Extract and parse JSON from LLM response with multiple fallback strategies.

        Args:
            text: Text containing JSON response from LLM.
            max_candidates: Maximum number of JSON candidates to try.

        Returns:
            Tuple of (parsed_json, error_message). Returns None, error_msg if all parsing fails.
        """
        if not text or not text.strip():
            logger.debug("JSON parsing failed: Empty response text")
            return None, "Empty response text"

        # Clean the response
        cleaned_text = self.clean_llm_response(text)
        if not cleaned_text:
            logger.debug("JSON parsing failed: Response became empty after cleaning")
            return None, "Response became empty after cleaning"

        # Try parsing the cleaned text directly first
        parsed, error = self.parse_json_safe(cleaned_text)
        if parsed is not None:
            logger.debug("JSON parsing succeeded with direct parsing")
            return parsed, None

        # Extract JSON candidates from the cleaned text
        candidates = self.extract_json_from_text(None)

        # Limit candidates to avoid excessive processing
        candidates = candidates[:max_candidates]
        logger.debug(f"Extracted {len(candidates)} JSON candidates from response")

        # Try each candidate
        for i, candidate in enumerate(candidates):
            logger.debug(f"Trying candidate {i + 1}: {candidate[:100]}...")
            # Try the candidate as-is
            parsed, error = self.parse_json_safe(candidate)
            if parsed is not None:
                logger.debug(f"JSON parsing succeeded with candidate {i + 1}")
                return parsed, None

            # Try to fix common issues
            fixed_candidates = self.try_fix_common_json_issues(candidate)
            for j, fixed in enumerate(fixed_candidates):
                if fixed != candidate:  # Only try if different
                    logger.debug(
                        f"Trying fixed candidate {i + 1}.{j + 1}: {fixed[:100]}..."
                    )
                    parsed, error = self.parse_json_safe(fixed)
                    if parsed is not None:
                        logger.debug(
                            f"JSON parsing succeeded with fixed candidate {i + 1}.{j + 1}"
                        )
                        return parsed, None

        # If all parsing failed, return the best error message
        error_msg = f"Failed to extract valid JSON from response. Tried {len(candidates)} candidates."
        logger.warning(
            f"JSON parsing failed: {error_msg}. Original text: {text[:200]}..."
        )
        return None, error_msg

    def xǁRobustJSONParserǁextract_and_parse_json__mutmut_31(
        self, text: str, max_candidates: int = 5
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Extract and parse JSON from LLM response with multiple fallback strategies.

        Args:
            text: Text containing JSON response from LLM.
            max_candidates: Maximum number of JSON candidates to try.

        Returns:
            Tuple of (parsed_json, error_message). Returns None, error_msg if all parsing fails.
        """
        if not text or not text.strip():
            logger.debug("JSON parsing failed: Empty response text")
            return None, "Empty response text"

        # Clean the response
        cleaned_text = self.clean_llm_response(text)
        if not cleaned_text:
            logger.debug("JSON parsing failed: Response became empty after cleaning")
            return None, "Response became empty after cleaning"

        # Try parsing the cleaned text directly first
        parsed, error = self.parse_json_safe(cleaned_text)
        if parsed is not None:
            logger.debug("JSON parsing succeeded with direct parsing")
            return parsed, None

        # Extract JSON candidates from the cleaned text
        candidates = self.extract_json_from_text(cleaned_text)

        # Limit candidates to avoid excessive processing
        candidates = None
        logger.debug(f"Extracted {len(candidates)} JSON candidates from response")

        # Try each candidate
        for i, candidate in enumerate(candidates):
            logger.debug(f"Trying candidate {i + 1}: {candidate[:100]}...")
            # Try the candidate as-is
            parsed, error = self.parse_json_safe(candidate)
            if parsed is not None:
                logger.debug(f"JSON parsing succeeded with candidate {i + 1}")
                return parsed, None

            # Try to fix common issues
            fixed_candidates = self.try_fix_common_json_issues(candidate)
            for j, fixed in enumerate(fixed_candidates):
                if fixed != candidate:  # Only try if different
                    logger.debug(
                        f"Trying fixed candidate {i + 1}.{j + 1}: {fixed[:100]}..."
                    )
                    parsed, error = self.parse_json_safe(fixed)
                    if parsed is not None:
                        logger.debug(
                            f"JSON parsing succeeded with fixed candidate {i + 1}.{j + 1}"
                        )
                        return parsed, None

        # If all parsing failed, return the best error message
        error_msg = f"Failed to extract valid JSON from response. Tried {len(candidates)} candidates."
        logger.warning(
            f"JSON parsing failed: {error_msg}. Original text: {text[:200]}..."
        )
        return None, error_msg

    def xǁRobustJSONParserǁextract_and_parse_json__mutmut_32(
        self, text: str, max_candidates: int = 5
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Extract and parse JSON from LLM response with multiple fallback strategies.

        Args:
            text: Text containing JSON response from LLM.
            max_candidates: Maximum number of JSON candidates to try.

        Returns:
            Tuple of (parsed_json, error_message). Returns None, error_msg if all parsing fails.
        """
        if not text or not text.strip():
            logger.debug("JSON parsing failed: Empty response text")
            return None, "Empty response text"

        # Clean the response
        cleaned_text = self.clean_llm_response(text)
        if not cleaned_text:
            logger.debug("JSON parsing failed: Response became empty after cleaning")
            return None, "Response became empty after cleaning"

        # Try parsing the cleaned text directly first
        parsed, error = self.parse_json_safe(cleaned_text)
        if parsed is not None:
            logger.debug("JSON parsing succeeded with direct parsing")
            return parsed, None

        # Extract JSON candidates from the cleaned text
        candidates = self.extract_json_from_text(cleaned_text)

        # Limit candidates to avoid excessive processing
        candidates = candidates[:max_candidates]
        logger.debug(None)

        # Try each candidate
        for i, candidate in enumerate(candidates):
            logger.debug(f"Trying candidate {i + 1}: {candidate[:100]}...")
            # Try the candidate as-is
            parsed, error = self.parse_json_safe(candidate)
            if parsed is not None:
                logger.debug(f"JSON parsing succeeded with candidate {i + 1}")
                return parsed, None

            # Try to fix common issues
            fixed_candidates = self.try_fix_common_json_issues(candidate)
            for j, fixed in enumerate(fixed_candidates):
                if fixed != candidate:  # Only try if different
                    logger.debug(
                        f"Trying fixed candidate {i + 1}.{j + 1}: {fixed[:100]}..."
                    )
                    parsed, error = self.parse_json_safe(fixed)
                    if parsed is not None:
                        logger.debug(
                            f"JSON parsing succeeded with fixed candidate {i + 1}.{j + 1}"
                        )
                        return parsed, None

        # If all parsing failed, return the best error message
        error_msg = f"Failed to extract valid JSON from response. Tried {len(candidates)} candidates."
        logger.warning(
            f"JSON parsing failed: {error_msg}. Original text: {text[:200]}..."
        )
        return None, error_msg

    def xǁRobustJSONParserǁextract_and_parse_json__mutmut_33(
        self, text: str, max_candidates: int = 5
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Extract and parse JSON from LLM response with multiple fallback strategies.

        Args:
            text: Text containing JSON response from LLM.
            max_candidates: Maximum number of JSON candidates to try.

        Returns:
            Tuple of (parsed_json, error_message). Returns None, error_msg if all parsing fails.
        """
        if not text or not text.strip():
            logger.debug("JSON parsing failed: Empty response text")
            return None, "Empty response text"

        # Clean the response
        cleaned_text = self.clean_llm_response(text)
        if not cleaned_text:
            logger.debug("JSON parsing failed: Response became empty after cleaning")
            return None, "Response became empty after cleaning"

        # Try parsing the cleaned text directly first
        parsed, error = self.parse_json_safe(cleaned_text)
        if parsed is not None:
            logger.debug("JSON parsing succeeded with direct parsing")
            return parsed, None

        # Extract JSON candidates from the cleaned text
        candidates = self.extract_json_from_text(cleaned_text)

        # Limit candidates to avoid excessive processing
        candidates = candidates[:max_candidates]
        logger.debug(f"Extracted {len(candidates)} JSON candidates from response")

        # Try each candidate
        for i, candidate in enumerate(None):
            logger.debug(f"Trying candidate {i + 1}: {candidate[:100]}...")
            # Try the candidate as-is
            parsed, error = self.parse_json_safe(candidate)
            if parsed is not None:
                logger.debug(f"JSON parsing succeeded with candidate {i + 1}")
                return parsed, None

            # Try to fix common issues
            fixed_candidates = self.try_fix_common_json_issues(candidate)
            for j, fixed in enumerate(fixed_candidates):
                if fixed != candidate:  # Only try if different
                    logger.debug(
                        f"Trying fixed candidate {i + 1}.{j + 1}: {fixed[:100]}..."
                    )
                    parsed, error = self.parse_json_safe(fixed)
                    if parsed is not None:
                        logger.debug(
                            f"JSON parsing succeeded with fixed candidate {i + 1}.{j + 1}"
                        )
                        return parsed, None

        # If all parsing failed, return the best error message
        error_msg = f"Failed to extract valid JSON from response. Tried {len(candidates)} candidates."
        logger.warning(
            f"JSON parsing failed: {error_msg}. Original text: {text[:200]}..."
        )
        return None, error_msg

    def xǁRobustJSONParserǁextract_and_parse_json__mutmut_34(
        self, text: str, max_candidates: int = 5
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Extract and parse JSON from LLM response with multiple fallback strategies.

        Args:
            text: Text containing JSON response from LLM.
            max_candidates: Maximum number of JSON candidates to try.

        Returns:
            Tuple of (parsed_json, error_message). Returns None, error_msg if all parsing fails.
        """
        if not text or not text.strip():
            logger.debug("JSON parsing failed: Empty response text")
            return None, "Empty response text"

        # Clean the response
        cleaned_text = self.clean_llm_response(text)
        if not cleaned_text:
            logger.debug("JSON parsing failed: Response became empty after cleaning")
            return None, "Response became empty after cleaning"

        # Try parsing the cleaned text directly first
        parsed, error = self.parse_json_safe(cleaned_text)
        if parsed is not None:
            logger.debug("JSON parsing succeeded with direct parsing")
            return parsed, None

        # Extract JSON candidates from the cleaned text
        candidates = self.extract_json_from_text(cleaned_text)

        # Limit candidates to avoid excessive processing
        candidates = candidates[:max_candidates]
        logger.debug(f"Extracted {len(candidates)} JSON candidates from response")

        # Try each candidate
        for i, candidate in enumerate(candidates):
            logger.debug(None)
            # Try the candidate as-is
            parsed, error = self.parse_json_safe(candidate)
            if parsed is not None:
                logger.debug(f"JSON parsing succeeded with candidate {i + 1}")
                return parsed, None

            # Try to fix common issues
            fixed_candidates = self.try_fix_common_json_issues(candidate)
            for j, fixed in enumerate(fixed_candidates):
                if fixed != candidate:  # Only try if different
                    logger.debug(
                        f"Trying fixed candidate {i + 1}.{j + 1}: {fixed[:100]}..."
                    )
                    parsed, error = self.parse_json_safe(fixed)
                    if parsed is not None:
                        logger.debug(
                            f"JSON parsing succeeded with fixed candidate {i + 1}.{j + 1}"
                        )
                        return parsed, None

        # If all parsing failed, return the best error message
        error_msg = f"Failed to extract valid JSON from response. Tried {len(candidates)} candidates."
        logger.warning(
            f"JSON parsing failed: {error_msg}. Original text: {text[:200]}..."
        )
        return None, error_msg

    def xǁRobustJSONParserǁextract_and_parse_json__mutmut_35(
        self, text: str, max_candidates: int = 5
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Extract and parse JSON from LLM response with multiple fallback strategies.

        Args:
            text: Text containing JSON response from LLM.
            max_candidates: Maximum number of JSON candidates to try.

        Returns:
            Tuple of (parsed_json, error_message). Returns None, error_msg if all parsing fails.
        """
        if not text or not text.strip():
            logger.debug("JSON parsing failed: Empty response text")
            return None, "Empty response text"

        # Clean the response
        cleaned_text = self.clean_llm_response(text)
        if not cleaned_text:
            logger.debug("JSON parsing failed: Response became empty after cleaning")
            return None, "Response became empty after cleaning"

        # Try parsing the cleaned text directly first
        parsed, error = self.parse_json_safe(cleaned_text)
        if parsed is not None:
            logger.debug("JSON parsing succeeded with direct parsing")
            return parsed, None

        # Extract JSON candidates from the cleaned text
        candidates = self.extract_json_from_text(cleaned_text)

        # Limit candidates to avoid excessive processing
        candidates = candidates[:max_candidates]
        logger.debug(f"Extracted {len(candidates)} JSON candidates from response")

        # Try each candidate
        for i, candidate in enumerate(candidates):
            logger.debug(f"Trying candidate {i - 1}: {candidate[:100]}...")
            # Try the candidate as-is
            parsed, error = self.parse_json_safe(candidate)
            if parsed is not None:
                logger.debug(f"JSON parsing succeeded with candidate {i + 1}")
                return parsed, None

            # Try to fix common issues
            fixed_candidates = self.try_fix_common_json_issues(candidate)
            for j, fixed in enumerate(fixed_candidates):
                if fixed != candidate:  # Only try if different
                    logger.debug(
                        f"Trying fixed candidate {i + 1}.{j + 1}: {fixed[:100]}..."
                    )
                    parsed, error = self.parse_json_safe(fixed)
                    if parsed is not None:
                        logger.debug(
                            f"JSON parsing succeeded with fixed candidate {i + 1}.{j + 1}"
                        )
                        return parsed, None

        # If all parsing failed, return the best error message
        error_msg = f"Failed to extract valid JSON from response. Tried {len(candidates)} candidates."
        logger.warning(
            f"JSON parsing failed: {error_msg}. Original text: {text[:200]}..."
        )
        return None, error_msg

    def xǁRobustJSONParserǁextract_and_parse_json__mutmut_36(
        self, text: str, max_candidates: int = 5
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Extract and parse JSON from LLM response with multiple fallback strategies.

        Args:
            text: Text containing JSON response from LLM.
            max_candidates: Maximum number of JSON candidates to try.

        Returns:
            Tuple of (parsed_json, error_message). Returns None, error_msg if all parsing fails.
        """
        if not text or not text.strip():
            logger.debug("JSON parsing failed: Empty response text")
            return None, "Empty response text"

        # Clean the response
        cleaned_text = self.clean_llm_response(text)
        if not cleaned_text:
            logger.debug("JSON parsing failed: Response became empty after cleaning")
            return None, "Response became empty after cleaning"

        # Try parsing the cleaned text directly first
        parsed, error = self.parse_json_safe(cleaned_text)
        if parsed is not None:
            logger.debug("JSON parsing succeeded with direct parsing")
            return parsed, None

        # Extract JSON candidates from the cleaned text
        candidates = self.extract_json_from_text(cleaned_text)

        # Limit candidates to avoid excessive processing
        candidates = candidates[:max_candidates]
        logger.debug(f"Extracted {len(candidates)} JSON candidates from response")

        # Try each candidate
        for i, candidate in enumerate(candidates):
            logger.debug(f"Trying candidate {i + 2}: {candidate[:100]}...")
            # Try the candidate as-is
            parsed, error = self.parse_json_safe(candidate)
            if parsed is not None:
                logger.debug(f"JSON parsing succeeded with candidate {i + 1}")
                return parsed, None

            # Try to fix common issues
            fixed_candidates = self.try_fix_common_json_issues(candidate)
            for j, fixed in enumerate(fixed_candidates):
                if fixed != candidate:  # Only try if different
                    logger.debug(
                        f"Trying fixed candidate {i + 1}.{j + 1}: {fixed[:100]}..."
                    )
                    parsed, error = self.parse_json_safe(fixed)
                    if parsed is not None:
                        logger.debug(
                            f"JSON parsing succeeded with fixed candidate {i + 1}.{j + 1}"
                        )
                        return parsed, None

        # If all parsing failed, return the best error message
        error_msg = f"Failed to extract valid JSON from response. Tried {len(candidates)} candidates."
        logger.warning(
            f"JSON parsing failed: {error_msg}. Original text: {text[:200]}..."
        )
        return None, error_msg

    def xǁRobustJSONParserǁextract_and_parse_json__mutmut_37(
        self, text: str, max_candidates: int = 5
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Extract and parse JSON from LLM response with multiple fallback strategies.

        Args:
            text: Text containing JSON response from LLM.
            max_candidates: Maximum number of JSON candidates to try.

        Returns:
            Tuple of (parsed_json, error_message). Returns None, error_msg if all parsing fails.
        """
        if not text or not text.strip():
            logger.debug("JSON parsing failed: Empty response text")
            return None, "Empty response text"

        # Clean the response
        cleaned_text = self.clean_llm_response(text)
        if not cleaned_text:
            logger.debug("JSON parsing failed: Response became empty after cleaning")
            return None, "Response became empty after cleaning"

        # Try parsing the cleaned text directly first
        parsed, error = self.parse_json_safe(cleaned_text)
        if parsed is not None:
            logger.debug("JSON parsing succeeded with direct parsing")
            return parsed, None

        # Extract JSON candidates from the cleaned text
        candidates = self.extract_json_from_text(cleaned_text)

        # Limit candidates to avoid excessive processing
        candidates = candidates[:max_candidates]
        logger.debug(f"Extracted {len(candidates)} JSON candidates from response")

        # Try each candidate
        for i, candidate in enumerate(candidates):
            logger.debug(f"Trying candidate {i + 1}: {candidate[:101]}...")
            # Try the candidate as-is
            parsed, error = self.parse_json_safe(candidate)
            if parsed is not None:
                logger.debug(f"JSON parsing succeeded with candidate {i + 1}")
                return parsed, None

            # Try to fix common issues
            fixed_candidates = self.try_fix_common_json_issues(candidate)
            for j, fixed in enumerate(fixed_candidates):
                if fixed != candidate:  # Only try if different
                    logger.debug(
                        f"Trying fixed candidate {i + 1}.{j + 1}: {fixed[:100]}..."
                    )
                    parsed, error = self.parse_json_safe(fixed)
                    if parsed is not None:
                        logger.debug(
                            f"JSON parsing succeeded with fixed candidate {i + 1}.{j + 1}"
                        )
                        return parsed, None

        # If all parsing failed, return the best error message
        error_msg = f"Failed to extract valid JSON from response. Tried {len(candidates)} candidates."
        logger.warning(
            f"JSON parsing failed: {error_msg}. Original text: {text[:200]}..."
        )
        return None, error_msg

    def xǁRobustJSONParserǁextract_and_parse_json__mutmut_38(
        self, text: str, max_candidates: int = 5
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Extract and parse JSON from LLM response with multiple fallback strategies.

        Args:
            text: Text containing JSON response from LLM.
            max_candidates: Maximum number of JSON candidates to try.

        Returns:
            Tuple of (parsed_json, error_message). Returns None, error_msg if all parsing fails.
        """
        if not text or not text.strip():
            logger.debug("JSON parsing failed: Empty response text")
            return None, "Empty response text"

        # Clean the response
        cleaned_text = self.clean_llm_response(text)
        if not cleaned_text:
            logger.debug("JSON parsing failed: Response became empty after cleaning")
            return None, "Response became empty after cleaning"

        # Try parsing the cleaned text directly first
        parsed, error = self.parse_json_safe(cleaned_text)
        if parsed is not None:
            logger.debug("JSON parsing succeeded with direct parsing")
            return parsed, None

        # Extract JSON candidates from the cleaned text
        candidates = self.extract_json_from_text(cleaned_text)

        # Limit candidates to avoid excessive processing
        candidates = candidates[:max_candidates]
        logger.debug(f"Extracted {len(candidates)} JSON candidates from response")

        # Try each candidate
        for i, candidate in enumerate(candidates):
            logger.debug(f"Trying candidate {i + 1}: {candidate[:100]}...")
            # Try the candidate as-is
            parsed, error = None
            if parsed is not None:
                logger.debug(f"JSON parsing succeeded with candidate {i + 1}")
                return parsed, None

            # Try to fix common issues
            fixed_candidates = self.try_fix_common_json_issues(candidate)
            for j, fixed in enumerate(fixed_candidates):
                if fixed != candidate:  # Only try if different
                    logger.debug(
                        f"Trying fixed candidate {i + 1}.{j + 1}: {fixed[:100]}..."
                    )
                    parsed, error = self.parse_json_safe(fixed)
                    if parsed is not None:
                        logger.debug(
                            f"JSON parsing succeeded with fixed candidate {i + 1}.{j + 1}"
                        )
                        return parsed, None

        # If all parsing failed, return the best error message
        error_msg = f"Failed to extract valid JSON from response. Tried {len(candidates)} candidates."
        logger.warning(
            f"JSON parsing failed: {error_msg}. Original text: {text[:200]}..."
        )
        return None, error_msg

    def xǁRobustJSONParserǁextract_and_parse_json__mutmut_39(
        self, text: str, max_candidates: int = 5
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Extract and parse JSON from LLM response with multiple fallback strategies.

        Args:
            text: Text containing JSON response from LLM.
            max_candidates: Maximum number of JSON candidates to try.

        Returns:
            Tuple of (parsed_json, error_message). Returns None, error_msg if all parsing fails.
        """
        if not text or not text.strip():
            logger.debug("JSON parsing failed: Empty response text")
            return None, "Empty response text"

        # Clean the response
        cleaned_text = self.clean_llm_response(text)
        if not cleaned_text:
            logger.debug("JSON parsing failed: Response became empty after cleaning")
            return None, "Response became empty after cleaning"

        # Try parsing the cleaned text directly first
        parsed, error = self.parse_json_safe(cleaned_text)
        if parsed is not None:
            logger.debug("JSON parsing succeeded with direct parsing")
            return parsed, None

        # Extract JSON candidates from the cleaned text
        candidates = self.extract_json_from_text(cleaned_text)

        # Limit candidates to avoid excessive processing
        candidates = candidates[:max_candidates]
        logger.debug(f"Extracted {len(candidates)} JSON candidates from response")

        # Try each candidate
        for i, candidate in enumerate(candidates):
            logger.debug(f"Trying candidate {i + 1}: {candidate[:100]}...")
            # Try the candidate as-is
            parsed, error = self.parse_json_safe(None)
            if parsed is not None:
                logger.debug(f"JSON parsing succeeded with candidate {i + 1}")
                return parsed, None

            # Try to fix common issues
            fixed_candidates = self.try_fix_common_json_issues(candidate)
            for j, fixed in enumerate(fixed_candidates):
                if fixed != candidate:  # Only try if different
                    logger.debug(
                        f"Trying fixed candidate {i + 1}.{j + 1}: {fixed[:100]}..."
                    )
                    parsed, error = self.parse_json_safe(fixed)
                    if parsed is not None:
                        logger.debug(
                            f"JSON parsing succeeded with fixed candidate {i + 1}.{j + 1}"
                        )
                        return parsed, None

        # If all parsing failed, return the best error message
        error_msg = f"Failed to extract valid JSON from response. Tried {len(candidates)} candidates."
        logger.warning(
            f"JSON parsing failed: {error_msg}. Original text: {text[:200]}..."
        )
        return None, error_msg

    def xǁRobustJSONParserǁextract_and_parse_json__mutmut_40(
        self, text: str, max_candidates: int = 5
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Extract and parse JSON from LLM response with multiple fallback strategies.

        Args:
            text: Text containing JSON response from LLM.
            max_candidates: Maximum number of JSON candidates to try.

        Returns:
            Tuple of (parsed_json, error_message). Returns None, error_msg if all parsing fails.
        """
        if not text or not text.strip():
            logger.debug("JSON parsing failed: Empty response text")
            return None, "Empty response text"

        # Clean the response
        cleaned_text = self.clean_llm_response(text)
        if not cleaned_text:
            logger.debug("JSON parsing failed: Response became empty after cleaning")
            return None, "Response became empty after cleaning"

        # Try parsing the cleaned text directly first
        parsed, error = self.parse_json_safe(cleaned_text)
        if parsed is not None:
            logger.debug("JSON parsing succeeded with direct parsing")
            return parsed, None

        # Extract JSON candidates from the cleaned text
        candidates = self.extract_json_from_text(cleaned_text)

        # Limit candidates to avoid excessive processing
        candidates = candidates[:max_candidates]
        logger.debug(f"Extracted {len(candidates)} JSON candidates from response")

        # Try each candidate
        for i, candidate in enumerate(candidates):
            logger.debug(f"Trying candidate {i + 1}: {candidate[:100]}...")
            # Try the candidate as-is
            parsed, error = self.parse_json_safe(candidate)
            if parsed is None:
                logger.debug(f"JSON parsing succeeded with candidate {i + 1}")
                return parsed, None

            # Try to fix common issues
            fixed_candidates = self.try_fix_common_json_issues(candidate)
            for j, fixed in enumerate(fixed_candidates):
                if fixed != candidate:  # Only try if different
                    logger.debug(
                        f"Trying fixed candidate {i + 1}.{j + 1}: {fixed[:100]}..."
                    )
                    parsed, error = self.parse_json_safe(fixed)
                    if parsed is not None:
                        logger.debug(
                            f"JSON parsing succeeded with fixed candidate {i + 1}.{j + 1}"
                        )
                        return parsed, None

        # If all parsing failed, return the best error message
        error_msg = f"Failed to extract valid JSON from response. Tried {len(candidates)} candidates."
        logger.warning(
            f"JSON parsing failed: {error_msg}. Original text: {text[:200]}..."
        )
        return None, error_msg

    def xǁRobustJSONParserǁextract_and_parse_json__mutmut_41(
        self, text: str, max_candidates: int = 5
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Extract and parse JSON from LLM response with multiple fallback strategies.

        Args:
            text: Text containing JSON response from LLM.
            max_candidates: Maximum number of JSON candidates to try.

        Returns:
            Tuple of (parsed_json, error_message). Returns None, error_msg if all parsing fails.
        """
        if not text or not text.strip():
            logger.debug("JSON parsing failed: Empty response text")
            return None, "Empty response text"

        # Clean the response
        cleaned_text = self.clean_llm_response(text)
        if not cleaned_text:
            logger.debug("JSON parsing failed: Response became empty after cleaning")
            return None, "Response became empty after cleaning"

        # Try parsing the cleaned text directly first
        parsed, error = self.parse_json_safe(cleaned_text)
        if parsed is not None:
            logger.debug("JSON parsing succeeded with direct parsing")
            return parsed, None

        # Extract JSON candidates from the cleaned text
        candidates = self.extract_json_from_text(cleaned_text)

        # Limit candidates to avoid excessive processing
        candidates = candidates[:max_candidates]
        logger.debug(f"Extracted {len(candidates)} JSON candidates from response")

        # Try each candidate
        for i, candidate in enumerate(candidates):
            logger.debug(f"Trying candidate {i + 1}: {candidate[:100]}...")
            # Try the candidate as-is
            parsed, error = self.parse_json_safe(candidate)
            if parsed is not None:
                logger.debug(None)
                return parsed, None

            # Try to fix common issues
            fixed_candidates = self.try_fix_common_json_issues(candidate)
            for j, fixed in enumerate(fixed_candidates):
                if fixed != candidate:  # Only try if different
                    logger.debug(
                        f"Trying fixed candidate {i + 1}.{j + 1}: {fixed[:100]}..."
                    )
                    parsed, error = self.parse_json_safe(fixed)
                    if parsed is not None:
                        logger.debug(
                            f"JSON parsing succeeded with fixed candidate {i + 1}.{j + 1}"
                        )
                        return parsed, None

        # If all parsing failed, return the best error message
        error_msg = f"Failed to extract valid JSON from response. Tried {len(candidates)} candidates."
        logger.warning(
            f"JSON parsing failed: {error_msg}. Original text: {text[:200]}..."
        )
        return None, error_msg

    def xǁRobustJSONParserǁextract_and_parse_json__mutmut_42(
        self, text: str, max_candidates: int = 5
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Extract and parse JSON from LLM response with multiple fallback strategies.

        Args:
            text: Text containing JSON response from LLM.
            max_candidates: Maximum number of JSON candidates to try.

        Returns:
            Tuple of (parsed_json, error_message). Returns None, error_msg if all parsing fails.
        """
        if not text or not text.strip():
            logger.debug("JSON parsing failed: Empty response text")
            return None, "Empty response text"

        # Clean the response
        cleaned_text = self.clean_llm_response(text)
        if not cleaned_text:
            logger.debug("JSON parsing failed: Response became empty after cleaning")
            return None, "Response became empty after cleaning"

        # Try parsing the cleaned text directly first
        parsed, error = self.parse_json_safe(cleaned_text)
        if parsed is not None:
            logger.debug("JSON parsing succeeded with direct parsing")
            return parsed, None

        # Extract JSON candidates from the cleaned text
        candidates = self.extract_json_from_text(cleaned_text)

        # Limit candidates to avoid excessive processing
        candidates = candidates[:max_candidates]
        logger.debug(f"Extracted {len(candidates)} JSON candidates from response")

        # Try each candidate
        for i, candidate in enumerate(candidates):
            logger.debug(f"Trying candidate {i + 1}: {candidate[:100]}...")
            # Try the candidate as-is
            parsed, error = self.parse_json_safe(candidate)
            if parsed is not None:
                logger.debug(f"JSON parsing succeeded with candidate {i - 1}")
                return parsed, None

            # Try to fix common issues
            fixed_candidates = self.try_fix_common_json_issues(candidate)
            for j, fixed in enumerate(fixed_candidates):
                if fixed != candidate:  # Only try if different
                    logger.debug(
                        f"Trying fixed candidate {i + 1}.{j + 1}: {fixed[:100]}..."
                    )
                    parsed, error = self.parse_json_safe(fixed)
                    if parsed is not None:
                        logger.debug(
                            f"JSON parsing succeeded with fixed candidate {i + 1}.{j + 1}"
                        )
                        return parsed, None

        # If all parsing failed, return the best error message
        error_msg = f"Failed to extract valid JSON from response. Tried {len(candidates)} candidates."
        logger.warning(
            f"JSON parsing failed: {error_msg}. Original text: {text[:200]}..."
        )
        return None, error_msg

    def xǁRobustJSONParserǁextract_and_parse_json__mutmut_43(
        self, text: str, max_candidates: int = 5
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Extract and parse JSON from LLM response with multiple fallback strategies.

        Args:
            text: Text containing JSON response from LLM.
            max_candidates: Maximum number of JSON candidates to try.

        Returns:
            Tuple of (parsed_json, error_message). Returns None, error_msg if all parsing fails.
        """
        if not text or not text.strip():
            logger.debug("JSON parsing failed: Empty response text")
            return None, "Empty response text"

        # Clean the response
        cleaned_text = self.clean_llm_response(text)
        if not cleaned_text:
            logger.debug("JSON parsing failed: Response became empty after cleaning")
            return None, "Response became empty after cleaning"

        # Try parsing the cleaned text directly first
        parsed, error = self.parse_json_safe(cleaned_text)
        if parsed is not None:
            logger.debug("JSON parsing succeeded with direct parsing")
            return parsed, None

        # Extract JSON candidates from the cleaned text
        candidates = self.extract_json_from_text(cleaned_text)

        # Limit candidates to avoid excessive processing
        candidates = candidates[:max_candidates]
        logger.debug(f"Extracted {len(candidates)} JSON candidates from response")

        # Try each candidate
        for i, candidate in enumerate(candidates):
            logger.debug(f"Trying candidate {i + 1}: {candidate[:100]}...")
            # Try the candidate as-is
            parsed, error = self.parse_json_safe(candidate)
            if parsed is not None:
                logger.debug(f"JSON parsing succeeded with candidate {i + 2}")
                return parsed, None

            # Try to fix common issues
            fixed_candidates = self.try_fix_common_json_issues(candidate)
            for j, fixed in enumerate(fixed_candidates):
                if fixed != candidate:  # Only try if different
                    logger.debug(
                        f"Trying fixed candidate {i + 1}.{j + 1}: {fixed[:100]}..."
                    )
                    parsed, error = self.parse_json_safe(fixed)
                    if parsed is not None:
                        logger.debug(
                            f"JSON parsing succeeded with fixed candidate {i + 1}.{j + 1}"
                        )
                        return parsed, None

        # If all parsing failed, return the best error message
        error_msg = f"Failed to extract valid JSON from response. Tried {len(candidates)} candidates."
        logger.warning(
            f"JSON parsing failed: {error_msg}. Original text: {text[:200]}..."
        )
        return None, error_msg

    def xǁRobustJSONParserǁextract_and_parse_json__mutmut_44(
        self, text: str, max_candidates: int = 5
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Extract and parse JSON from LLM response with multiple fallback strategies.

        Args:
            text: Text containing JSON response from LLM.
            max_candidates: Maximum number of JSON candidates to try.

        Returns:
            Tuple of (parsed_json, error_message). Returns None, error_msg if all parsing fails.
        """
        if not text or not text.strip():
            logger.debug("JSON parsing failed: Empty response text")
            return None, "Empty response text"

        # Clean the response
        cleaned_text = self.clean_llm_response(text)
        if not cleaned_text:
            logger.debug("JSON parsing failed: Response became empty after cleaning")
            return None, "Response became empty after cleaning"

        # Try parsing the cleaned text directly first
        parsed, error = self.parse_json_safe(cleaned_text)
        if parsed is not None:
            logger.debug("JSON parsing succeeded with direct parsing")
            return parsed, None

        # Extract JSON candidates from the cleaned text
        candidates = self.extract_json_from_text(cleaned_text)

        # Limit candidates to avoid excessive processing
        candidates = candidates[:max_candidates]
        logger.debug(f"Extracted {len(candidates)} JSON candidates from response")

        # Try each candidate
        for i, candidate in enumerate(candidates):
            logger.debug(f"Trying candidate {i + 1}: {candidate[:100]}...")
            # Try the candidate as-is
            parsed, error = self.parse_json_safe(candidate)
            if parsed is not None:
                logger.debug(f"JSON parsing succeeded with candidate {i + 1}")
                return parsed, None

            # Try to fix common issues
            fixed_candidates = None
            for j, fixed in enumerate(fixed_candidates):
                if fixed != candidate:  # Only try if different
                    logger.debug(
                        f"Trying fixed candidate {i + 1}.{j + 1}: {fixed[:100]}..."
                    )
                    parsed, error = self.parse_json_safe(fixed)
                    if parsed is not None:
                        logger.debug(
                            f"JSON parsing succeeded with fixed candidate {i + 1}.{j + 1}"
                        )
                        return parsed, None

        # If all parsing failed, return the best error message
        error_msg = f"Failed to extract valid JSON from response. Tried {len(candidates)} candidates."
        logger.warning(
            f"JSON parsing failed: {error_msg}. Original text: {text[:200]}..."
        )
        return None, error_msg

    def xǁRobustJSONParserǁextract_and_parse_json__mutmut_45(
        self, text: str, max_candidates: int = 5
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Extract and parse JSON from LLM response with multiple fallback strategies.

        Args:
            text: Text containing JSON response from LLM.
            max_candidates: Maximum number of JSON candidates to try.

        Returns:
            Tuple of (parsed_json, error_message). Returns None, error_msg if all parsing fails.
        """
        if not text or not text.strip():
            logger.debug("JSON parsing failed: Empty response text")
            return None, "Empty response text"

        # Clean the response
        cleaned_text = self.clean_llm_response(text)
        if not cleaned_text:
            logger.debug("JSON parsing failed: Response became empty after cleaning")
            return None, "Response became empty after cleaning"

        # Try parsing the cleaned text directly first
        parsed, error = self.parse_json_safe(cleaned_text)
        if parsed is not None:
            logger.debug("JSON parsing succeeded with direct parsing")
            return parsed, None

        # Extract JSON candidates from the cleaned text
        candidates = self.extract_json_from_text(cleaned_text)

        # Limit candidates to avoid excessive processing
        candidates = candidates[:max_candidates]
        logger.debug(f"Extracted {len(candidates)} JSON candidates from response")

        # Try each candidate
        for i, candidate in enumerate(candidates):
            logger.debug(f"Trying candidate {i + 1}: {candidate[:100]}...")
            # Try the candidate as-is
            parsed, error = self.parse_json_safe(candidate)
            if parsed is not None:
                logger.debug(f"JSON parsing succeeded with candidate {i + 1}")
                return parsed, None

            # Try to fix common issues
            fixed_candidates = self.try_fix_common_json_issues(None)
            for j, fixed in enumerate(fixed_candidates):
                if fixed != candidate:  # Only try if different
                    logger.debug(
                        f"Trying fixed candidate {i + 1}.{j + 1}: {fixed[:100]}..."
                    )
                    parsed, error = self.parse_json_safe(fixed)
                    if parsed is not None:
                        logger.debug(
                            f"JSON parsing succeeded with fixed candidate {i + 1}.{j + 1}"
                        )
                        return parsed, None

        # If all parsing failed, return the best error message
        error_msg = f"Failed to extract valid JSON from response. Tried {len(candidates)} candidates."
        logger.warning(
            f"JSON parsing failed: {error_msg}. Original text: {text[:200]}..."
        )
        return None, error_msg

    def xǁRobustJSONParserǁextract_and_parse_json__mutmut_46(
        self, text: str, max_candidates: int = 5
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Extract and parse JSON from LLM response with multiple fallback strategies.

        Args:
            text: Text containing JSON response from LLM.
            max_candidates: Maximum number of JSON candidates to try.

        Returns:
            Tuple of (parsed_json, error_message). Returns None, error_msg if all parsing fails.
        """
        if not text or not text.strip():
            logger.debug("JSON parsing failed: Empty response text")
            return None, "Empty response text"

        # Clean the response
        cleaned_text = self.clean_llm_response(text)
        if not cleaned_text:
            logger.debug("JSON parsing failed: Response became empty after cleaning")
            return None, "Response became empty after cleaning"

        # Try parsing the cleaned text directly first
        parsed, error = self.parse_json_safe(cleaned_text)
        if parsed is not None:
            logger.debug("JSON parsing succeeded with direct parsing")
            return parsed, None

        # Extract JSON candidates from the cleaned text
        candidates = self.extract_json_from_text(cleaned_text)

        # Limit candidates to avoid excessive processing
        candidates = candidates[:max_candidates]
        logger.debug(f"Extracted {len(candidates)} JSON candidates from response")

        # Try each candidate
        for i, candidate in enumerate(candidates):
            logger.debug(f"Trying candidate {i + 1}: {candidate[:100]}...")
            # Try the candidate as-is
            parsed, error = self.parse_json_safe(candidate)
            if parsed is not None:
                logger.debug(f"JSON parsing succeeded with candidate {i + 1}")
                return parsed, None

            # Try to fix common issues
            self.try_fix_common_json_issues(candidate)
            for j, fixed in enumerate(None):
                if fixed != candidate:  # Only try if different
                    logger.debug(
                        f"Trying fixed candidate {i + 1}.{j + 1}: {fixed[:100]}..."
                    )
                    parsed, error = self.parse_json_safe(fixed)
                    if parsed is not None:
                        logger.debug(
                            f"JSON parsing succeeded with fixed candidate {i + 1}.{j + 1}"
                        )
                        return parsed, None

        # If all parsing failed, return the best error message
        error_msg = f"Failed to extract valid JSON from response. Tried {len(candidates)} candidates."
        logger.warning(
            f"JSON parsing failed: {error_msg}. Original text: {text[:200]}..."
        )
        return None, error_msg

    def xǁRobustJSONParserǁextract_and_parse_json__mutmut_47(
        self, text: str, max_candidates: int = 5
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Extract and parse JSON from LLM response with multiple fallback strategies.

        Args:
            text: Text containing JSON response from LLM.
            max_candidates: Maximum number of JSON candidates to try.

        Returns:
            Tuple of (parsed_json, error_message). Returns None, error_msg if all parsing fails.
        """
        if not text or not text.strip():
            logger.debug("JSON parsing failed: Empty response text")
            return None, "Empty response text"

        # Clean the response
        cleaned_text = self.clean_llm_response(text)
        if not cleaned_text:
            logger.debug("JSON parsing failed: Response became empty after cleaning")
            return None, "Response became empty after cleaning"

        # Try parsing the cleaned text directly first
        parsed, error = self.parse_json_safe(cleaned_text)
        if parsed is not None:
            logger.debug("JSON parsing succeeded with direct parsing")
            return parsed, None

        # Extract JSON candidates from the cleaned text
        candidates = self.extract_json_from_text(cleaned_text)

        # Limit candidates to avoid excessive processing
        candidates = candidates[:max_candidates]
        logger.debug(f"Extracted {len(candidates)} JSON candidates from response")

        # Try each candidate
        for i, candidate in enumerate(candidates):
            logger.debug(f"Trying candidate {i + 1}: {candidate[:100]}...")
            # Try the candidate as-is
            parsed, error = self.parse_json_safe(candidate)
            if parsed is not None:
                logger.debug(f"JSON parsing succeeded with candidate {i + 1}")
                return parsed, None

            # Try to fix common issues
            fixed_candidates = self.try_fix_common_json_issues(candidate)
            for j, fixed in enumerate(fixed_candidates):
                if fixed == candidate:  # Only try if different
                    logger.debug(
                        f"Trying fixed candidate {i + 1}.{j + 1}: {fixed[:100]}..."
                    )
                    parsed, error = self.parse_json_safe(fixed)
                    if parsed is not None:
                        logger.debug(
                            f"JSON parsing succeeded with fixed candidate {i + 1}.{j + 1}"
                        )
                        return parsed, None

        # If all parsing failed, return the best error message
        error_msg = f"Failed to extract valid JSON from response. Tried {len(candidates)} candidates."
        logger.warning(
            f"JSON parsing failed: {error_msg}. Original text: {text[:200]}..."
        )
        return None, error_msg

    def xǁRobustJSONParserǁextract_and_parse_json__mutmut_48(
        self, text: str, max_candidates: int = 5
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Extract and parse JSON from LLM response with multiple fallback strategies.

        Args:
            text: Text containing JSON response from LLM.
            max_candidates: Maximum number of JSON candidates to try.

        Returns:
            Tuple of (parsed_json, error_message). Returns None, error_msg if all parsing fails.
        """
        if not text or not text.strip():
            logger.debug("JSON parsing failed: Empty response text")
            return None, "Empty response text"

        # Clean the response
        cleaned_text = self.clean_llm_response(text)
        if not cleaned_text:
            logger.debug("JSON parsing failed: Response became empty after cleaning")
            return None, "Response became empty after cleaning"

        # Try parsing the cleaned text directly first
        parsed, error = self.parse_json_safe(cleaned_text)
        if parsed is not None:
            logger.debug("JSON parsing succeeded with direct parsing")
            return parsed, None

        # Extract JSON candidates from the cleaned text
        candidates = self.extract_json_from_text(cleaned_text)

        # Limit candidates to avoid excessive processing
        candidates = candidates[:max_candidates]
        logger.debug(f"Extracted {len(candidates)} JSON candidates from response")

        # Try each candidate
        for i, candidate in enumerate(candidates):
            logger.debug(f"Trying candidate {i + 1}: {candidate[:100]}...")
            # Try the candidate as-is
            parsed, error = self.parse_json_safe(candidate)
            if parsed is not None:
                logger.debug(f"JSON parsing succeeded with candidate {i + 1}")
                return parsed, None

            # Try to fix common issues
            fixed_candidates = self.try_fix_common_json_issues(candidate)
            for j, fixed in enumerate(fixed_candidates):
                if fixed != candidate:  # Only try if different
                    logger.debug(None)
                    parsed, error = self.parse_json_safe(fixed)
                    if parsed is not None:
                        logger.debug(
                            f"JSON parsing succeeded with fixed candidate {i + 1}.{j + 1}"
                        )
                        return parsed, None

        # If all parsing failed, return the best error message
        error_msg = f"Failed to extract valid JSON from response. Tried {len(candidates)} candidates."
        logger.warning(
            f"JSON parsing failed: {error_msg}. Original text: {text[:200]}..."
        )
        return None, error_msg

    def xǁRobustJSONParserǁextract_and_parse_json__mutmut_49(
        self, text: str, max_candidates: int = 5
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Extract and parse JSON from LLM response with multiple fallback strategies.

        Args:
            text: Text containing JSON response from LLM.
            max_candidates: Maximum number of JSON candidates to try.

        Returns:
            Tuple of (parsed_json, error_message). Returns None, error_msg if all parsing fails.
        """
        if not text or not text.strip():
            logger.debug("JSON parsing failed: Empty response text")
            return None, "Empty response text"

        # Clean the response
        cleaned_text = self.clean_llm_response(text)
        if not cleaned_text:
            logger.debug("JSON parsing failed: Response became empty after cleaning")
            return None, "Response became empty after cleaning"

        # Try parsing the cleaned text directly first
        parsed, error = self.parse_json_safe(cleaned_text)
        if parsed is not None:
            logger.debug("JSON parsing succeeded with direct parsing")
            return parsed, None

        # Extract JSON candidates from the cleaned text
        candidates = self.extract_json_from_text(cleaned_text)

        # Limit candidates to avoid excessive processing
        candidates = candidates[:max_candidates]
        logger.debug(f"Extracted {len(candidates)} JSON candidates from response")

        # Try each candidate
        for i, candidate in enumerate(candidates):
            logger.debug(f"Trying candidate {i + 1}: {candidate[:100]}...")
            # Try the candidate as-is
            parsed, error = self.parse_json_safe(candidate)
            if parsed is not None:
                logger.debug(f"JSON parsing succeeded with candidate {i + 1}")
                return parsed, None

            # Try to fix common issues
            fixed_candidates = self.try_fix_common_json_issues(candidate)
            for j, fixed in enumerate(fixed_candidates):
                if fixed != candidate:  # Only try if different
                    logger.debug(
                        f"Trying fixed candidate {i - 1}.{j + 1}: {fixed[:100]}..."
                    )
                    parsed, error = self.parse_json_safe(fixed)
                    if parsed is not None:
                        logger.debug(
                            f"JSON parsing succeeded with fixed candidate {i + 1}.{j + 1}"
                        )
                        return parsed, None

        # If all parsing failed, return the best error message
        error_msg = f"Failed to extract valid JSON from response. Tried {len(candidates)} candidates."
        logger.warning(
            f"JSON parsing failed: {error_msg}. Original text: {text[:200]}..."
        )
        return None, error_msg

    def xǁRobustJSONParserǁextract_and_parse_json__mutmut_50(
        self, text: str, max_candidates: int = 5
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Extract and parse JSON from LLM response with multiple fallback strategies.

        Args:
            text: Text containing JSON response from LLM.
            max_candidates: Maximum number of JSON candidates to try.

        Returns:
            Tuple of (parsed_json, error_message). Returns None, error_msg if all parsing fails.
        """
        if not text or not text.strip():
            logger.debug("JSON parsing failed: Empty response text")
            return None, "Empty response text"

        # Clean the response
        cleaned_text = self.clean_llm_response(text)
        if not cleaned_text:
            logger.debug("JSON parsing failed: Response became empty after cleaning")
            return None, "Response became empty after cleaning"

        # Try parsing the cleaned text directly first
        parsed, error = self.parse_json_safe(cleaned_text)
        if parsed is not None:
            logger.debug("JSON parsing succeeded with direct parsing")
            return parsed, None

        # Extract JSON candidates from the cleaned text
        candidates = self.extract_json_from_text(cleaned_text)

        # Limit candidates to avoid excessive processing
        candidates = candidates[:max_candidates]
        logger.debug(f"Extracted {len(candidates)} JSON candidates from response")

        # Try each candidate
        for i, candidate in enumerate(candidates):
            logger.debug(f"Trying candidate {i + 1}: {candidate[:100]}...")
            # Try the candidate as-is
            parsed, error = self.parse_json_safe(candidate)
            if parsed is not None:
                logger.debug(f"JSON parsing succeeded with candidate {i + 1}")
                return parsed, None

            # Try to fix common issues
            fixed_candidates = self.try_fix_common_json_issues(candidate)
            for j, fixed in enumerate(fixed_candidates):
                if fixed != candidate:  # Only try if different
                    logger.debug(
                        f"Trying fixed candidate {i + 2}.{j + 1}: {fixed[:100]}..."
                    )
                    parsed, error = self.parse_json_safe(fixed)
                    if parsed is not None:
                        logger.debug(
                            f"JSON parsing succeeded with fixed candidate {i + 1}.{j + 1}"
                        )
                        return parsed, None

        # If all parsing failed, return the best error message
        error_msg = f"Failed to extract valid JSON from response. Tried {len(candidates)} candidates."
        logger.warning(
            f"JSON parsing failed: {error_msg}. Original text: {text[:200]}..."
        )
        return None, error_msg

    def xǁRobustJSONParserǁextract_and_parse_json__mutmut_51(
        self, text: str, max_candidates: int = 5
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Extract and parse JSON from LLM response with multiple fallback strategies.

        Args:
            text: Text containing JSON response from LLM.
            max_candidates: Maximum number of JSON candidates to try.

        Returns:
            Tuple of (parsed_json, error_message). Returns None, error_msg if all parsing fails.
        """
        if not text or not text.strip():
            logger.debug("JSON parsing failed: Empty response text")
            return None, "Empty response text"

        # Clean the response
        cleaned_text = self.clean_llm_response(text)
        if not cleaned_text:
            logger.debug("JSON parsing failed: Response became empty after cleaning")
            return None, "Response became empty after cleaning"

        # Try parsing the cleaned text directly first
        parsed, error = self.parse_json_safe(cleaned_text)
        if parsed is not None:
            logger.debug("JSON parsing succeeded with direct parsing")
            return parsed, None

        # Extract JSON candidates from the cleaned text
        candidates = self.extract_json_from_text(cleaned_text)

        # Limit candidates to avoid excessive processing
        candidates = candidates[:max_candidates]
        logger.debug(f"Extracted {len(candidates)} JSON candidates from response")

        # Try each candidate
        for i, candidate in enumerate(candidates):
            logger.debug(f"Trying candidate {i + 1}: {candidate[:100]}...")
            # Try the candidate as-is
            parsed, error = self.parse_json_safe(candidate)
            if parsed is not None:
                logger.debug(f"JSON parsing succeeded with candidate {i + 1}")
                return parsed, None

            # Try to fix common issues
            fixed_candidates = self.try_fix_common_json_issues(candidate)
            for j, fixed in enumerate(fixed_candidates):
                if fixed != candidate:  # Only try if different
                    logger.debug(
                        f"Trying fixed candidate {i + 1}.{j - 1}: {fixed[:100]}..."
                    )
                    parsed, error = self.parse_json_safe(fixed)
                    if parsed is not None:
                        logger.debug(
                            f"JSON parsing succeeded with fixed candidate {i + 1}.{j + 1}"
                        )
                        return parsed, None

        # If all parsing failed, return the best error message
        error_msg = f"Failed to extract valid JSON from response. Tried {len(candidates)} candidates."
        logger.warning(
            f"JSON parsing failed: {error_msg}. Original text: {text[:200]}..."
        )
        return None, error_msg

    def xǁRobustJSONParserǁextract_and_parse_json__mutmut_52(
        self, text: str, max_candidates: int = 5
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Extract and parse JSON from LLM response with multiple fallback strategies.

        Args:
            text: Text containing JSON response from LLM.
            max_candidates: Maximum number of JSON candidates to try.

        Returns:
            Tuple of (parsed_json, error_message). Returns None, error_msg if all parsing fails.
        """
        if not text or not text.strip():
            logger.debug("JSON parsing failed: Empty response text")
            return None, "Empty response text"

        # Clean the response
        cleaned_text = self.clean_llm_response(text)
        if not cleaned_text:
            logger.debug("JSON parsing failed: Response became empty after cleaning")
            return None, "Response became empty after cleaning"

        # Try parsing the cleaned text directly first
        parsed, error = self.parse_json_safe(cleaned_text)
        if parsed is not None:
            logger.debug("JSON parsing succeeded with direct parsing")
            return parsed, None

        # Extract JSON candidates from the cleaned text
        candidates = self.extract_json_from_text(cleaned_text)

        # Limit candidates to avoid excessive processing
        candidates = candidates[:max_candidates]
        logger.debug(f"Extracted {len(candidates)} JSON candidates from response")

        # Try each candidate
        for i, candidate in enumerate(candidates):
            logger.debug(f"Trying candidate {i + 1}: {candidate[:100]}...")
            # Try the candidate as-is
            parsed, error = self.parse_json_safe(candidate)
            if parsed is not None:
                logger.debug(f"JSON parsing succeeded with candidate {i + 1}")
                return parsed, None

            # Try to fix common issues
            fixed_candidates = self.try_fix_common_json_issues(candidate)
            for j, fixed in enumerate(fixed_candidates):
                if fixed != candidate:  # Only try if different
                    logger.debug(
                        f"Trying fixed candidate {i + 1}.{j + 2}: {fixed[:100]}..."
                    )
                    parsed, error = self.parse_json_safe(fixed)
                    if parsed is not None:
                        logger.debug(
                            f"JSON parsing succeeded with fixed candidate {i + 1}.{j + 1}"
                        )
                        return parsed, None

        # If all parsing failed, return the best error message
        error_msg = f"Failed to extract valid JSON from response. Tried {len(candidates)} candidates."
        logger.warning(
            f"JSON parsing failed: {error_msg}. Original text: {text[:200]}..."
        )
        return None, error_msg

    def xǁRobustJSONParserǁextract_and_parse_json__mutmut_53(
        self, text: str, max_candidates: int = 5
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Extract and parse JSON from LLM response with multiple fallback strategies.

        Args:
            text: Text containing JSON response from LLM.
            max_candidates: Maximum number of JSON candidates to try.

        Returns:
            Tuple of (parsed_json, error_message). Returns None, error_msg if all parsing fails.
        """
        if not text or not text.strip():
            logger.debug("JSON parsing failed: Empty response text")
            return None, "Empty response text"

        # Clean the response
        cleaned_text = self.clean_llm_response(text)
        if not cleaned_text:
            logger.debug("JSON parsing failed: Response became empty after cleaning")
            return None, "Response became empty after cleaning"

        # Try parsing the cleaned text directly first
        parsed, error = self.parse_json_safe(cleaned_text)
        if parsed is not None:
            logger.debug("JSON parsing succeeded with direct parsing")
            return parsed, None

        # Extract JSON candidates from the cleaned text
        candidates = self.extract_json_from_text(cleaned_text)

        # Limit candidates to avoid excessive processing
        candidates = candidates[:max_candidates]
        logger.debug(f"Extracted {len(candidates)} JSON candidates from response")

        # Try each candidate
        for i, candidate in enumerate(candidates):
            logger.debug(f"Trying candidate {i + 1}: {candidate[:100]}...")
            # Try the candidate as-is
            parsed, error = self.parse_json_safe(candidate)
            if parsed is not None:
                logger.debug(f"JSON parsing succeeded with candidate {i + 1}")
                return parsed, None

            # Try to fix common issues
            fixed_candidates = self.try_fix_common_json_issues(candidate)
            for j, fixed in enumerate(fixed_candidates):
                if fixed != candidate:  # Only try if different
                    logger.debug(
                        f"Trying fixed candidate {i + 1}.{j + 1}: {fixed[:101]}..."
                    )
                    parsed, error = self.parse_json_safe(fixed)
                    if parsed is not None:
                        logger.debug(
                            f"JSON parsing succeeded with fixed candidate {i + 1}.{j + 1}"
                        )
                        return parsed, None

        # If all parsing failed, return the best error message
        error_msg = f"Failed to extract valid JSON from response. Tried {len(candidates)} candidates."
        logger.warning(
            f"JSON parsing failed: {error_msg}. Original text: {text[:200]}..."
        )
        return None, error_msg

    def xǁRobustJSONParserǁextract_and_parse_json__mutmut_54(
        self, text: str, max_candidates: int = 5
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Extract and parse JSON from LLM response with multiple fallback strategies.

        Args:
            text: Text containing JSON response from LLM.
            max_candidates: Maximum number of JSON candidates to try.

        Returns:
            Tuple of (parsed_json, error_message). Returns None, error_msg if all parsing fails.
        """
        if not text or not text.strip():
            logger.debug("JSON parsing failed: Empty response text")
            return None, "Empty response text"

        # Clean the response
        cleaned_text = self.clean_llm_response(text)
        if not cleaned_text:
            logger.debug("JSON parsing failed: Response became empty after cleaning")
            return None, "Response became empty after cleaning"

        # Try parsing the cleaned text directly first
        parsed, error = self.parse_json_safe(cleaned_text)
        if parsed is not None:
            logger.debug("JSON parsing succeeded with direct parsing")
            return parsed, None

        # Extract JSON candidates from the cleaned text
        candidates = self.extract_json_from_text(cleaned_text)

        # Limit candidates to avoid excessive processing
        candidates = candidates[:max_candidates]
        logger.debug(f"Extracted {len(candidates)} JSON candidates from response")

        # Try each candidate
        for i, candidate in enumerate(candidates):
            logger.debug(f"Trying candidate {i + 1}: {candidate[:100]}...")
            # Try the candidate as-is
            parsed, error = self.parse_json_safe(candidate)
            if parsed is not None:
                logger.debug(f"JSON parsing succeeded with candidate {i + 1}")
                return parsed, None

            # Try to fix common issues
            fixed_candidates = self.try_fix_common_json_issues(candidate)
            for j, fixed in enumerate(fixed_candidates):
                if fixed != candidate:  # Only try if different
                    logger.debug(
                        f"Trying fixed candidate {i + 1}.{j + 1}: {fixed[:100]}..."
                    )
                    parsed, error = None
                    if parsed is not None:
                        logger.debug(
                            f"JSON parsing succeeded with fixed candidate {i + 1}.{j + 1}"
                        )
                        return parsed, None

        # If all parsing failed, return the best error message
        error_msg = f"Failed to extract valid JSON from response. Tried {len(candidates)} candidates."
        logger.warning(
            f"JSON parsing failed: {error_msg}. Original text: {text[:200]}..."
        )
        return None, error_msg

    def xǁRobustJSONParserǁextract_and_parse_json__mutmut_55(
        self, text: str, max_candidates: int = 5
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Extract and parse JSON from LLM response with multiple fallback strategies.

        Args:
            text: Text containing JSON response from LLM.
            max_candidates: Maximum number of JSON candidates to try.

        Returns:
            Tuple of (parsed_json, error_message). Returns None, error_msg if all parsing fails.
        """
        if not text or not text.strip():
            logger.debug("JSON parsing failed: Empty response text")
            return None, "Empty response text"

        # Clean the response
        cleaned_text = self.clean_llm_response(text)
        if not cleaned_text:
            logger.debug("JSON parsing failed: Response became empty after cleaning")
            return None, "Response became empty after cleaning"

        # Try parsing the cleaned text directly first
        parsed, error = self.parse_json_safe(cleaned_text)
        if parsed is not None:
            logger.debug("JSON parsing succeeded with direct parsing")
            return parsed, None

        # Extract JSON candidates from the cleaned text
        candidates = self.extract_json_from_text(cleaned_text)

        # Limit candidates to avoid excessive processing
        candidates = candidates[:max_candidates]
        logger.debug(f"Extracted {len(candidates)} JSON candidates from response")

        # Try each candidate
        for i, candidate in enumerate(candidates):
            logger.debug(f"Trying candidate {i + 1}: {candidate[:100]}...")
            # Try the candidate as-is
            parsed, error = self.parse_json_safe(candidate)
            if parsed is not None:
                logger.debug(f"JSON parsing succeeded with candidate {i + 1}")
                return parsed, None

            # Try to fix common issues
            fixed_candidates = self.try_fix_common_json_issues(candidate)
            for j, fixed in enumerate(fixed_candidates):
                if fixed != candidate:  # Only try if different
                    logger.debug(
                        f"Trying fixed candidate {i + 1}.{j + 1}: {fixed[:100]}..."
                    )
                    parsed, error = self.parse_json_safe(None)
                    if parsed is not None:
                        logger.debug(
                            f"JSON parsing succeeded with fixed candidate {i + 1}.{j + 1}"
                        )
                        return parsed, None

        # If all parsing failed, return the best error message
        error_msg = f"Failed to extract valid JSON from response. Tried {len(candidates)} candidates."
        logger.warning(
            f"JSON parsing failed: {error_msg}. Original text: {text[:200]}..."
        )
        return None, error_msg

    def xǁRobustJSONParserǁextract_and_parse_json__mutmut_56(
        self, text: str, max_candidates: int = 5
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Extract and parse JSON from LLM response with multiple fallback strategies.

        Args:
            text: Text containing JSON response from LLM.
            max_candidates: Maximum number of JSON candidates to try.

        Returns:
            Tuple of (parsed_json, error_message). Returns None, error_msg if all parsing fails.
        """
        if not text or not text.strip():
            logger.debug("JSON parsing failed: Empty response text")
            return None, "Empty response text"

        # Clean the response
        cleaned_text = self.clean_llm_response(text)
        if not cleaned_text:
            logger.debug("JSON parsing failed: Response became empty after cleaning")
            return None, "Response became empty after cleaning"

        # Try parsing the cleaned text directly first
        parsed, error = self.parse_json_safe(cleaned_text)
        if parsed is not None:
            logger.debug("JSON parsing succeeded with direct parsing")
            return parsed, None

        # Extract JSON candidates from the cleaned text
        candidates = self.extract_json_from_text(cleaned_text)

        # Limit candidates to avoid excessive processing
        candidates = candidates[:max_candidates]
        logger.debug(f"Extracted {len(candidates)} JSON candidates from response")

        # Try each candidate
        for i, candidate in enumerate(candidates):
            logger.debug(f"Trying candidate {i + 1}: {candidate[:100]}...")
            # Try the candidate as-is
            parsed, error = self.parse_json_safe(candidate)
            if parsed is not None:
                logger.debug(f"JSON parsing succeeded with candidate {i + 1}")
                return parsed, None

            # Try to fix common issues
            fixed_candidates = self.try_fix_common_json_issues(candidate)
            for j, fixed in enumerate(fixed_candidates):
                if fixed != candidate:  # Only try if different
                    logger.debug(
                        f"Trying fixed candidate {i + 1}.{j + 1}: {fixed[:100]}..."
                    )
                    parsed, error = self.parse_json_safe(fixed)
                    if parsed is None:
                        logger.debug(
                            f"JSON parsing succeeded with fixed candidate {i + 1}.{j + 1}"
                        )
                        return parsed, None

        # If all parsing failed, return the best error message
        error_msg = f"Failed to extract valid JSON from response. Tried {len(candidates)} candidates."
        logger.warning(
            f"JSON parsing failed: {error_msg}. Original text: {text[:200]}..."
        )
        return None, error_msg

    def xǁRobustJSONParserǁextract_and_parse_json__mutmut_57(
        self, text: str, max_candidates: int = 5
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Extract and parse JSON from LLM response with multiple fallback strategies.

        Args:
            text: Text containing JSON response from LLM.
            max_candidates: Maximum number of JSON candidates to try.

        Returns:
            Tuple of (parsed_json, error_message). Returns None, error_msg if all parsing fails.
        """
        if not text or not text.strip():
            logger.debug("JSON parsing failed: Empty response text")
            return None, "Empty response text"

        # Clean the response
        cleaned_text = self.clean_llm_response(text)
        if not cleaned_text:
            logger.debug("JSON parsing failed: Response became empty after cleaning")
            return None, "Response became empty after cleaning"

        # Try parsing the cleaned text directly first
        parsed, error = self.parse_json_safe(cleaned_text)
        if parsed is not None:
            logger.debug("JSON parsing succeeded with direct parsing")
            return parsed, None

        # Extract JSON candidates from the cleaned text
        candidates = self.extract_json_from_text(cleaned_text)

        # Limit candidates to avoid excessive processing
        candidates = candidates[:max_candidates]
        logger.debug(f"Extracted {len(candidates)} JSON candidates from response")

        # Try each candidate
        for i, candidate in enumerate(candidates):
            logger.debug(f"Trying candidate {i + 1}: {candidate[:100]}...")
            # Try the candidate as-is
            parsed, error = self.parse_json_safe(candidate)
            if parsed is not None:
                logger.debug(f"JSON parsing succeeded with candidate {i + 1}")
                return parsed, None

            # Try to fix common issues
            fixed_candidates = self.try_fix_common_json_issues(candidate)
            for j, fixed in enumerate(fixed_candidates):
                if fixed != candidate:  # Only try if different
                    logger.debug(
                        f"Trying fixed candidate {i + 1}.{j + 1}: {fixed[:100]}..."
                    )
                    parsed, error = self.parse_json_safe(fixed)
                    if parsed is not None:
                        logger.debug(None)
                        return parsed, None

        # If all parsing failed, return the best error message
        error_msg = f"Failed to extract valid JSON from response. Tried {len(candidates)} candidates."
        logger.warning(
            f"JSON parsing failed: {error_msg}. Original text: {text[:200]}..."
        )
        return None, error_msg

    def xǁRobustJSONParserǁextract_and_parse_json__mutmut_58(
        self, text: str, max_candidates: int = 5
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Extract and parse JSON from LLM response with multiple fallback strategies.

        Args:
            text: Text containing JSON response from LLM.
            max_candidates: Maximum number of JSON candidates to try.

        Returns:
            Tuple of (parsed_json, error_message). Returns None, error_msg if all parsing fails.
        """
        if not text or not text.strip():
            logger.debug("JSON parsing failed: Empty response text")
            return None, "Empty response text"

        # Clean the response
        cleaned_text = self.clean_llm_response(text)
        if not cleaned_text:
            logger.debug("JSON parsing failed: Response became empty after cleaning")
            return None, "Response became empty after cleaning"

        # Try parsing the cleaned text directly first
        parsed, error = self.parse_json_safe(cleaned_text)
        if parsed is not None:
            logger.debug("JSON parsing succeeded with direct parsing")
            return parsed, None

        # Extract JSON candidates from the cleaned text
        candidates = self.extract_json_from_text(cleaned_text)

        # Limit candidates to avoid excessive processing
        candidates = candidates[:max_candidates]
        logger.debug(f"Extracted {len(candidates)} JSON candidates from response")

        # Try each candidate
        for i, candidate in enumerate(candidates):
            logger.debug(f"Trying candidate {i + 1}: {candidate[:100]}...")
            # Try the candidate as-is
            parsed, error = self.parse_json_safe(candidate)
            if parsed is not None:
                logger.debug(f"JSON parsing succeeded with candidate {i + 1}")
                return parsed, None

            # Try to fix common issues
            fixed_candidates = self.try_fix_common_json_issues(candidate)
            for j, fixed in enumerate(fixed_candidates):
                if fixed != candidate:  # Only try if different
                    logger.debug(
                        f"Trying fixed candidate {i + 1}.{j + 1}: {fixed[:100]}..."
                    )
                    parsed, error = self.parse_json_safe(fixed)
                    if parsed is not None:
                        logger.debug(
                            f"JSON parsing succeeded with fixed candidate {i - 1}.{j + 1}"
                        )
                        return parsed, None

        # If all parsing failed, return the best error message
        error_msg = f"Failed to extract valid JSON from response. Tried {len(candidates)} candidates."
        logger.warning(
            f"JSON parsing failed: {error_msg}. Original text: {text[:200]}..."
        )
        return None, error_msg

    def xǁRobustJSONParserǁextract_and_parse_json__mutmut_59(
        self, text: str, max_candidates: int = 5
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Extract and parse JSON from LLM response with multiple fallback strategies.

        Args:
            text: Text containing JSON response from LLM.
            max_candidates: Maximum number of JSON candidates to try.

        Returns:
            Tuple of (parsed_json, error_message). Returns None, error_msg if all parsing fails.
        """
        if not text or not text.strip():
            logger.debug("JSON parsing failed: Empty response text")
            return None, "Empty response text"

        # Clean the response
        cleaned_text = self.clean_llm_response(text)
        if not cleaned_text:
            logger.debug("JSON parsing failed: Response became empty after cleaning")
            return None, "Response became empty after cleaning"

        # Try parsing the cleaned text directly first
        parsed, error = self.parse_json_safe(cleaned_text)
        if parsed is not None:
            logger.debug("JSON parsing succeeded with direct parsing")
            return parsed, None

        # Extract JSON candidates from the cleaned text
        candidates = self.extract_json_from_text(cleaned_text)

        # Limit candidates to avoid excessive processing
        candidates = candidates[:max_candidates]
        logger.debug(f"Extracted {len(candidates)} JSON candidates from response")

        # Try each candidate
        for i, candidate in enumerate(candidates):
            logger.debug(f"Trying candidate {i + 1}: {candidate[:100]}...")
            # Try the candidate as-is
            parsed, error = self.parse_json_safe(candidate)
            if parsed is not None:
                logger.debug(f"JSON parsing succeeded with candidate {i + 1}")
                return parsed, None

            # Try to fix common issues
            fixed_candidates = self.try_fix_common_json_issues(candidate)
            for j, fixed in enumerate(fixed_candidates):
                if fixed != candidate:  # Only try if different
                    logger.debug(
                        f"Trying fixed candidate {i + 1}.{j + 1}: {fixed[:100]}..."
                    )
                    parsed, error = self.parse_json_safe(fixed)
                    if parsed is not None:
                        logger.debug(
                            f"JSON parsing succeeded with fixed candidate {i + 2}.{j + 1}"
                        )
                        return parsed, None

        # If all parsing failed, return the best error message
        error_msg = f"Failed to extract valid JSON from response. Tried {len(candidates)} candidates."
        logger.warning(
            f"JSON parsing failed: {error_msg}. Original text: {text[:200]}..."
        )
        return None, error_msg

    def xǁRobustJSONParserǁextract_and_parse_json__mutmut_60(
        self, text: str, max_candidates: int = 5
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Extract and parse JSON from LLM response with multiple fallback strategies.

        Args:
            text: Text containing JSON response from LLM.
            max_candidates: Maximum number of JSON candidates to try.

        Returns:
            Tuple of (parsed_json, error_message). Returns None, error_msg if all parsing fails.
        """
        if not text or not text.strip():
            logger.debug("JSON parsing failed: Empty response text")
            return None, "Empty response text"

        # Clean the response
        cleaned_text = self.clean_llm_response(text)
        if not cleaned_text:
            logger.debug("JSON parsing failed: Response became empty after cleaning")
            return None, "Response became empty after cleaning"

        # Try parsing the cleaned text directly first
        parsed, error = self.parse_json_safe(cleaned_text)
        if parsed is not None:
            logger.debug("JSON parsing succeeded with direct parsing")
            return parsed, None

        # Extract JSON candidates from the cleaned text
        candidates = self.extract_json_from_text(cleaned_text)

        # Limit candidates to avoid excessive processing
        candidates = candidates[:max_candidates]
        logger.debug(f"Extracted {len(candidates)} JSON candidates from response")

        # Try each candidate
        for i, candidate in enumerate(candidates):
            logger.debug(f"Trying candidate {i + 1}: {candidate[:100]}...")
            # Try the candidate as-is
            parsed, error = self.parse_json_safe(candidate)
            if parsed is not None:
                logger.debug(f"JSON parsing succeeded with candidate {i + 1}")
                return parsed, None

            # Try to fix common issues
            fixed_candidates = self.try_fix_common_json_issues(candidate)
            for j, fixed in enumerate(fixed_candidates):
                if fixed != candidate:  # Only try if different
                    logger.debug(
                        f"Trying fixed candidate {i + 1}.{j + 1}: {fixed[:100]}..."
                    )
                    parsed, error = self.parse_json_safe(fixed)
                    if parsed is not None:
                        logger.debug(
                            f"JSON parsing succeeded with fixed candidate {i + 1}.{j - 1}"
                        )
                        return parsed, None

        # If all parsing failed, return the best error message
        error_msg = f"Failed to extract valid JSON from response. Tried {len(candidates)} candidates."
        logger.warning(
            f"JSON parsing failed: {error_msg}. Original text: {text[:200]}..."
        )
        return None, error_msg

    def xǁRobustJSONParserǁextract_and_parse_json__mutmut_61(
        self, text: str, max_candidates: int = 5
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Extract and parse JSON from LLM response with multiple fallback strategies.

        Args:
            text: Text containing JSON response from LLM.
            max_candidates: Maximum number of JSON candidates to try.

        Returns:
            Tuple of (parsed_json, error_message). Returns None, error_msg if all parsing fails.
        """
        if not text or not text.strip():
            logger.debug("JSON parsing failed: Empty response text")
            return None, "Empty response text"

        # Clean the response
        cleaned_text = self.clean_llm_response(text)
        if not cleaned_text:
            logger.debug("JSON parsing failed: Response became empty after cleaning")
            return None, "Response became empty after cleaning"

        # Try parsing the cleaned text directly first
        parsed, error = self.parse_json_safe(cleaned_text)
        if parsed is not None:
            logger.debug("JSON parsing succeeded with direct parsing")
            return parsed, None

        # Extract JSON candidates from the cleaned text
        candidates = self.extract_json_from_text(cleaned_text)

        # Limit candidates to avoid excessive processing
        candidates = candidates[:max_candidates]
        logger.debug(f"Extracted {len(candidates)} JSON candidates from response")

        # Try each candidate
        for i, candidate in enumerate(candidates):
            logger.debug(f"Trying candidate {i + 1}: {candidate[:100]}...")
            # Try the candidate as-is
            parsed, error = self.parse_json_safe(candidate)
            if parsed is not None:
                logger.debug(f"JSON parsing succeeded with candidate {i + 1}")
                return parsed, None

            # Try to fix common issues
            fixed_candidates = self.try_fix_common_json_issues(candidate)
            for j, fixed in enumerate(fixed_candidates):
                if fixed != candidate:  # Only try if different
                    logger.debug(
                        f"Trying fixed candidate {i + 1}.{j + 1}: {fixed[:100]}..."
                    )
                    parsed, error = self.parse_json_safe(fixed)
                    if parsed is not None:
                        logger.debug(
                            f"JSON parsing succeeded with fixed candidate {i + 1}.{j + 2}"
                        )
                        return parsed, None

        # If all parsing failed, return the best error message
        error_msg = f"Failed to extract valid JSON from response. Tried {len(candidates)} candidates."
        logger.warning(
            f"JSON parsing failed: {error_msg}. Original text: {text[:200]}..."
        )
        return None, error_msg

    def xǁRobustJSONParserǁextract_and_parse_json__mutmut_62(
        self, text: str, max_candidates: int = 5
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Extract and parse JSON from LLM response with multiple fallback strategies.

        Args:
            text: Text containing JSON response from LLM.
            max_candidates: Maximum number of JSON candidates to try.

        Returns:
            Tuple of (parsed_json, error_message). Returns None, error_msg if all parsing fails.
        """
        if not text or not text.strip():
            logger.debug("JSON parsing failed: Empty response text")
            return None, "Empty response text"

        # Clean the response
        cleaned_text = self.clean_llm_response(text)
        if not cleaned_text:
            logger.debug("JSON parsing failed: Response became empty after cleaning")
            return None, "Response became empty after cleaning"

        # Try parsing the cleaned text directly first
        parsed, error = self.parse_json_safe(cleaned_text)
        if parsed is not None:
            logger.debug("JSON parsing succeeded with direct parsing")
            return parsed, None

        # Extract JSON candidates from the cleaned text
        candidates = self.extract_json_from_text(cleaned_text)

        # Limit candidates to avoid excessive processing
        candidates = candidates[:max_candidates]
        logger.debug(f"Extracted {len(candidates)} JSON candidates from response")

        # Try each candidate
        for i, candidate in enumerate(candidates):
            logger.debug(f"Trying candidate {i + 1}: {candidate[:100]}...")
            # Try the candidate as-is
            parsed, error = self.parse_json_safe(candidate)
            if parsed is not None:
                logger.debug(f"JSON parsing succeeded with candidate {i + 1}")
                return parsed, None

            # Try to fix common issues
            fixed_candidates = self.try_fix_common_json_issues(candidate)
            for j, fixed in enumerate(fixed_candidates):
                if fixed != candidate:  # Only try if different
                    logger.debug(
                        f"Trying fixed candidate {i + 1}.{j + 1}: {fixed[:100]}..."
                    )
                    parsed, error = self.parse_json_safe(fixed)
                    if parsed is not None:
                        logger.debug(
                            f"JSON parsing succeeded with fixed candidate {i + 1}.{j + 1}"
                        )
                        return parsed, None

        # If all parsing failed, return the best error message
        error_msg = None
        logger.warning(
            f"JSON parsing failed: {error_msg}. Original text: {text[:200]}..."
        )
        return None, error_msg

    def xǁRobustJSONParserǁextract_and_parse_json__mutmut_63(
        self, text: str, max_candidates: int = 5
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Extract and parse JSON from LLM response with multiple fallback strategies.

        Args:
            text: Text containing JSON response from LLM.
            max_candidates: Maximum number of JSON candidates to try.

        Returns:
            Tuple of (parsed_json, error_message). Returns None, error_msg if all parsing fails.
        """
        if not text or not text.strip():
            logger.debug("JSON parsing failed: Empty response text")
            return None, "Empty response text"

        # Clean the response
        cleaned_text = self.clean_llm_response(text)
        if not cleaned_text:
            logger.debug("JSON parsing failed: Response became empty after cleaning")
            return None, "Response became empty after cleaning"

        # Try parsing the cleaned text directly first
        parsed, error = self.parse_json_safe(cleaned_text)
        if parsed is not None:
            logger.debug("JSON parsing succeeded with direct parsing")
            return parsed, None

        # Extract JSON candidates from the cleaned text
        candidates = self.extract_json_from_text(cleaned_text)

        # Limit candidates to avoid excessive processing
        candidates = candidates[:max_candidates]
        logger.debug(f"Extracted {len(candidates)} JSON candidates from response")

        # Try each candidate
        for i, candidate in enumerate(candidates):
            logger.debug(f"Trying candidate {i + 1}: {candidate[:100]}...")
            # Try the candidate as-is
            parsed, error = self.parse_json_safe(candidate)
            if parsed is not None:
                logger.debug(f"JSON parsing succeeded with candidate {i + 1}")
                return parsed, None

            # Try to fix common issues
            fixed_candidates = self.try_fix_common_json_issues(candidate)
            for j, fixed in enumerate(fixed_candidates):
                if fixed != candidate:  # Only try if different
                    logger.debug(
                        f"Trying fixed candidate {i + 1}.{j + 1}: {fixed[:100]}..."
                    )
                    parsed, error = self.parse_json_safe(fixed)
                    if parsed is not None:
                        logger.debug(
                            f"JSON parsing succeeded with fixed candidate {i + 1}.{j + 1}"
                        )
                        return parsed, None

        # If all parsing failed, return the best error message
        error_msg = f"Failed to extract valid JSON from response. Tried {len(candidates)} candidates."
        logger.warning(None)
        return None, error_msg

    def xǁRobustJSONParserǁextract_and_parse_json__mutmut_64(
        self, text: str, max_candidates: int = 5
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Extract and parse JSON from LLM response with multiple fallback strategies.

        Args:
            text: Text containing JSON response from LLM.
            max_candidates: Maximum number of JSON candidates to try.

        Returns:
            Tuple of (parsed_json, error_message). Returns None, error_msg if all parsing fails.
        """
        if not text or not text.strip():
            logger.debug("JSON parsing failed: Empty response text")
            return None, "Empty response text"

        # Clean the response
        cleaned_text = self.clean_llm_response(text)
        if not cleaned_text:
            logger.debug("JSON parsing failed: Response became empty after cleaning")
            return None, "Response became empty after cleaning"

        # Try parsing the cleaned text directly first
        parsed, error = self.parse_json_safe(cleaned_text)
        if parsed is not None:
            logger.debug("JSON parsing succeeded with direct parsing")
            return parsed, None

        # Extract JSON candidates from the cleaned text
        candidates = self.extract_json_from_text(cleaned_text)

        # Limit candidates to avoid excessive processing
        candidates = candidates[:max_candidates]
        logger.debug(f"Extracted {len(candidates)} JSON candidates from response")

        # Try each candidate
        for i, candidate in enumerate(candidates):
            logger.debug(f"Trying candidate {i + 1}: {candidate[:100]}...")
            # Try the candidate as-is
            parsed, error = self.parse_json_safe(candidate)
            if parsed is not None:
                logger.debug(f"JSON parsing succeeded with candidate {i + 1}")
                return parsed, None

            # Try to fix common issues
            fixed_candidates = self.try_fix_common_json_issues(candidate)
            for j, fixed in enumerate(fixed_candidates):
                if fixed != candidate:  # Only try if different
                    logger.debug(
                        f"Trying fixed candidate {i + 1}.{j + 1}: {fixed[:100]}..."
                    )
                    parsed, error = self.parse_json_safe(fixed)
                    if parsed is not None:
                        logger.debug(
                            f"JSON parsing succeeded with fixed candidate {i + 1}.{j + 1}"
                        )
                        return parsed, None

        # If all parsing failed, return the best error message
        error_msg = f"Failed to extract valid JSON from response. Tried {len(candidates)} candidates."
        logger.warning(
            f"JSON parsing failed: {error_msg}. Original text: {text[:201]}..."
        )
        return None, error_msg

    xǁRobustJSONParserǁextract_and_parse_json__mutmut_mutants: ClassVar[MutantDict] = {
        "xǁRobustJSONParserǁextract_and_parse_json__mutmut_1": xǁRobustJSONParserǁextract_and_parse_json__mutmut_1,
        "xǁRobustJSONParserǁextract_and_parse_json__mutmut_2": xǁRobustJSONParserǁextract_and_parse_json__mutmut_2,
        "xǁRobustJSONParserǁextract_and_parse_json__mutmut_3": xǁRobustJSONParserǁextract_and_parse_json__mutmut_3,
        "xǁRobustJSONParserǁextract_and_parse_json__mutmut_4": xǁRobustJSONParserǁextract_and_parse_json__mutmut_4,
        "xǁRobustJSONParserǁextract_and_parse_json__mutmut_5": xǁRobustJSONParserǁextract_and_parse_json__mutmut_5,
        "xǁRobustJSONParserǁextract_and_parse_json__mutmut_6": xǁRobustJSONParserǁextract_and_parse_json__mutmut_6,
        "xǁRobustJSONParserǁextract_and_parse_json__mutmut_7": xǁRobustJSONParserǁextract_and_parse_json__mutmut_7,
        "xǁRobustJSONParserǁextract_and_parse_json__mutmut_8": xǁRobustJSONParserǁextract_and_parse_json__mutmut_8,
        "xǁRobustJSONParserǁextract_and_parse_json__mutmut_9": xǁRobustJSONParserǁextract_and_parse_json__mutmut_9,
        "xǁRobustJSONParserǁextract_and_parse_json__mutmut_10": xǁRobustJSONParserǁextract_and_parse_json__mutmut_10,
        "xǁRobustJSONParserǁextract_and_parse_json__mutmut_11": xǁRobustJSONParserǁextract_and_parse_json__mutmut_11,
        "xǁRobustJSONParserǁextract_and_parse_json__mutmut_12": xǁRobustJSONParserǁextract_and_parse_json__mutmut_12,
        "xǁRobustJSONParserǁextract_and_parse_json__mutmut_13": xǁRobustJSONParserǁextract_and_parse_json__mutmut_13,
        "xǁRobustJSONParserǁextract_and_parse_json__mutmut_14": xǁRobustJSONParserǁextract_and_parse_json__mutmut_14,
        "xǁRobustJSONParserǁextract_and_parse_json__mutmut_15": xǁRobustJSONParserǁextract_and_parse_json__mutmut_15,
        "xǁRobustJSONParserǁextract_and_parse_json__mutmut_16": xǁRobustJSONParserǁextract_and_parse_json__mutmut_16,
        "xǁRobustJSONParserǁextract_and_parse_json__mutmut_17": xǁRobustJSONParserǁextract_and_parse_json__mutmut_17,
        "xǁRobustJSONParserǁextract_and_parse_json__mutmut_18": xǁRobustJSONParserǁextract_and_parse_json__mutmut_18,
        "xǁRobustJSONParserǁextract_and_parse_json__mutmut_19": xǁRobustJSONParserǁextract_and_parse_json__mutmut_19,
        "xǁRobustJSONParserǁextract_and_parse_json__mutmut_20": xǁRobustJSONParserǁextract_and_parse_json__mutmut_20,
        "xǁRobustJSONParserǁextract_and_parse_json__mutmut_21": xǁRobustJSONParserǁextract_and_parse_json__mutmut_21,
        "xǁRobustJSONParserǁextract_and_parse_json__mutmut_22": xǁRobustJSONParserǁextract_and_parse_json__mutmut_22,
        "xǁRobustJSONParserǁextract_and_parse_json__mutmut_23": xǁRobustJSONParserǁextract_and_parse_json__mutmut_23,
        "xǁRobustJSONParserǁextract_and_parse_json__mutmut_24": xǁRobustJSONParserǁextract_and_parse_json__mutmut_24,
        "xǁRobustJSONParserǁextract_and_parse_json__mutmut_25": xǁRobustJSONParserǁextract_and_parse_json__mutmut_25,
        "xǁRobustJSONParserǁextract_and_parse_json__mutmut_26": xǁRobustJSONParserǁextract_and_parse_json__mutmut_26,
        "xǁRobustJSONParserǁextract_and_parse_json__mutmut_27": xǁRobustJSONParserǁextract_and_parse_json__mutmut_27,
        "xǁRobustJSONParserǁextract_and_parse_json__mutmut_28": xǁRobustJSONParserǁextract_and_parse_json__mutmut_28,
        "xǁRobustJSONParserǁextract_and_parse_json__mutmut_29": xǁRobustJSONParserǁextract_and_parse_json__mutmut_29,
        "xǁRobustJSONParserǁextract_and_parse_json__mutmut_30": xǁRobustJSONParserǁextract_and_parse_json__mutmut_30,
        "xǁRobustJSONParserǁextract_and_parse_json__mutmut_31": xǁRobustJSONParserǁextract_and_parse_json__mutmut_31,
        "xǁRobustJSONParserǁextract_and_parse_json__mutmut_32": xǁRobustJSONParserǁextract_and_parse_json__mutmut_32,
        "xǁRobustJSONParserǁextract_and_parse_json__mutmut_33": xǁRobustJSONParserǁextract_and_parse_json__mutmut_33,
        "xǁRobustJSONParserǁextract_and_parse_json__mutmut_34": xǁRobustJSONParserǁextract_and_parse_json__mutmut_34,
        "xǁRobustJSONParserǁextract_and_parse_json__mutmut_35": xǁRobustJSONParserǁextract_and_parse_json__mutmut_35,
        "xǁRobustJSONParserǁextract_and_parse_json__mutmut_36": xǁRobustJSONParserǁextract_and_parse_json__mutmut_36,
        "xǁRobustJSONParserǁextract_and_parse_json__mutmut_37": xǁRobustJSONParserǁextract_and_parse_json__mutmut_37,
        "xǁRobustJSONParserǁextract_and_parse_json__mutmut_38": xǁRobustJSONParserǁextract_and_parse_json__mutmut_38,
        "xǁRobustJSONParserǁextract_and_parse_json__mutmut_39": xǁRobustJSONParserǁextract_and_parse_json__mutmut_39,
        "xǁRobustJSONParserǁextract_and_parse_json__mutmut_40": xǁRobustJSONParserǁextract_and_parse_json__mutmut_40,
        "xǁRobustJSONParserǁextract_and_parse_json__mutmut_41": xǁRobustJSONParserǁextract_and_parse_json__mutmut_41,
        "xǁRobustJSONParserǁextract_and_parse_json__mutmut_42": xǁRobustJSONParserǁextract_and_parse_json__mutmut_42,
        "xǁRobustJSONParserǁextract_and_parse_json__mutmut_43": xǁRobustJSONParserǁextract_and_parse_json__mutmut_43,
        "xǁRobustJSONParserǁextract_and_parse_json__mutmut_44": xǁRobustJSONParserǁextract_and_parse_json__mutmut_44,
        "xǁRobustJSONParserǁextract_and_parse_json__mutmut_45": xǁRobustJSONParserǁextract_and_parse_json__mutmut_45,
        "xǁRobustJSONParserǁextract_and_parse_json__mutmut_46": xǁRobustJSONParserǁextract_and_parse_json__mutmut_46,
        "xǁRobustJSONParserǁextract_and_parse_json__mutmut_47": xǁRobustJSONParserǁextract_and_parse_json__mutmut_47,
        "xǁRobustJSONParserǁextract_and_parse_json__mutmut_48": xǁRobustJSONParserǁextract_and_parse_json__mutmut_48,
        "xǁRobustJSONParserǁextract_and_parse_json__mutmut_49": xǁRobustJSONParserǁextract_and_parse_json__mutmut_49,
        "xǁRobustJSONParserǁextract_and_parse_json__mutmut_50": xǁRobustJSONParserǁextract_and_parse_json__mutmut_50,
        "xǁRobustJSONParserǁextract_and_parse_json__mutmut_51": xǁRobustJSONParserǁextract_and_parse_json__mutmut_51,
        "xǁRobustJSONParserǁextract_and_parse_json__mutmut_52": xǁRobustJSONParserǁextract_and_parse_json__mutmut_52,
        "xǁRobustJSONParserǁextract_and_parse_json__mutmut_53": xǁRobustJSONParserǁextract_and_parse_json__mutmut_53,
        "xǁRobustJSONParserǁextract_and_parse_json__mutmut_54": xǁRobustJSONParserǁextract_and_parse_json__mutmut_54,
        "xǁRobustJSONParserǁextract_and_parse_json__mutmut_55": xǁRobustJSONParserǁextract_and_parse_json__mutmut_55,
        "xǁRobustJSONParserǁextract_and_parse_json__mutmut_56": xǁRobustJSONParserǁextract_and_parse_json__mutmut_56,
        "xǁRobustJSONParserǁextract_and_parse_json__mutmut_57": xǁRobustJSONParserǁextract_and_parse_json__mutmut_57,
        "xǁRobustJSONParserǁextract_and_parse_json__mutmut_58": xǁRobustJSONParserǁextract_and_parse_json__mutmut_58,
        "xǁRobustJSONParserǁextract_and_parse_json__mutmut_59": xǁRobustJSONParserǁextract_and_parse_json__mutmut_59,
        "xǁRobustJSONParserǁextract_and_parse_json__mutmut_60": xǁRobustJSONParserǁextract_and_parse_json__mutmut_60,
        "xǁRobustJSONParserǁextract_and_parse_json__mutmut_61": xǁRobustJSONParserǁextract_and_parse_json__mutmut_61,
        "xǁRobustJSONParserǁextract_and_parse_json__mutmut_62": xǁRobustJSONParserǁextract_and_parse_json__mutmut_62,
        "xǁRobustJSONParserǁextract_and_parse_json__mutmut_63": xǁRobustJSONParserǁextract_and_parse_json__mutmut_63,
        "xǁRobustJSONParserǁextract_and_parse_json__mutmut_64": xǁRobustJSONParserǁextract_and_parse_json__mutmut_64,
    }

    def extract_and_parse_json(self, *args, **kwargs):
        result = _mutmut_trampoline(
            object.__getattribute__(
                self, "xǁRobustJSONParserǁextract_and_parse_json__mutmut_orig"
            ),
            object.__getattribute__(
                self, "xǁRobustJSONParserǁextract_and_parse_json__mutmut_mutants"
            ),
            args,
            kwargs,
            self,
        )
        return result

    extract_and_parse_json.__signature__ = _mutmut_signature(
        xǁRobustJSONParserǁextract_and_parse_json__mutmut_orig
    )
    xǁRobustJSONParserǁextract_and_parse_json__mutmut_orig.__name__ = (
        "xǁRobustJSONParserǁextract_and_parse_json"
    )

    def xǁRobustJSONParserǁparse_with_schema_validation__mutmut_orig(
        self, text: str, required_keys: List[str]
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
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
            logger.debug(f"Schema validation failed: Could not parse JSON - {error}")
            return None, error

        missing_keys = []
        for key in required_keys:
            if key not in parsed:
                missing_keys.append(key)

        if missing_keys:
            error_msg = f"Missing required keys: {missing_keys}"
            logger.warning(
                f"Schema validation failed: {error_msg}. Parsed keys: {list(parsed.keys())}"
            )
            return None, error_msg

        logger.debug("Schema validation succeeded: All required keys present")
        return parsed, None

    def xǁRobustJSONParserǁparse_with_schema_validation__mutmut_1(
        self, text: str, required_keys: List[str]
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Parse JSON and validate it contains required keys.

        Args:
            text: Text containing JSON response from LLM.
            required_keys: List of keys that must be present in the JSON.

        Returns:
            Tuple of (parsed_json, error_message).
        """
        parsed, error = None
        if parsed is None:
            logger.debug(f"Schema validation failed: Could not parse JSON - {error}")
            return None, error

        missing_keys = []
        for key in required_keys:
            if key not in parsed:
                missing_keys.append(key)

        if missing_keys:
            error_msg = f"Missing required keys: {missing_keys}"
            logger.warning(
                f"Schema validation failed: {error_msg}. Parsed keys: {list(parsed.keys())}"
            )
            return None, error_msg

        logger.debug("Schema validation succeeded: All required keys present")
        return parsed, None

    def xǁRobustJSONParserǁparse_with_schema_validation__mutmut_2(
        self, text: str, required_keys: List[str]
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Parse JSON and validate it contains required keys.

        Args:
            text: Text containing JSON response from LLM.
            required_keys: List of keys that must be present in the JSON.

        Returns:
            Tuple of (parsed_json, error_message).
        """
        parsed, error = self.extract_and_parse_json(None)
        if parsed is None:
            logger.debug(f"Schema validation failed: Could not parse JSON - {error}")
            return None, error

        missing_keys = []
        for key in required_keys:
            if key not in parsed:
                missing_keys.append(key)

        if missing_keys:
            error_msg = f"Missing required keys: {missing_keys}"
            logger.warning(
                f"Schema validation failed: {error_msg}. Parsed keys: {list(parsed.keys())}"
            )
            return None, error_msg

        logger.debug("Schema validation succeeded: All required keys present")
        return parsed, None

    def xǁRobustJSONParserǁparse_with_schema_validation__mutmut_3(
        self, text: str, required_keys: List[str]
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Parse JSON and validate it contains required keys.

        Args:
            text: Text containing JSON response from LLM.
            required_keys: List of keys that must be present in the JSON.

        Returns:
            Tuple of (parsed_json, error_message).
        """
        parsed, error = self.extract_and_parse_json(text)
        if parsed is not None:
            logger.debug(f"Schema validation failed: Could not parse JSON - {error}")
            return None, error

        missing_keys = []
        for key in required_keys:
            if key not in parsed:
                missing_keys.append(key)

        if missing_keys:
            error_msg = f"Missing required keys: {missing_keys}"
            logger.warning(
                f"Schema validation failed: {error_msg}. Parsed keys: {list(parsed.keys())}"
            )
            return None, error_msg

        logger.debug("Schema validation succeeded: All required keys present")
        return parsed, None

    def xǁRobustJSONParserǁparse_with_schema_validation__mutmut_4(
        self, text: str, required_keys: List[str]
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
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
            logger.debug(None)
            return None, error

        missing_keys = []
        for key in required_keys:
            if key not in parsed:
                missing_keys.append(key)

        if missing_keys:
            error_msg = f"Missing required keys: {missing_keys}"
            logger.warning(
                f"Schema validation failed: {error_msg}. Parsed keys: {list(parsed.keys())}"
            )
            return None, error_msg

        logger.debug("Schema validation succeeded: All required keys present")
        return parsed, None

    def xǁRobustJSONParserǁparse_with_schema_validation__mutmut_5(
        self, text: str, required_keys: List[str]
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
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
            logger.debug(f"Schema validation failed: Could not parse JSON - {error}")
            return None, error

        missing_keys = None
        for key in required_keys:
            if key not in parsed:
                missing_keys.append(key)

        if missing_keys:
            error_msg = f"Missing required keys: {missing_keys}"
            logger.warning(
                f"Schema validation failed: {error_msg}. Parsed keys: {list(parsed.keys())}"
            )
            return None, error_msg

        logger.debug("Schema validation succeeded: All required keys present")
        return parsed, None

    def xǁRobustJSONParserǁparse_with_schema_validation__mutmut_6(
        self, text: str, required_keys: List[str]
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
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
            logger.debug(f"Schema validation failed: Could not parse JSON - {error}")
            return None, error

        missing_keys = []
        for key in required_keys:
            if key in parsed:
                missing_keys.append(key)

        if missing_keys:
            error_msg = f"Missing required keys: {missing_keys}"
            logger.warning(
                f"Schema validation failed: {error_msg}. Parsed keys: {list(parsed.keys())}"
            )
            return None, error_msg

        logger.debug("Schema validation succeeded: All required keys present")
        return parsed, None

    def xǁRobustJSONParserǁparse_with_schema_validation__mutmut_7(
        self, text: str, required_keys: List[str]
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
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
            logger.debug(f"Schema validation failed: Could not parse JSON - {error}")
            return None, error

        missing_keys = []
        for key in required_keys:
            if key not in parsed:
                missing_keys.append(None)

        if missing_keys:
            error_msg = f"Missing required keys: {missing_keys}"
            logger.warning(
                f"Schema validation failed: {error_msg}. Parsed keys: {list(parsed.keys())}"
            )
            return None, error_msg

        logger.debug("Schema validation succeeded: All required keys present")
        return parsed, None

    def xǁRobustJSONParserǁparse_with_schema_validation__mutmut_8(
        self, text: str, required_keys: List[str]
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
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
            logger.debug(f"Schema validation failed: Could not parse JSON - {error}")
            return None, error

        missing_keys = []
        for key in required_keys:
            if key not in parsed:
                missing_keys.append(key)

        if missing_keys:
            error_msg = None
            logger.warning(
                f"Schema validation failed: {error_msg}. Parsed keys: {list(parsed.keys())}"
            )
            return None, error_msg

        logger.debug("Schema validation succeeded: All required keys present")
        return parsed, None

    def xǁRobustJSONParserǁparse_with_schema_validation__mutmut_9(
        self, text: str, required_keys: List[str]
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
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
            logger.debug(f"Schema validation failed: Could not parse JSON - {error}")
            return None, error

        missing_keys = []
        for key in required_keys:
            if key not in parsed:
                missing_keys.append(key)

        if missing_keys:
            error_msg = f"Missing required keys: {missing_keys}"
            logger.warning(None)
            return None, error_msg

        logger.debug("Schema validation succeeded: All required keys present")
        return parsed, None

    def xǁRobustJSONParserǁparse_with_schema_validation__mutmut_10(
        self, text: str, required_keys: List[str]
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
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
            logger.debug(f"Schema validation failed: Could not parse JSON - {error}")
            return None, error

        missing_keys = []
        for key in required_keys:
            if key not in parsed:
                missing_keys.append(key)

        if missing_keys:
            error_msg = f"Missing required keys: {missing_keys}"
            logger.warning(
                f"Schema validation failed: {error_msg}. Parsed keys: {list(None)}"
            )
            return None, error_msg

        logger.debug("Schema validation succeeded: All required keys present")
        return parsed, None

    def xǁRobustJSONParserǁparse_with_schema_validation__mutmut_11(
        self, text: str, required_keys: List[str]
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
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
            logger.debug(f"Schema validation failed: Could not parse JSON - {error}")
            return None, error

        missing_keys = []
        for key in required_keys:
            if key not in parsed:
                missing_keys.append(key)

        if missing_keys:
            error_msg = f"Missing required keys: {missing_keys}"
            logger.warning(
                f"Schema validation failed: {error_msg}. Parsed keys: {list(parsed.keys())}"
            )
            return None, error_msg

        logger.debug(None)
        return parsed, None

    def xǁRobustJSONParserǁparse_with_schema_validation__mutmut_12(
        self, text: str, required_keys: List[str]
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
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
            logger.debug(f"Schema validation failed: Could not parse JSON - {error}")
            return None, error

        missing_keys = []
        for key in required_keys:
            if key not in parsed:
                missing_keys.append(key)

        if missing_keys:
            error_msg = f"Missing required keys: {missing_keys}"
            logger.warning(
                f"Schema validation failed: {error_msg}. Parsed keys: {list(parsed.keys())}"
            )
            return None, error_msg

        logger.debug("XXSchema validation succeeded: All required keys presentXX")
        return parsed, None

    def xǁRobustJSONParserǁparse_with_schema_validation__mutmut_13(
        self, text: str, required_keys: List[str]
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
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
            logger.debug(f"Schema validation failed: Could not parse JSON - {error}")
            return None, error

        missing_keys = []
        for key in required_keys:
            if key not in parsed:
                missing_keys.append(key)

        if missing_keys:
            error_msg = f"Missing required keys: {missing_keys}"
            logger.warning(
                f"Schema validation failed: {error_msg}. Parsed keys: {list(parsed.keys())}"
            )
            return None, error_msg

        logger.debug("schema validation succeeded: all required keys present")
        return parsed, None

    def xǁRobustJSONParserǁparse_with_schema_validation__mutmut_14(
        self, text: str, required_keys: List[str]
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
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
            logger.debug(f"Schema validation failed: Could not parse JSON - {error}")
            return None, error

        missing_keys = []
        for key in required_keys:
            if key not in parsed:
                missing_keys.append(key)

        if missing_keys:
            error_msg = f"Missing required keys: {missing_keys}"
            logger.warning(
                f"Schema validation failed: {error_msg}. Parsed keys: {list(parsed.keys())}"
            )
            return None, error_msg

        logger.debug("SCHEMA VALIDATION SUCCEEDED: ALL REQUIRED KEYS PRESENT")
        return parsed, None

    xǁRobustJSONParserǁparse_with_schema_validation__mutmut_mutants: ClassVar[
        MutantDict
    ] = {
        "xǁRobustJSONParserǁparse_with_schema_validation__mutmut_1": xǁRobustJSONParserǁparse_with_schema_validation__mutmut_1,
        "xǁRobustJSONParserǁparse_with_schema_validation__mutmut_2": xǁRobustJSONParserǁparse_with_schema_validation__mutmut_2,
        "xǁRobustJSONParserǁparse_with_schema_validation__mutmut_3": xǁRobustJSONParserǁparse_with_schema_validation__mutmut_3,
        "xǁRobustJSONParserǁparse_with_schema_validation__mutmut_4": xǁRobustJSONParserǁparse_with_schema_validation__mutmut_4,
        "xǁRobustJSONParserǁparse_with_schema_validation__mutmut_5": xǁRobustJSONParserǁparse_with_schema_validation__mutmut_5,
        "xǁRobustJSONParserǁparse_with_schema_validation__mutmut_6": xǁRobustJSONParserǁparse_with_schema_validation__mutmut_6,
        "xǁRobustJSONParserǁparse_with_schema_validation__mutmut_7": xǁRobustJSONParserǁparse_with_schema_validation__mutmut_7,
        "xǁRobustJSONParserǁparse_with_schema_validation__mutmut_8": xǁRobustJSONParserǁparse_with_schema_validation__mutmut_8,
        "xǁRobustJSONParserǁparse_with_schema_validation__mutmut_9": xǁRobustJSONParserǁparse_with_schema_validation__mutmut_9,
        "xǁRobustJSONParserǁparse_with_schema_validation__mutmut_10": xǁRobustJSONParserǁparse_with_schema_validation__mutmut_10,
        "xǁRobustJSONParserǁparse_with_schema_validation__mutmut_11": xǁRobustJSONParserǁparse_with_schema_validation__mutmut_11,
        "xǁRobustJSONParserǁparse_with_schema_validation__mutmut_12": xǁRobustJSONParserǁparse_with_schema_validation__mutmut_12,
        "xǁRobustJSONParserǁparse_with_schema_validation__mutmut_13": xǁRobustJSONParserǁparse_with_schema_validation__mutmut_13,
        "xǁRobustJSONParserǁparse_with_schema_validation__mutmut_14": xǁRobustJSONParserǁparse_with_schema_validation__mutmut_14,
    }

    def parse_with_schema_validation(self, *args, **kwargs):
        result = _mutmut_trampoline(
            object.__getattribute__(
                self, "xǁRobustJSONParserǁparse_with_schema_validation__mutmut_orig"
            ),
            object.__getattribute__(
                self, "xǁRobustJSONParserǁparse_with_schema_validation__mutmut_mutants"
            ),
            args,
            kwargs,
            self,
        )
        return result

    parse_with_schema_validation.__signature__ = _mutmut_signature(
        xǁRobustJSONParserǁparse_with_schema_validation__mutmut_orig
    )
    xǁRobustJSONParserǁparse_with_schema_validation__mutmut_orig.__name__ = (
        "xǁRobustJSONParserǁparse_with_schema_validation"
    )


# Global instance for convenience
json_parser = RobustJSONParser()


def x_parse_llm_json_response__mutmut_orig(
    response: str, required_keys: Optional[List[str]] = None
) -> Dict[str, Any]:
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
        parsed, error = json_parser.parse_with_schema_validation(
            response, required_keys
        )
    else:
        parsed, error = json_parser.extract_and_parse_json(response)

    if parsed is None:
        raise JSONParseError(f"Failed to parse JSON from LLM response: {error}")

    return parsed


def x_parse_llm_json_response__mutmut_1(
    response: str, required_keys: Optional[List[str]] = None
) -> Dict[str, Any]:
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
        parsed, error = None
    else:
        parsed, error = json_parser.extract_and_parse_json(response)

    if parsed is None:
        raise JSONParseError(f"Failed to parse JSON from LLM response: {error}")

    return parsed


def x_parse_llm_json_response__mutmut_2(
    response: str, required_keys: Optional[List[str]] = None
) -> Dict[str, Any]:
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
        parsed, error = json_parser.parse_with_schema_validation(None, required_keys)
    else:
        parsed, error = json_parser.extract_and_parse_json(response)

    if parsed is None:
        raise JSONParseError(f"Failed to parse JSON from LLM response: {error}")

    return parsed


def x_parse_llm_json_response__mutmut_3(
    response: str, required_keys: Optional[List[str]] = None
) -> Dict[str, Any]:
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
        parsed, error = json_parser.parse_with_schema_validation(response, None)
    else:
        parsed, error = json_parser.extract_and_parse_json(response)

    if parsed is None:
        raise JSONParseError(f"Failed to parse JSON from LLM response: {error}")

    return parsed


def x_parse_llm_json_response__mutmut_4(
    response: str, required_keys: Optional[List[str]] = None
) -> Dict[str, Any]:
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
        parsed, error = json_parser.parse_with_schema_validation(required_keys)
    else:
        parsed, error = json_parser.extract_and_parse_json(response)

    if parsed is None:
        raise JSONParseError(f"Failed to parse JSON from LLM response: {error}")

    return parsed


def x_parse_llm_json_response__mutmut_5(
    response: str, required_keys: Optional[List[str]] = None
) -> Dict[str, Any]:
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
        parsed, error = json_parser.parse_with_schema_validation(
            response,
        )
    else:
        parsed, error = json_parser.extract_and_parse_json(response)

    if parsed is None:
        raise JSONParseError(f"Failed to parse JSON from LLM response: {error}")

    return parsed


def x_parse_llm_json_response__mutmut_6(
    response: str, required_keys: Optional[List[str]] = None
) -> Dict[str, Any]:
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
        parsed, error = json_parser.parse_with_schema_validation(
            response, required_keys
        )
    else:
        parsed, error = None

    if parsed is None:
        raise JSONParseError(f"Failed to parse JSON from LLM response: {error}")

    return parsed


def x_parse_llm_json_response__mutmut_7(
    response: str, required_keys: Optional[List[str]] = None
) -> Dict[str, Any]:
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
        parsed, error = json_parser.parse_with_schema_validation(
            response, required_keys
        )
    else:
        parsed, error = json_parser.extract_and_parse_json(None)

    if parsed is None:
        raise JSONParseError(f"Failed to parse JSON from LLM response: {error}")

    return parsed


def x_parse_llm_json_response__mutmut_8(
    response: str, required_keys: Optional[List[str]] = None
) -> Dict[str, Any]:
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
        parsed, error = json_parser.parse_with_schema_validation(
            response, required_keys
        )
    else:
        parsed, error = json_parser.extract_and_parse_json(response)

    if parsed is not None:
        raise JSONParseError(f"Failed to parse JSON from LLM response: {error}")

    return parsed


def x_parse_llm_json_response__mutmut_9(
    response: str, required_keys: Optional[List[str]] = None
) -> Dict[str, Any]:
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
        parsed, error = json_parser.parse_with_schema_validation(
            response, required_keys
        )
    else:
        parsed, error = json_parser.extract_and_parse_json(response)

    if parsed is None:
        raise JSONParseError(None)

    return parsed


x_parse_llm_json_response__mutmut_mutants: ClassVar[MutantDict] = {
    "x_parse_llm_json_response__mutmut_1": x_parse_llm_json_response__mutmut_1,
    "x_parse_llm_json_response__mutmut_2": x_parse_llm_json_response__mutmut_2,
    "x_parse_llm_json_response__mutmut_3": x_parse_llm_json_response__mutmut_3,
    "x_parse_llm_json_response__mutmut_4": x_parse_llm_json_response__mutmut_4,
    "x_parse_llm_json_response__mutmut_5": x_parse_llm_json_response__mutmut_5,
    "x_parse_llm_json_response__mutmut_6": x_parse_llm_json_response__mutmut_6,
    "x_parse_llm_json_response__mutmut_7": x_parse_llm_json_response__mutmut_7,
    "x_parse_llm_json_response__mutmut_8": x_parse_llm_json_response__mutmut_8,
    "x_parse_llm_json_response__mutmut_9": x_parse_llm_json_response__mutmut_9,
}


def parse_llm_json_response(*args, **kwargs):
    result = _mutmut_trampoline(
        x_parse_llm_json_response__mutmut_orig,
        x_parse_llm_json_response__mutmut_mutants,
        args,
        kwargs,
    )
    return result


parse_llm_json_response.__signature__ = _mutmut_signature(
    x_parse_llm_json_response__mutmut_orig
)
x_parse_llm_json_response__mutmut_orig.__name__ = "x_parse_llm_json_response"


def x_safe_parse_llm_json_response__mutmut_orig(
    response: str, required_keys: Optional[List[str]] = None
) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """
    Safe version of parse_llm_json_response that doesn't raise exceptions.

    Args:
        response: Raw LLM response text.
        required_keys: Optional list of keys that must be present.

    Returns:
        Tuple of (parsed_json, error_message).
    """
    try:
        if required_keys:
            return json_parser.parse_with_schema_validation(response, required_keys)
        else:
            return json_parser.extract_and_parse_json(response)
    except Exception as e:
        return None, str(e)


def x_safe_parse_llm_json_response__mutmut_1(
    response: str, required_keys: Optional[List[str]] = None
) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """
    Safe version of parse_llm_json_response that doesn't raise exceptions.

    Args:
        response: Raw LLM response text.
        required_keys: Optional list of keys that must be present.

    Returns:
        Tuple of (parsed_json, error_message).
    """
    try:
        if required_keys:
            return json_parser.parse_with_schema_validation(None, required_keys)
        else:
            return json_parser.extract_and_parse_json(response)
    except Exception as e:
        return None, str(e)


def x_safe_parse_llm_json_response__mutmut_2(
    response: str, required_keys: Optional[List[str]] = None
) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """
    Safe version of parse_llm_json_response that doesn't raise exceptions.

    Args:
        response: Raw LLM response text.
        required_keys: Optional list of keys that must be present.

    Returns:
        Tuple of (parsed_json, error_message).
    """
    try:
        if required_keys:
            return json_parser.parse_with_schema_validation(response, None)
        else:
            return json_parser.extract_and_parse_json(response)
    except Exception as e:
        return None, str(e)


def x_safe_parse_llm_json_response__mutmut_3(
    response: str, required_keys: Optional[List[str]] = None
) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """
    Safe version of parse_llm_json_response that doesn't raise exceptions.

    Args:
        response: Raw LLM response text.
        required_keys: Optional list of keys that must be present.

    Returns:
        Tuple of (parsed_json, error_message).
    """
    try:
        if required_keys:
            return json_parser.parse_with_schema_validation(required_keys)
        else:
            return json_parser.extract_and_parse_json(response)
    except Exception as e:
        return None, str(e)


def x_safe_parse_llm_json_response__mutmut_4(
    response: str, required_keys: Optional[List[str]] = None
) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """
    Safe version of parse_llm_json_response that doesn't raise exceptions.

    Args:
        response: Raw LLM response text.
        required_keys: Optional list of keys that must be present.

    Returns:
        Tuple of (parsed_json, error_message).
    """
    try:
        if required_keys:
            return json_parser.parse_with_schema_validation(
                response,
            )
        else:
            return json_parser.extract_and_parse_json(response)
    except Exception as e:
        return None, str(e)


def x_safe_parse_llm_json_response__mutmut_5(
    response: str, required_keys: Optional[List[str]] = None
) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """
    Safe version of parse_llm_json_response that doesn't raise exceptions.

    Args:
        response: Raw LLM response text.
        required_keys: Optional list of keys that must be present.

    Returns:
        Tuple of (parsed_json, error_message).
    """
    try:
        if required_keys:
            return json_parser.parse_with_schema_validation(response, required_keys)
        else:
            return json_parser.extract_and_parse_json(None)
    except Exception as e:
        return None, str(e)


def x_safe_parse_llm_json_response__mutmut_6(
    response: str, required_keys: Optional[List[str]] = None
) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """
    Safe version of parse_llm_json_response that doesn't raise exceptions.

    Args:
        response: Raw LLM response text.
        required_keys: Optional list of keys that must be present.

    Returns:
        Tuple of (parsed_json, error_message).
    """
    try:
        if required_keys:
            return json_parser.parse_with_schema_validation(response, required_keys)
        else:
            return json_parser.extract_and_parse_json(response)
    except Exception:
        return None, str(None)


x_safe_parse_llm_json_response__mutmut_mutants: ClassVar[MutantDict] = {
    "x_safe_parse_llm_json_response__mutmut_1": x_safe_parse_llm_json_response__mutmut_1,
    "x_safe_parse_llm_json_response__mutmut_2": x_safe_parse_llm_json_response__mutmut_2,
    "x_safe_parse_llm_json_response__mutmut_3": x_safe_parse_llm_json_response__mutmut_3,
    "x_safe_parse_llm_json_response__mutmut_4": x_safe_parse_llm_json_response__mutmut_4,
    "x_safe_parse_llm_json_response__mutmut_5": x_safe_parse_llm_json_response__mutmut_5,
    "x_safe_parse_llm_json_response__mutmut_6": x_safe_parse_llm_json_response__mutmut_6,
}


def safe_parse_llm_json_response(*args, **kwargs):
    result = _mutmut_trampoline(
        x_safe_parse_llm_json_response__mutmut_orig,
        x_safe_parse_llm_json_response__mutmut_mutants,
        args,
        kwargs,
    )
    return result


safe_parse_llm_json_response.__signature__ = _mutmut_signature(
    x_safe_parse_llm_json_response__mutmut_orig
)
x_safe_parse_llm_json_response__mutmut_orig.__name__ = "x_safe_parse_llm_json_response"
