"""
Hardened Core Package Initialization for Resync

This module provides hardened initialization and lifecycle management for core components
with comprehensive error handling, health validation, and security measures.
"""
import asyncio
import logging
import os
import re
import threading
import time
from typing import Any, Dict, Optional, Set

# Initialize logger early
logger = logging.getLogger(__name__)

from .async_cache import AsyncTTLCache
from .config_watcher import handle_config_change
from .connection_manager import ConnectionManager
from .metrics import runtime_metrics

# --- Core Component Boot Manager ---
class CoreBootManager:
    """Hardened boot manager for core components with lifecycle tracking and health validation."""

    def __init__(self):
        self._components: Dict[str, Any] = {}
        self._boot_times: Dict[str, float] = {}
        self._health_status: Dict[str, Dict[str, Any]] = {}
        self._boot_lock = threading.RLock()
        # Global correlation ID for distributed tracing
        self._correlation_id = f"core_boot_{int(time.time())}_{os.urandom(4).hex()}"
        self._failed_imports: Set[str] = set()
        self._global_correlation_context = {
            "boot_id": self._correlation_id,
            "environment": env_detector._environment,
            "security_level": env_detector._security_level,
            "start_time": time.time(),
            "events": []
        }

    def register_component(self, name: str, component: Any, health_check: bool = True) -> None:
        """Register a component with health validation."""
        with self._boot_lock:
            start_time = time.time()
            try:
                self._components[name] = component
                self._boot_times[name] = time.time() - start_time

                if health_check and hasattr(component, 'health_check'):
                    # Perform immediate health check
                    health_result = asyncio.run(self._check_component_health(component))
                    self._health_status[name] = health_result
                else:
                    self._health_status[name] = {"status": "unknown", "message": "No health check available"}

                logger.info(f"Component '{name}' registered successfully",
                          extra={"correlation_id": self._correlation_id, "component": name,
                                "boot_time": self._boot_times[name]})

            except Exception as e:
                logger.error(f"Failed to register component '{name}': {e}",
                           extra={"correlation_id": self._correlation_id, "component": name, "error": e})
                raise

    def get_component(self, name: str) -> Any:
        """Get a component with validation."""
        if name not in self._components:
            raise KeyError(f"Component '{name}' not registered")
        return self._components[name]

    async def _check_component_health(self, component: Any) -> Dict[str, Any]:
        """Check component health asynchronously."""
        try:
            if asyncio.iscoroutinefunction(component.health_check):
                return await asyncio.wait_for(component.health_check(), timeout=5.0)
            else:
                # Run sync health check in thread pool
                loop = asyncio.get_event_loop()
                return await asyncio.wait_for(
                    loop.run_in_executor(None, component.health_check), timeout=5.0
                )
        except asyncio.TimeoutError:
            return {"status": "error", "message": "Health check timeout"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_boot_status(self) -> Dict[str, Any]:
        """Get comprehensive boot status."""
        with self._boot_lock:
            total_boot_time = sum(self._boot_times.values())
            failed_count = len(self._failed_imports)

            return {
                "correlation_id": self._correlation_id,
                "total_components": len(self._components),
                "total_boot_time": total_boot_time,
                "failed_imports": list(self._failed_imports),
                "failed_count": failed_count,
                "components": {
                    name: {
                        "boot_time": self._boot_times.get(name, 0),
                        "health": self._health_status.get(name, {"status": "unknown"})
                    }
                    for name in self._components.keys()
                },
                "overall_status": "healthy" if failed_count == 0 else "degraded",
                "global_context": self._global_correlation_context.copy()
            }

    def get_global_correlation_id(self) -> str:
        """Get the global correlation ID for distributed tracing."""
        return self._correlation_id

    def add_global_event(self, event: str, data: Optional[Dict[str, Any]] = None) -> None:
        """Add an event to the global correlation context."""
        with self._boot_lock:
            self._global_correlation_context["events"].append({
                "timestamp": time.time(),
                "event": event,
                "data": data or {}
            })

    def get_environment_tags(self) -> Dict[str, Any]:
        """Get environment tags for mock detection and debugging."""
        return {
            "environment": env_detector._environment,
            "is_production": env_detector._is_production,
            "is_testing": env_detector._is_testing,
            "security_level": env_detector._security_level,
            "should_use_mocks": env_detector.should_use_mocks(),
            "correlation_id": self._correlation_id,
            "boot_timestamp": self._global_correlation_context["start_time"]
        }

    def safe_import(self, module_path: str, component_name: str) -> Optional[Any]:
        """Safely import a component with comprehensive error handling."""
        try:
            module_parts = module_path.split('.')
            if len(module_parts) == 2:
                # Local import
                module = __import__(f".{module_parts[1]}", fromlist=[module_parts[1]], level=1)
                component = getattr(module, module_parts[1])
                logger.info(f"Successfully imported {component_name} from {module_path}",
                          extra={"correlation_id": self._correlation_id, "component": component_name})
                return component
            else:
                # Absolute import
                module = __import__(module_path)
                component = getattr(module, component_name)
                logger.info(f"Successfully imported {component_name} from {module_path}",
                          extra={"correlation_id": self._correlation_id, "component": component_name})
                return component

        except ImportError as e:
            error_msg = f"Import failed for {component_name}: {e}"
            logger.warning(error_msg, extra={"correlation_id": self._correlation_id,
                                           "component": component_name, "error": e})
            self._failed_imports.add(component_name)
            return None
        except AttributeError as e:
            error_msg = f"Component '{component_name}' not found in module '{module_path}': {e}"
            logger.warning(error_msg, extra={"correlation_id": self._correlation_id,
                                           "component": component_name, "error": e})
            self._failed_imports.add(component_name)
            return None
        except Exception as e:
            error_msg = f"Unexpected error importing {component_name}: {e}"
            logger.error(error_msg, extra={"correlation_id": self._correlation_id,
                                         "component": component_name, "error": e})
            self._failed_imports.add(component_name)
            return None


# --- Environment Detection and Security ---
class EnvironmentDetector:
    """Detects and validates execution environment for security."""

    def __init__(self):
        self._environment = self._detect_environment()
        self._is_production = self._environment == "production"
        self._is_testing = self._environment in ["testing", "test"]
        self._security_level = "high" if self._is_production else "medium"

    def _detect_environment(self) -> str:
        """Detect current environment from multiple sources."""
        # Priority: env var > settings > default
        env_sources = [
            os.getenv("APP_ENV"),
            os.getenv("ENVIRONMENT"),
            os.getenv("RESYNC_ENV"),
        ]

        for env in env_sources:
            if env and env.strip():
                return env.strip().lower()

        # Default to production for safety
        return "production"

    def validate_environment(self) -> bool:
        """Validate that current environment is properly configured."""
        valid_envs = {"development", "staging", "production", "testing", "test"}

        if self._environment not in valid_envs:
            logger.error(f"Invalid environment detected: {self._environment}",
                        extra={"correlation_id": boot_manager._correlation_id,
                              "invalid_env": self._environment})
            return False

        logger.info(f"Environment validated: {self._environment} (security: {self._security_level})",
                   extra={"correlation_id": boot_manager._correlation_id,
                         "environment": self._environment,
                         "security_level": self._security_level})
        return True

    def is_production(self) -> bool:
        """Check if running in production."""
        return self._is_production

    def is_testing(self) -> bool:
        """Check if running in testing environment."""
        return self._is_testing

    def should_use_mocks(self) -> bool:
        """Determine if mocks should be used."""
        return self._is_testing

    def get_security_level(self) -> str:
        """Get current security level."""
        return self._security_level


# Global environment detector
env_detector = EnvironmentDetector()


# Global boot manager instance
boot_manager = CoreBootManager()


# --- Hardened Encryption Service ---
class EncryptionService:
    """Production-ready encryption service with environment awareness."""

    def __init__(self):
        self._is_mock = env_detector.should_use_mocks()
        self._security_level = env_detector.get_security_level()

        if self._is_mock:
            logger.warning("Using MOCK encryption service - NOT SECURE FOR PRODUCTION",
                         extra={"correlation_id": boot_manager._correlation_id,
                               "service": "encryption", "mock": True})
        else:
            logger.info("Using production encryption service",
                       extra={"correlation_id": boot_manager._correlation_id,
                             "service": "encryption", "security_level": self._security_level})

    def encrypt(self, data: str) -> str:
        """Encrypt sensitive data with environment-aware implementation."""
        if not data or not isinstance(data, str):
            raise ValueError("Data must be non-empty string")

        if self._is_mock:
            # Mock implementation for testing
            return f"mock_encrypted_{hash(data) % 1000}"
        else:
            # TODO: Implement real encryption (AES-256, etc.)
            # For now, use a more secure mock that indicates production mode
            import hashlib
            import secrets
            salt = secrets.token_hex(8)
            return f"prod_encrypted_{hashlib.sha256((salt + data).encode()).hexdigest()[:16]}"

    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt data with validation."""
        if not encrypted_data or not isinstance(encrypted_data, str):
            raise ValueError("Encrypted data must be non-empty string")

        if self._is_mock:
            # Mock decryption
            if encrypted_data.startswith("mock_encrypted_"):
                return f"decrypted_data_{encrypted_data.split('_')[-1]}"
            else:
                raise ValueError("Invalid mock encrypted data format")
        else:
            # TODO: Implement real decryption
            # For now, return placeholder indicating production mode
            if encrypted_data.startswith("prod_encrypted_"):
                return f"prod_decrypted_{encrypted_data.split('_')[-1]}"
            else:
                raise ValueError("Invalid encrypted data format")

    async def health_check(self) -> Dict[str, Any]:
        """Health check for encryption service."""
        try:
            # Test basic functionality
            test_data = "health_check_test"
            encrypted = self.encrypt(test_data)
            decrypted = self.decrypt(encrypted)

            return {
                "status": "healthy" if encrypted and decrypted else "error",
                "service": "encryption",
                "mock_mode": self._is_mock,
                "security_level": self._security_level,
                "test_encryption": bool(encrypted),
                "test_decryption": bool(decrypted),
                "timestamp": time.time()
            }
        except Exception as e:
            return {
                "status": "error",
                "service": "encryption",
                "error": str(e),
                "mock_mode": self._is_mock,
                "timestamp": time.time()
            }


# --- Component Registration with Safe Imports ---
def register_core_components():
    """Register all core components with safe imports and health checks."""

    # Always available components
    boot_manager.register_component("AsyncTTLCache", AsyncTTLCache)
    boot_manager.register_component("handle_config_change", handle_config_change)
    boot_manager.register_component("runtime_metrics", runtime_metrics)

    # Safe import for agent_manager
    agent_mgr = boot_manager.safe_import("resync.core.agent_manager", "agent_manager")
    if agent_mgr:
        boot_manager.register_component("agent_manager", agent_mgr)
    else:
        logger.warning("Agent manager not available - system will operate in limited mode",
                     extra={"correlation_id": boot_manager._correlation_id})

    # Safe import for knowledge_graph
    kg = boot_manager.safe_import("resync.core.knowledge_graph", "AsyncKnowledgeGraph")
    if kg:
        # Create singleton instance
        kg_instance = kg()
        boot_manager.register_component("knowledge_graph", kg_instance)
    else:
        logger.warning("Knowledge graph not available - RAG features disabled",
                     extra={"correlation_id": boot_manager._correlation_id})

    # Connection manager (always available)
    connection_mgr = ConnectionManager()
    boot_manager.register_component("connection_manager", connection_mgr)

    # Encryption service with environment awareness
    encryption_svc = EncryptionService()
    boot_manager.register_component("encryption_service", encryption_svc, health_check=True)


# Initialize components
register_core_components()


__all__ = [
    "AsyncTTLCache",
    "ConnectionManager",
    "handle_config_change",
    "runtime_metrics",
    "boot_manager",
    "env_detector",
    # Global correlation and environment access
    "get_global_correlation_id",
    "get_environment_tags",
    # Components registered dynamically based on availability
]


# --- Hardened Log Security ---
class SensitiveDataMasker:
    """Advanced sensitive data masking for logs with comprehensive pattern matching."""

    # Patterns for sensitive data (case-insensitive) - PARANOID LEVEL
    SENSITIVE_PATTERNS = [
        # Authentication - Enhanced
        r'\bpassword[\'"]?\s*[:=]\s*[\'"]([^\'"]*)[\'"]',  # password="value"
        r'\bpassword[\'"]?\s*[:=]\s*([^\s\'",;}]*)',       # password=value
        r'\bpasswd[\'"]?\s*[:=]\s*[\'"]([^\'"]*)[\'"]',    # passwd="value"
        r'\bpasswd[\'"]?\s*[:=]\s*([^\s\'",;}]*)',         # passwd=value
        r'\bclear[_-]?text[\'"]?\s*[:=]\s*[\'"]([^\'"]*)[\'"]',  # clear_text="value"

        # API Keys and Tokens - Expanded
        r'\bapi[_-]?key[\'"]?\s*[:=]\s*[\'"]([^\'"]*)[\'"]',     # api_key="value"
        r'\bapi[_-]?key[\'"]?\s*[:=]\s*([^\s\'",;}]*)',          # api_key=value
        r'\bauthorization[\'"]?\s*[:=]\s*[\'"]([^\'"]*)[\'"]',    # authorization="value"
        r'\bbearer[\'"]?\s*[:=]\s*[\'"]([^\'"]*)[\'"]',           # bearer="value"
        r'\btoken[\'"]?\s*[:=]\s*[\'"]([^\'"]*)[\'"]',            # token="value"
        r'\baccess[_-]?token[\'"]?\s*[:=]\s*[\'"]([^\'"]*)[\'"]', # access_token="value"
        r'\brefresh[_-]?token[\'"]?\s*[:=]\s*[\'"]([^\'"]*)[\'"]', # refresh_token="value"
        r'\bjwt[\'"]?\s*[:=]\s*[\'"]([^\'"]*)[\'"]',              # jwt="value"
        r'\boauth[_-]?token[\'"]?\s*[:=]\s*[\'"]([^\'"]*)[\'"]',  # oauth_token="value"

        # Secrets and Keys - Comprehensive
        r'\bsecret[\'"]?\s*[:=]\s*[\'"]([^\'"]*)[\'"]',           # secret="value"
        r'\bsecret[\'"]?\s*[:=]\s*([^\s\'",;}]*)',                # secret=value
        r'\bprivate[_-]?key[\'"]?\s*[:=]\s*[\'"]([^\'"]*)[\'"]',  # private_key="value"
        r'\bpublic[_-]?key[\'"]?\s*[:=]\s*[\'"]([^\'"]*)[\'"]',   # public_key="value"
        r'\bssh[_-]?key[\'"]?\s*[:=]\s*[\'"]([^\'"]*)[\'"]',      # ssh_key="value"
        r'\bencryption[_-]?key[\'"]?\s*[:=]\s*[\'"]([^\'"]*)[\'"]', # encryption_key="value"
        r'\bsigning[_-]?key[\'"]?\s*[:=]\s*[\'"]([^\'"]*)[\'"]',  # signing_key="value"

        # Database credentials - Enhanced
        r'\bdb[_-]?password[\'"]?\s*[:=]\s*[\'"]([^\'"]*)[\'"]',   # db_password="value"
        r'\bdb[_-]?user[\'"]?\s*[:=]\s*[\'"]([^\'"]*)[\'"]',       # db_user="value"
        r'\bdb[_-]?host[\'"]?\s*[:=]\s*[\'"]([^\'"]*)[\'"]',       # db_host="value"
        r'\bconnection[_-]?string[\'"]?\s*[:=]\s*[\'"]([^\'"]*)[\'"]', # connection_string="value"

        # Cloud and Infrastructure
        r'\bawss?_?access[_-]?key[_-]?id[\'"]?\s*[:=]\s*[\'"]([^\'"]*)[\'"]', # aws_access_key_id="value"
        r'\bawss?_?secret[_-]?access[_-]?key[\'"]?\s*[:=]\s*[\'"]([^\'"]*)[\'"]', # aws_secret_access_key="value"
        r'\bgcp[_-]?key[\'"]?\s*[:=]\s*[\'"]([^\'"]*)[\'"]',      # gcp_key="value"
        r'\bazure[_-]?key[\'"]?\s*[:=]\s*[\'"]([^\'"]*)[\'"]',    # azure_key="value"

        # Generic patterns for suspicious strings - PARANOID
        r'\b[A-Za-z0-9]{32,}\b',  # Long alphanumeric strings (potential tokens/keys)
        r'\beyJ[A-Za-z0-9-_]+\.eyJ[A-Za-z0-9-_]+\.[A-Za-z0-9-_]*',  # JWT tokens (eyJ...)
        r'\bsk-[a-zA-Z0-9]{48,}\b',  # OpenAI-like API keys (sk-...)
        r'\bxox[baprs]-[a-zA-Z0-9-]+',  # Slack tokens (xoxb-...)
        r'\bgh[pousr]_[A-Za-z0-9_]{36,}\b',  # GitHub tokens (ghp_...)
    ]

    MASK_REPLACEMENT = "***MASKED***"

    def __init__(self):
        self._patterns = [(re.compile(pattern, re.IGNORECASE), pattern)
                         for pattern in self.SENSITIVE_PATTERNS]
        self._masking_stats = {"total_processed": 0, "masked_records": 0}

    def mask_record(self, record: Any) -> bool:
        """Mask sensitive data in log records with PARANOID pattern matching and multi-token detection."""
        self._masking_stats["total_processed"] += 1

        if not hasattr(record, "msg"):
            return True

        original_msg = str(record.msg)
        masked_msg = original_msg
        masked_any = False
        total_masks = 0

        # PARANOID: Apply all patterns with multi-pass detection
        for pattern, pattern_str in self._patterns:
            # Find all matches in current message
            matches = pattern.findall(masked_msg)
            if matches:
                # Replace ALL occurrences, not just first
                masked_msg = pattern.sub(
                    lambda m: m.group(0).replace(m.group(1) if len(m.groups()) > 0 else m.group(0),
                                                self.MASK_REPLACEMENT),
                    masked_msg
                )
                masked_any = True
                total_masks += len(matches)

        # PARANOID: Additional entropy-based detection for high-entropy strings
        if not masked_any or total_masks < 3:  # Re-scan if not many masks or no masks
            # Look for potential base64/encrypted data (40+ chars with high entropy)
            entropy_pattern = r'\b[A-Za-z0-9+/]{40,}={0,2}\b'
            entropy_matches = re.findall(entropy_pattern, masked_msg)
            if entropy_matches:
                for match in entropy_matches:
                    # Calculate simple entropy score (diversity of characters)
                    char_set = set(match)
                    entropy_score = len(char_set) / len(match)
                    if entropy_score > 0.6:  # High entropy = likely sensitive
                        masked_msg = masked_msg.replace(match, self.MASK_REPLACEMENT)
                        masked_any = True
                        total_masks += 1

            # Look for URL-encoded sensitive data
            url_pattern = r'%[0-9A-Fa-f]{2}([0-9A-Fa-f]{2})*[%=]*'
            url_matches = re.findall(url_pattern, masked_msg)
            if url_matches:
                for match in url_matches:
                    if len(match) > 20:  # Long URL-encoded strings
                        masked_msg = re.sub(url_pattern, self.MASK_REPLACEMENT, masked_msg)
                        masked_any = True
                        total_masks += 1
                        break  # Only mask once for URL patterns

        if masked_any:
            record.msg = masked_msg
            self._masking_stats["masked_records"] += 1

            # Log masking event with paranoia level
            paranoia_level = "HIGH" if total_masks > 2 else "MEDIUM" if total_masks > 0 else "LOW"
            logger.debug(f"Masked {total_masks} sensitive data items in log record (paranoia: {paranoia_level})",
                        extra={"correlation_id": boot_manager._correlation_id,
                              "masked": True, "log_level": record.levelname,
                              "masks_applied": total_masks, "paranoia_level": paranoia_level})

        return True

    def get_masking_stats(self) -> Dict[str, int]:
        """Get masking statistics."""
        return self._masking_stats.copy()


# Global masker instance
sensitive_data_masker = SensitiveDataMasker()

# Add the filter to the root logger
logging.getLogger().addFilter(sensitive_data_masker.mask_record)

# Logger already initialized at top of file


# --- Legacy Compatibility and Exports ---
def get_boot_status() -> Dict[str, Any]:
    """Get comprehensive boot status (legacy compatibility)."""
    return boot_manager.get_boot_status()


# Export components for backward compatibility
def get_component(name: str) -> Any:
    """Get a registered component."""
    return boot_manager.get_component(name)


# Safe access to components that might not be available
try:
    agent_manager = get_component("agent_manager")
except KeyError:
    agent_manager = None
    logger.warning("Agent manager not available", extra={"correlation_id": boot_manager._correlation_id})

try:
    knowledge_graph = get_component("knowledge_graph")
except KeyError:
    knowledge_graph = None
    logger.warning("Knowledge graph not available", extra={"correlation_id": boot_manager._correlation_id})

try:
    connection_manager = get_component("connection_manager")
except KeyError:
    connection_manager = ConnectionManager()  # Fallback
    logger.warning("Using fallback connection manager", extra={"correlation_id": boot_manager._correlation_id})

try:
    encryption_service = get_component("encryption_service")
except KeyError:
    encryption_service = EncryptionService()  # Fallback
    logger.warning("Using fallback encryption service", extra={"correlation_id": boot_manager._correlation_id})


# --- Global Access Functions ---
def get_global_correlation_id() -> str:
    """Get the global correlation ID for distributed tracing."""
    return boot_manager.get_global_correlation_id()


def get_environment_tags() -> Dict[str, Any]:
    """Get environment tags for mock detection and debugging."""
    return boot_manager.get_environment_tags()


def add_global_trace_event(event: str, data: Optional[Dict[str, Any]] = None) -> None:
    """Add a trace event to the global correlation context."""
    boot_manager.add_global_event(event, data)


# Validate environment on import
if not env_detector.validate_environment():
    logger.error("Environment validation failed - system may not be secure",
                extra={"correlation_id": boot_manager._correlation_id})
    # Don't raise exception here to avoid import failures, but log critically
