from __future__ import annotations

import ipaddress
import logging
import re
import tempfile
from pathlib import Path
from typing import Any, Union

from pydantic import BaseModel, Field, ValidationError, validator

from resync.core.app_context import AppContext
from resync.core import env_detector

logger = logging.getLogger(__name__)


class SanitizedPath(BaseModel):
    """Sanitized file/directory path with security validations."""

    path: str = Field(..., min_length=1, max_length=4096)

    @validator("path")
    def validate_path(cls, v):
        """Validate path for security issues."""
        if not v or not v.strip():
            raise ValueError("Path cannot be empty")

        # Convert to Path for validation
        path_obj = Path(v)

        # Check for path traversal attempts
        try:
            resolved_path = path_obj.resolve()
        except (OSError, RuntimeError) as e:
            raise ValueError(f"Invalid path resolution: {e}")

        # Prevent absolute paths that could escape intended directories
        allowed_dirs = [Path.cwd(), Path.home()]
        if env_detector.is_testing():
            allowed_dirs.append(Path(tempfile.gettempdir()))

        if resolved_path.is_absolute() and not any(
            str(resolved_path).startswith(str(allowed.resolve()))
            for allowed in allowed_dirs
        ):
            raise ValueError(
                "Absolute paths outside allowed directories are not permitted"
            )

        # Check for suspicious patterns
        suspicious_patterns = ["..", "\\", "\x00", "\n", "\r"]
        for pattern in suspicious_patterns:
            if pattern in v:
                raise ValueError(f"Path contains suspicious pattern: {pattern}")

        return str(resolved_path)


class SanitizedHostPort(BaseModel):
    """Sanitized IP address and port combination."""

    host: str = Field(..., min_length=1, max_length=253)
    port: int = Field(..., ge=1, le=65535)

    @validator("host")
    def validate_host(cls, v):
        """Validate host as IP address or valid hostname."""
        if not v or not v.strip():
            raise ValueError("Host cannot be empty")

        # Remove whitespace
        v = v.strip()

        # Try to parse as IP address first
        try:
            ipaddress.ip_address(v)
            return v
        except ValueError:
            pass

        # Validate as hostname
        if not re.match(
            r"^[a-zA-Z0-9]([a-zA-Z0-9\-]*[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]*[a-zA-Z0-9])?)*$",
            v,
        ):
            raise ValueError("Invalid hostname format")

        return v

    @validator("port")
    def validate_port(cls, v):
        """Validate port number."""
        if v < 1024:
            import warnings
            warnings.warn(
                f"Using privileged port {v} - ensure proper permissions", UserWarning
            )
        suspicious_ports = [22, 23, 25, 53, 80, 443, 3306, 5432]
        if v in suspicious_ports:
            import warnings
            warnings.warn(
                f"Using well-known port {v} - verify this is intended", UserWarning
            )
        return v


class InputSanitizer:
    """Global input sanitization utilities."""

    @staticmethod
    def sanitize_path(path: Union[str, Path]) -> Path:
        """Sanitize and validate file/directory path."""
        try:
            sanitized = SanitizedPath(path=str(path))
            return Path(sanitized.path)
        except ValidationError as e:
            correlation_id = AppContext.get_correlation_id()
            logger.error(
                f"Path sanitization failed: {path}",
                extra={
                    "correlation_id": correlation_id,
                    "component": "input_sanitizer",
                    "operation": "sanitize_path",
                    "error": e,
                    "invalid_path": str(path),
                },
            )
            raise ValueError(f"Invalid path: {e}") from e

    @staticmethod
    def sanitize_host_port(host_port: str) -> tuple[str, int]:
        """Sanitize and validate host:port combination."""
        if ":" not in host_port:
            raise ValueError("Host:port format required (host:port)")

        try:
            host, port_str = host_port.rsplit(":", 1)
            port = int(port_str)
            sanitized = SanitizedHostPort(host=host, port=port)
            return sanitized.host, sanitized.port
        except (ValueError, ValidationError) as e:
            correlation_id = AppContext.get_correlation_id()
            logger.error(
                f"Host:port sanitization failed: {host_port}",
                extra={
                    "correlation_id": correlation_id,
                    "component": "input_sanitizer",
                    "operation": "sanitize_host_port",
                    "error": e,
                    "invalid_host_port": host_port,
                },
            )
            raise ValueError(f"Invalid host:port format: {e}") from e

    @staticmethod
    def sanitize_environment_value(
        key: str, value: Any, expected_type: type = str
    ) -> Any:
        """Sanitize environment variable value with type validation."""
        if value is None:
            raise ValueError(f"Environment variable {key} is not set")
        try:
            if expected_type == bool:
                if isinstance(value, str):
                    return value.lower() in ("true", "1", "yes", "on")
                return bool(value)
            elif expected_type == int:
                return int(value)
            elif expected_type == float:
                return float(value)
            elif expected_type == str:
                if not isinstance(value, str):
                    value = str(value)
                value = value.strip()
                if not value:
                    raise ValueError(f"Environment variable {key} cannot be empty")
                return value
            else:
                return expected_type(value)
        except (ValueError, TypeError) as e:
            correlation_id = AppContext.get_correlation_id()
            logger.error(
                f"Environment variable sanitization failed: {key}={value}",
                extra={
                    "correlation_id": correlation_id,
                    "component": "input_sanitizer",
                    "operation": "sanitize_env",
                    "error": e,
                    "env_key": key,
                    "env_value": str(value),
                    "expected_type": expected_type.__name__,
                },
            )
            raise ValueError(f"Invalid environment variable {key}: {e}") from e

    @staticmethod
    def validate_path_exists(path: Union[str, Path], must_exist: bool = True) -> Path:
        """Validate path exists and is accessible."""
        sanitized_path = InputSanitizer.sanitize_path(path)
        if must_exist:
            if not sanitized_path.exists():
                correlation_id = AppContext.get_correlation_id()
                logger.error(
                    f"Required path does not exist: {sanitized_path}",
                    extra={
                        "correlation_id": correlation_id,
                        "component": "input_sanitizer",
                        "operation": "validate_path_exists",
                        "path": str(sanitized_path),
                    },
                )
                raise FileNotFoundError(f"Path does not exist: {sanitized_path}")
            if sanitized_path.is_symlink():
                target = sanitized_path.readlink()
                if not str(target).startswith(str(Path.cwd())):
                    raise ValueError(
                        f"Symlink points outside allowed directory: {sanitized_path} -> {target}"
                    )
        return sanitized_path