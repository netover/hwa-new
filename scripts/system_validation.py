#!/usr/bin/env python3
"""
System Validation and Health Assessment Script

This script performs comprehensive validation of the Resync system including:
- Chaos Engineering tests
- Fuzzing campaigns
- Stress testing
- Health checks
- Security validation
- Performance benchmarking

Usage:
    python scripts/system_validation.py [--chaos-duration MINUTES] [--fuzz-duration SECONDS] [--stress-only] [--report-only]
"""

import argparse
import asyncio
import json
import logging
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from resync.core.chaos_engineering import run_chaos_engineering_suite, run_fuzzing_campaign
from resync.core.stress_testing import run_stress_testing_suite
from resync.core.metrics import runtime_metrics, get_correlation_context
from resync.core import get_global_correlation_id, get_environment_tags, get_boot_status


class SystemValidator:
    """Comprehensive system validation orchestrator."""

    def __init__(self):
        self.correlation_id = get_global_correlation_id()
        self.start_time = time.time()
        self.results = {}

    async def run_full_validation(self, chaos_duration: float = 3.0,
                                fuzz_duration: float = 30.0,
                                skip_chaos: bool = False,
                                skip_fuzzing: bool = False,
                                skip_stress: bool = False) -> Dict[str, Any]:
        """
        Run complete system validation suite.
        """
        correlation_id = runtime_metrics.create_correlation_id({
            "component": "system_validation",
            "operation": "full_validation",
            "chaos_duration": chaos_duration,
            "fuzz_duration": fuzz_duration,
            "skip_chaos": skip_chaos,
            "skip_fuzzing": skip_fuzzing,
            "skip_stress": skip_stress,
            "global_correlation": self.correlation_id
        })

        print("Starting Resync System Validation")
        print("=" * 50)

        try:
            # 1. System Health Check
            print("Phase 1: System Health Check")
            health_status = self._check_system_health()
            self.results["health_check"] = health_status
            print(f"    Health check completed: {health_status['overall_status']}")

            # 2. Chaos Engineering
            if not skip_chaos:
                print(f"\n Phase 2: Chaos Engineering ({chaos_duration}min)")
                chaos_results = await run_chaos_engineering_suite(chaos_duration)
                self.results["chaos_engineering"] = chaos_results
                success_rate = chaos_results['success_rate'] * 100
                print(f"    Chaos engineering completed: {success_rate:.1f}% success rate")
            else:
                print("     Chaos engineering skipped")

            # 3. Fuzzing Campaign
            if not skip_fuzzing:
                print(f"\n Phase 3: Fuzzing Campaign ({fuzz_duration}s)")
                fuzz_results = await run_fuzzing_campaign(fuzz_duration)
                self.results["fuzzing"] = fuzz_results
                success_rate = fuzz_results['success_rate'] * 100
                print(f"    Fuzzing campaign completed: {success_rate:.1f}% scenarios passed")
            else:
                print("     Fuzzing campaign skipped")

            # 4. Stress Testing
            if not skip_stress:
                print("\n Phase 4: Stress Testing")
                stress_results = await run_stress_testing_suite()
                self.results["stress_testing"] = stress_results
                total_ops = stress_results['total_operations']
                print(f"    Stress testing completed: {total_ops:.0f} operations")
            else:
                print("     Stress testing skipped")

            # 5. Generate Report
            print("\n Phase 5: Generating Validation Report")
            report = self._generate_validation_report()

            # Save detailed results
            self._save_results(report)

            duration = time.time() - self.start_time
            print(f" System validation completed successfully in {duration:.1f}s!")
            return report

        except Exception as e:
            print(f" System validation failed: {e}")
            logger.error("System validation failed", exc_info=True)
            return {"error": str(e), "correlation_id": correlation_id}

        finally:
            runtime_metrics.close_correlation_id(correlation_id)

    def _check_system_health(self) -> Dict[str, Any]:
        """Check overall system health with PRODUCTION READINESS validation."""
        try:
            correlation_id = runtime_metrics.create_correlation_id({
                "component": "system_validator",
                "operation": "health_check"
            })

            # PRODUCTION READINESS: Environment and security checks
            is_production = env_detector.is_production()
            security_level = env_detector.get_security_level()

            # Boot status
            boot_status = get_boot_status()

            # Environment check
            environment = get_environment_tags()

            health_status = {
                "overall_status": "unknown",
                "boot_status": boot_status,
                "environment": environment,
                "correlation_id": correlation_id.id,
                "production_ready": False,
                "production_issues": [],
                "component_health": {},
                "runtime_metrics": {},
                "timestamp": time.time()
            }

            # CRITICAL COMPONENTS FOR PRODUCTION - must all be healthy
            critical_components = [
                "async_cache",  # Core caching
                "audit_db",     # Audit logging
            ]

            # IMPORTANT COMPONENTS - should be healthy but allow graceful degradation
            important_components = [
                "agent_manager",      # AI agents
                "connection_manager",  # External connections
                "encryption_service"   # Security
            ]

            all_components = critical_components + important_components
            healthy_count = 0
            total_count = len(all_components)
            critical_failures = []
            production_blockers = []

            # Check component health with detailed validation
            health_issues = []
            for comp_name in all_components:
                try:
                    component = boot_manager.get_component(comp_name)
                    if hasattr(component, 'health_check'):
                        if asyncio.iscoroutinefunction(component.health_check):
                            health_result = asyncio.run(component.health_check())
                        else:
                            health_result = component.health_check()
                    else:
                        health_result = {
                            "status": "unknown",
                            "message": "No health check available",
                            "production_ready": False
                        }

                    # PRODUCTION READINESS: Check production_ready flag
                    component_production_ready = health_result.get("production_ready", False)
                    component_status = health_result.get("status", "unknown")

                    # Determine component health score
                    if component_status in ["healthy", "ok"] and component_production_ready:
                        healthy_count += 1
                        score = 1.0
                    elif component_status in ["healthy", "ok"]:
                        healthy_count += 0.8  # Good but not production ready
                        score = 0.8
                        if comp_name in critical_components:
                            production_blockers.append(f"{comp_name}: not production ready")
                    elif component_status == "warning":
                        healthy_count += 0.5  # Partial credit for warnings
                        score = 0.5
                        if comp_name in critical_components:
                            production_blockers.append(f"{comp_name}: warning status")
                    else:
                        score = 0.0
                        if comp_name in critical_components:
                            critical_failures.append(comp_name)
                            production_blockers.append(f"{comp_name}: {component_status}")

                    # Add score to component result
                    health_result["health_score"] = score
                    health_status["component_health"][comp_name] = health_result

                    if component_status not in ["healthy", "ok"]:
                        health_issues.append(f"{comp_name}: {health_result.get('message', component_status)}")

                except KeyError:
                    error_result = {
                        "status": "error",
                        "error": "Component not registered",
                        "production_ready": False,
                        "health_score": 0.0
                    }
                    health_status["component_health"][comp_name] = error_result
                    health_issues.append(f"{comp_name}: not registered")
                    if comp_name in critical_components:
                        critical_failures.append(comp_name)
                        production_blockers.append(f"{comp_name}: not registered")

                except Exception as e:
                    error_result = {
                        "status": "error",
                        "error": str(e),
                        "production_ready": False,
                        "health_score": 0.0
                    }
                    health_status["component_health"][comp_name] = error_result
                    health_issues.append(f"{comp_name}: {str(e)}")
                    if comp_name in critical_components:
                        critical_failures.append(comp_name)
                        production_blockers.append(f"{comp_name}: exception - {str(e)}")

            # Runtime metrics health
            metrics_snapshot = runtime_metrics.get_snapshot()
            cache_health = metrics_snapshot.get("cache", {})
            agent_health = metrics_snapshot.get("agent", {})
            audit_health = metrics_snapshot.get("audit", {})

            health_status["runtime_metrics"] = {
                "cache_hit_rate": cache_health.get("hit_rate", 0),
                "agent_success_rate": agent_health.get("agent_success_rate", 0),
                "audit_approval_rate": audit_health.get("approval_rate", 0)
            }

            # PRODUCTION READINESS VALIDATION
            health_percentage = (healthy_count / total_count) * 100 if total_count > 0 else 0
            has_critical_failures = len(critical_failures) > 0
            has_production_blockers = len(production_blockers) > 0

            # Determine overall status with production considerations
            if has_critical_failures:
                overall_status = "critical"
                production_ready = False
                health_status["production_issues"].extend([
                    f"CRITICAL FAILURE: {component}" for component in critical_failures
                ])
            elif has_production_blockers:
                overall_status = "warning"
                production_ready = not is_production  # Only allow in non-production
                health_status["production_issues"].extend([
                    f"PRODUCTION BLOCKER: {issue}" for issue in production_blockers
                ])
            elif health_percentage >= 95:
                overall_status = "excellent"
                production_ready = True
            elif health_percentage >= 85:
                overall_status = "healthy"
                production_ready = True
            elif health_percentage >= 70:
                overall_status = "degraded"
                production_ready = not is_production  # Degraded only acceptable in dev
            else:
                overall_status = "critical"
                production_ready = False

            # PRODUCTION-SPECIFIC VALIDATIONS
            if is_production:
                # In production, we need 100% health
                if health_percentage < 100:
                    production_ready = False
                    health_status["production_issues"].append(
                        f"PRODUCTION REQUIREMENT: 100% health required, got {health_percentage:.1f}%"
                    )

                # All critical components must be production_ready
                for comp_name in critical_components:
                    comp_health = health_status["component_health"].get(comp_name, {})
                    if not comp_health.get("production_ready", False):
                        production_ready = False
                        health_status["production_issues"].append(
                            f"PRODUCTION REQUIREMENT: {comp_name} not production ready"
                        )
            else:
                # In development, allow some degradation but never production ready
                production_ready = False

            # Final status assignment
            health_status.update({
                "overall_status": overall_status,
                "health_percentage": health_percentage,
                "healthy_components": healthy_count,
                "total_components": total_count,
                "health_issues": health_issues,
                "critical_failures": critical_failures,
                "production_ready": production_ready,
                "production_blockers": production_blockers,
                "is_production": is_production
            })

            # Log production readiness status
            if production_ready:
                log_with_correlation(logging.INFO,
                    f"System health check PASSED - Production Ready: {production_ready} ({health_percentage:.1f}%)",
                    correlation_id)
            else:
                log_with_correlation(logging.WARNING,
                    f"System health check FAILED - Production Ready: {production_ready} ({health_percentage:.1f}%)",
                    correlation_id)

            runtime_metrics.close_correlation_id(correlation_id)
            return health_status

        except Exception as e:
            return {
                "overall_status": "critical",
                "error": f"Health check system failure: {str(e)}",
                "correlation_id": "unknown",
                "production_ready": False,
                "production_issues": [f"SYSTEM FAILURE: {str(e)}"],
                "timestamp": time.time()
            }

    def _generate_validation_report(self) -> Dict[str, Any]:
        """Generate comprehensive validation report."""
        duration = time.time() - self.start_time

        # Calculate overall scores
        scores = self._calculate_validation_scores()

        report = {
            "validation_summary": {
                "correlation_id": self.correlation_id,
                "duration_seconds": duration,
                "timestamp": time.time(),
                "environment": get_environment_tags(),
                "overall_score": scores["overall"],
                "scores": scores
            },
            "test_results": self.results,
            "recommendations": self._generate_recommendations(scores),
            "system_info": {
                "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                "platform": sys.platform,
                "architecture": "64-bit" if sys.maxsize > 2**32 else "32-bit"
            }
        }

        return report

    def _calculate_validation_scores(self) -> Dict[str, Any]:
        """Calculate validation scores for different aspects."""
        scores = {
            "health": 0,
            "chaos_resilience": 0,
            "fuzzing_resilience": 0,
            "stress_resilience": 0,
            "overall": 0
        }

        # Health score
        if "health_check" in self.results:
            health = self.results["health_check"]
            if health.get("overall_status") == "healthy":
                scores["health"] = 100
            elif health.get("overall_status") == "degraded":
                scores["health"] = 70
            else:
                scores["health"] = 30

        # Chaos engineering score
        if "chaos_engineering" in self.results:
            chaos = self.results["chaos_engineering"]
            success_rate = chaos.get("success_rate", 0)
            scores["chaos_resilience"] = int(success_rate * 100)

        # Fuzzing score
        if "fuzzing" in self.results:
            fuzz = self.results["fuzzing"]
            success_rate = fuzz.get("success_rate", 0)
            scores["fuzzing_resilience"] = int(success_rate * 100)

        # Stress testing score
        if "stress_testing" in self.results:
            stress = self.results["stress_testing"]
            error_rate = stress.get("overall_error_rate", 1)
            # Invert error rate for score (lower errors = higher score)
            scores["stress_resilience"] = int((1 - min(error_rate, 1)) * 100)

        # Overall score (weighted average)
        weights = {"health": 0.3, "chaos_resilience": 0.25, "fuzzing_resilience": 0.25, "stress_resilience": 0.2}
        scores["overall"] = int(sum(scores[aspect] * weights[aspect] for aspect in weights.keys()))

        return scores

    def _generate_recommendations(self, scores: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on validation scores."""
        recommendations = []

        if scores["health"] < 80:
            recommendations.append(" CRITICAL: System health is degraded. Check component initialization and dependencies.")

        if scores["chaos_resilience"] < 70:
            recommendations.append(" HIGH: System shows vulnerabilities under chaos conditions. Implement better error handling and circuit breakers.")

        if scores["fuzzing_resilience"] < 80:
            recommendations.append(" MEDIUM: Fuzzing tests reveal input validation issues. Strengthen input sanitization and bounds checking.")

        if scores["stress_resilience"] < 70:
            recommendations.append(" HIGH: System performance degrades under load. Consider optimizing concurrent operations and resource usage.")

        if scores["overall"] >= 90:
            recommendations.append(" EXCELLENT: System shows high resilience and performance. Continue monitoring and maintenance.")
        elif scores["overall"] >= 80:
            recommendations.append(" GOOD: System is generally healthy but has room for improvement in some areas.")
        elif scores["overall"] >= 70:
            recommendations.append(" FAIR: System needs attention in multiple areas. Address high-priority issues.")
        else:
            recommendations.append(" POOR: System requires immediate attention. Multiple critical issues detected.")

        # Specific technical recommendations
        if any(score < 60 for score in [scores["chaos_resilience"], scores["stress_resilience"]]):
            recommendations.append(" Consider implementing rate limiting and request queuing for high-load scenarios.")

        if scores["fuzzing_resilience"] < 80:
            recommendations.append(" Enhance input validation with comprehensive schema validation and sanitization.")

        return recommendations

    def _save_results(self, report: Dict[str, Any]):
        """Save validation results to file."""
        try:
            reports_dir = Path("reports")
            reports_dir.mkdir(exist_ok=True)

            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"system_validation_report_{timestamp}.json"

            with open(reports_dir / filename, 'w') as f:
                json.dump(report, f, indent=2, default=str)

            print(f" Detailed report saved to: reports/{filename}")

            # Also save summary to console
            scores = report["validation_summary"]["scores"]
            print("\n Validation Scores:")
            print(f"   Health: {scores['health']}/100")
            print(f"   Chaos Resilience: {scores['chaos_resilience']}/100")
            print(f"   Fuzzing Resilience: {scores['fuzzing_resilience']}/100")
            print(f"   Stress Resilience: {scores['stress_resilience']}/100")
            print(f"   Overall Score: {scores['overall']}/100")

            print("\n Recommendations:")
            for rec in report["recommendations"]:
                print(f"   {rec}")

        except Exception as e:
            print(f"  Failed to save report: {e}")


async def main():
    """Main validation script entry point."""
    parser = argparse.ArgumentParser(description="Resync System Validation")
    parser.add_argument("--chaos-duration", type=float, default=3.0,
                       help="Duration of chaos engineering tests in minutes")
    parser.add_argument("--fuzz-duration", type=float, default=30.0,
                       help="Duration of fuzzing campaign in seconds")
    parser.add_argument("--skip-chaos", action="store_true",
                       help="Skip chaos engineering tests")
    parser.add_argument("--skip-fuzzing", action="store_true",
                       help="Skip fuzzing campaign")
    parser.add_argument("--skip-stress", action="store_true",
                       help="Skip stress testing")
    parser.add_argument("--report-only", action="store_true",
                       help="Only generate health report without running tests")

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Initialize validator
    validator = SystemValidator()

    try:
        if args.report_only:
            print(" Generating system health report only...")
            report = {"health_check": validator._check_system_health()}
            validator.results = report
            final_report = validator._generate_validation_report()
            validator._save_results(final_report)
        else:
            final_report = await validator.run_full_validation(
                chaos_duration=args.chaos_duration,
                fuzz_duration=args.fuzz_duration,
                skip_chaos=args.skip_chaos,
                skip_fuzzing=args.skip_fuzzing,
                skip_stress=args.skip_stress
            )

        return 0 if final_report.get("validation_summary", {}).get("overall_score", 0) >= 70 else 1

    except KeyboardInterrupt:
        print("\n  Validation interrupted by user")
        return 130
    except Exception as e:
        print(f" Validation failed with error: {e}")
        logger.error("Validation script failed", exc_info=True)
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
