"""
SOC 2 Type II Compliance Management System.

This module provides comprehensive SOC 2 Type II readiness including:
- Automated security controls validation
- Availability monitoring and reporting
- Processing integrity verification
- Confidentiality controls enforcement
- Privacy framework implementation
- Evidence collection and audit trails
- Compliance reporting and dashboards
- Change management and configuration controls
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from resync.core.structured_logger import get_logger

logger = get_logger(__name__)

# Import the refactored version
from .soc2_compliance_refactored import (
    SOC2ComplianceManager as SOC2ComplianceManagerRefactored,
    soc2_compliance_manager as soc2_compliance_manager_refactored,
    get_soc2_compliance_manager as get_soc2_compliance_manager_refactored
)

# Deprecation warning
import warnings

class DeprecatedSOC2ComplianceManager(SOC2ComplianceManagerRefactored):
    """
    DEPRECATED: Use SOC2ComplianceManagerRefactored instead.
    
    This class is maintained for backward compatibility but will be removed in a future version.
    All new code should use the refactored version in soc2_compliance_refactored.py.
    """
    
    def __init__(self, config: Optional[SOC2ComplianceConfig] = None):
        warnings.warn(
            "DeprecatedSOC2ComplianceManager is deprecated. Use SOC2ComplianceManagerRefactored instead.",
            DeprecationWarning,
            stacklevel=2
        )
        super().__init__(config)

# Create backward compatible aliases
SOC2ComplianceManager = DeprecatedSOC2ComplianceManager
soc2_compliance_manager = soc2_compliance_manager_refactored
global_soc2_compliance_manager = soc2_compliance_manager_refactored
get_soc2_compliance_manager = get_soc2_compliance_manager_refactored

# Keep the original classes for backward compatibility
# (These are imported from the refactored module)
SOC2TrustServiceCriteria = SOC2ComplianceManagerRefactored.SOC2TrustServiceCriteria
ControlCategory = SOC2ComplianceManagerRefactored.ControlCategory
ControlStatus = SOC2ComplianceManagerRefactored.ControlStatus
SOC2Control = SOC2ComplianceManagerRefactored.SOC2Control
SOC2Evidence = SOC2ComplianceManagerRefactored.SOC2Evidence
AvailabilityMetric = SOC2ComplianceManagerRefactored.AvailabilityMetric
ProcessingIntegrityCheck = SOC2ComplianceManagerRefactored.ProcessingIntegrityCheck
ConfidentialityIncident = SOC2ComplianceManagerRefactored.ConfidentialityIncident
SOC2ComplianceConfig = SOC2ComplianceManagerRefactored.SOC2ComplianceConfig

# Remove the original implementation details to avoid confusion
# The actual implementation is now in soc2_compliance_refactored.py"
