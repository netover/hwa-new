"""
Compliance Report Generation Strategies.

This module implements the Strategy pattern for generating different parts of the SOC 2 compliance report.
Each strategy is responsible for a specific component of the report, making the code more modular,
testable, and maintainable.
"""

from typing import Dict, Any
from collections import defaultdict
from enum import Enum

from resync.core.soc2_compliance_refactored import SOC2ComplianceManager, SOC2TrustServiceCriteria


class ReportStrategy:
    """Base interface for report generation strategies."""
    
    def execute(self, manager: SOC2ComplianceManager) -> Dict[str, Any]:
        """Execute the strategy and return the report component."""
        raise NotImplementedError("Subclasses must implement execute method")


class ControlComplianceStrategy(ReportStrategy):
    """Strategy for calculating control compliance."""
    
    def execute(self, manager: SOC2ComplianceManager) -> Dict[str, Any]:
        """Calculate control compliance statistics."""
        total_controls = len(manager.controls)
        compliant_controls = sum(1 for c in manager.controls.values() if c.is_compliant())
        
        return {
            "total_controls": total_controls,
            "compliant_controls": compliant_controls,
            "compliance_rate": compliant_controls / max(1, total_controls)
        }


class CriteriaScoresStrategy(ReportStrategy):
    """Strategy for calculating criteria scores."""
    
    def execute(self, manager: SOC2ComplianceManager) -> Dict[str, Any]:
        """Calculate scores for each SOC 2 trust service criteria."""
        criteria_compliance = defaultdict(lambda: {"total": 0, "compliant": 0})
        
        for control in manager.controls.values():
            for criterion in control.criteria:
                criteria_compliance[criterion]["total"] += 1
                if control.is_compliant():
                    criteria_compliance[criterion]["compliant"] += 1
        
        criteria_scores = {}
        for criterion, scores in criteria_compliance.items():
            score = scores["compliant"] / max(1, scores["total"])
            criteria_scores[criterion.value] = {
                "score": score,
                "compliant_controls": scores["compliant"],
                "total_controls": scores["total"],
            }
        
        return criteria_scores


class OverallComplianceStrategy(ReportStrategy):
    """Strategy for calculating overall compliance score."""
    
    def execute(self, manager: SOC2ComplianceManager) -> float:
        """Calculate weighted average overall compliance score."""
        criteria_scores = CriteriaScoresStrategy().execute(manager)
        
        weights = {
            SOC2TrustServiceCriteria.SECURITY: 0.3,
            SOC2TrustServiceCriteria.AVAILABILITY: 0.25,
            SOC2TrustServiceCriteria.PROCESSING_INTEGRITY: 0.2,
            SOC2TrustServiceCriteria.CONFIDENTIALITY: 0.15,
            SOC2TrustServiceCriteria.PRIVACY: 0.1,
        }
        
        weighted_score = 0.0
        total_weight = 0.0
        for criterion, weight in weights.items():
            if criterion.value in criteria_scores:
                weighted_score += criteria_scores[criterion.value]["score"] * weight
                total_weight += weight
        
        return weighted_score / max(0.01, total_weight)


class ControlStatusSummaryStrategy(ReportStrategy):
    """Strategy for generating control status summary."""
    
    def execute(self, manager: SOC2ComplianceManager) -> Dict[str, int]:
        """Generate summary of control status counts."""
        status_counts = defaultdict(int)
        for control in manager.controls.values():
            status_counts[control.status.value] += 1
        
        return dict(status_counts)


class EvidenceSummaryStrategy(ReportStrategy):
    """Strategy for generating evidence summary."""
    
    def execute(self, manager: SOC2ComplianceManager) -> Dict[str, Any]:
        """Generate summary of valid evidence."""
        evidence_counts = defaultdict(int)
        for evidence in manager.evidence.values():
            if evidence.is_valid():
                evidence_counts[evidence.evidence_type] += 1
        
        return {
            "total_valid_evidence": sum(evidence_counts.values()),
            "by_type": dict(evidence_counts),
        }


class AvailabilitySummaryStrategy(ReportStrategy):
    """Strategy for generating availability summary."""
    
    def execute(self, manager: SOC2ComplianceManager) -> Dict[str, Any]:
        """Generate summary of availability metrics."""
        if not manager.availability_metrics:
            return {}
        
        avg_availability = sum(
            m.availability_score for m in manager.availability_metrics
        ) / len(manager.availability_metrics)
        total_downtime = sum(
            m.total_downtime_seconds for m in manager.availability_metrics
        )
        
        return {
            "average_availability": avg_availability,
            "total_downtime_seconds": total_downtime,
            "target_availability": manager.config.target_availability_percentage,
            "meets_target": avg_availability >= manager.config.target_availability_percentage,
        }


class ProcessingIntegritySummaryStrategy(ReportStrategy):
    """Strategy for generating processing integrity summary."""
    
    def execute(self, manager: SOC2ComplianceManager) -> Dict[str, Any]:
        """Generate summary of processing integrity metrics."""
        if not manager.processing_checks:
            return {}
        
        avg_integrity = sum(
            c.integrity_score for c in manager.processing_checks
        ) / len(manager.processing_checks)
        failed_checks = sum(1 for c in manager.processing_checks if not c.is_valid)
        
        return {
            "average_integrity_score": avg_integrity,
            "failed_checks": failed_checks,
            "total_checks": len(manager.processing_checks),
            "integrity_target": 99.9,
            "meets_target": avg_integrity >= 99.9,
        }


class ConfidentialityIncidentsSummaryStrategy(ReportStrategy):
    """Strategy for generating confidentiality incidents summary."""
    
    def execute(self, manager: SOC2ComplianceManager) -> Dict[str, Any]:
        """Generate summary of confidentiality incidents."""
        incident_counts = defaultdict(int)
        for incident in manager.confidentiality_incidents:
            incident_counts[incident.severity] += 1
        
        return {
            "total_incidents": len(manager.confidentiality_incidents),
            "by_severity": dict(incident_counts),
            "unresolved_incidents": sum(
                1 for i in manager.confidentiality_incidents if not i.resolved
            ),
        }


class RecommendationsStrategy(ReportStrategy):
    """Strategy for generating recommendations."""

    def execute(self, manager: SOC2ComplianceManager, report: Dict[str, Any] = None) -> list:
        """Generate recommendations based on compliance report."""
        # Reuse the existing _generate_recommendations method
        # If report is provided, use it; otherwise create a basic structure
        if report is None:
            report = {"overall_compliance_score": 0.0}
        return manager._generate_recommendations(report)


class ReportGenerator:
    """Facade for generating complete compliance reports using strategies."""
    
    def __init__(self):
        self.strategies = {
            "control_compliance": ControlComplianceStrategy(),
            "criteria_scores": CriteriaScoresStrategy(),
            "overall_compliance": OverallComplianceStrategy(),
            "control_status": ControlStatusSummaryStrategy(),
            "evidence_summary": EvidenceSummaryStrategy(),
            "availability_summary": AvailabilitySummaryStrategy(),
            "processing_integrity_summary": ProcessingIntegritySummaryStrategy(),
            "confidentiality_incidents": ConfidentialityIncidentsSummaryStrategy(),
            "recommendations": RecommendationsStrategy(),
        }
    
    def generate_report(self, manager: SOC2ComplianceManager) -> Dict[str, Any]:
        """Generate a complete compliance report using all strategies."""
        report = {
            "generated_at": manager._get_current_timestamp(),
            "period_start": manager._get_period_start(),
            "period_end": manager._get_period_end(),
            "overall_compliance_score": 0.0,
            "criteria_scores": {},
            "control_status": {},
            "evidence_summary": {},
            "availability_summary": {},
            "processing_integrity_summary": {},
            "confidentiality_incidents": {},
            "recommendations": [],
        }
        
        # Execute each strategy
        report["control_compliance"] = self.strategies["control_compliance"].execute(manager)
        report["criteria_scores"] = self.strategies["criteria_scores"].execute(manager)
        report["overall_compliance_score"] = self.strategies["overall_compliance"].execute(manager)
        report["control_status"] = self.strategies["control_status"].execute(manager)
        report["evidence_summary"] = self.strategies["evidence_summary"].execute(manager)
        report["availability_summary"] = self.strategies["availability_summary"].execute(manager)
        report["processing_integrity_summary"] = self.strategies["processing_integrity_summary"].execute(manager)
        report["confidentiality_incidents"] = self.strategies["confidentiality_incidents"].execute(manager)
        report["recommendations"] = self.strategies["recommendations"].execute(manager)
        
        return report
