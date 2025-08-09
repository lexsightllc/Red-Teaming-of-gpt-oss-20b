import logging
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
import hashlib

class PublicSummaryGenerator:
    """
    Generates a public-facing summary report of findings with appropriate redaction.
    Implements Point 49: Writing Public-Facing Summary Conveying Urgency Without Exaggeration
    """
    def __init__(self, findings: List[Dict[str, Any]], output_path: str, run_metadata: Optional[Dict[str, Any]] = None):
        """
        Initialize the PublicSummaryGenerator with findings and output configuration.
        
        Args:
            findings: List of vulnerability findings to include in the summary
            output_path: Path where the summary file will be saved
            run_metadata: Optional metadata about the run (start time, end time, etc.)
        """
        self.findings = findings
        self.output_path = output_path
        self.run_metadata = run_metadata or {}
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Initialized PublicSummaryGenerator. Will save summary to: {output_path}")

    def _redact_sensitive_info(self, text: str) -> str:
        """Redact potentially sensitive information from text."""
        if not text or not isinstance(text, str):
            return "[REDACTED]"
        
        # Simple redaction - in a real implementation, this would be more sophisticated
        if any(sensitive in text.lower() for sensitive in ["api", "key", "password", "token"]):
            return "[REDACTED: SENSITIVE_INFORMATION]"
        return text

    def _generate_finding_summary(self, finding: Dict[str, Any]) -> str:
        """Generate a formatted summary for a single finding."""
        summary = f"### {finding.get('vulnerability_type', 'Unknown Vulnerability Type')} (ID: {finding.get('finding_id', 'N/A')})\n"
        
        # Basic info
        summary += f"- **Severity Score:** {finding.get('severity_score', 'N/A')}/10\n"
        summary += f"- **Reproduction Status:** {finding.get('reproduction_status', 'unknown').capitalize()}\n"
        
        # Component scores
        if all(k in finding for k in ['exploitability_score', 'impact_score', 'generality_score', 'detectability_score']):
            summary += "- **Component Scores:**\n"
            summary += f"  - Exploitability: {finding['exploitability_score']}/10\n"
            summary += f"  - Impact: {finding['impact_score']}/10\n"
            summary += f"  - Generality: {finding['generality_score']}/10\n"
            summary += f"  - Detectability: {finding['detectability_score']}/10\n"
        
        # Redacted details
        summary += f"- **Model Version:** {self._redact_sensitive_info(finding.get('model_version_tested', 'N/A'))}\n"
        # Timestamp
        if 'timestamp_found' in finding:
            try:
                ts = datetime.fromisoformat(finding['timestamp_found'].replace('Z', '+00:00'))
                summary += f"- **Detected:** {ts.strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
                # Calculate time since detection
                delta = datetime.now(ts.tzinfo) - ts
                if delta.days > 0:
                    summary += f"  - *{delta.days} days since detection*\n"
            except (ValueError, TypeError):
                summary += f"- **Detected:** {finding['timestamp_found']}\n"
        # Add reproduction info if available
        if 'reproduction_instructions' in finding and finding['reproduction_instructions']:
            summary += f"- **Reproduction:** {self._redact_sensitive_info(finding['reproduction_instructions'])}\n"
        # Add mitigation if available
        if 'mitigation_recommendations' in finding and finding['mitigation_recommendations']:
            summary += f"- **Mitigation:** {finding['mitigation_recommendations']}\n"
        # Add any notes
        if 'notes' in finding and finding['notes']:
            summary += f"- **Notes:** {self._redact_sensitive_info(finding['notes'])}\n"
        # Add metadata hashes for verification
        if all(k in finding for k in ['environment_hash', 'rng_seed']):
            summary += "\n*Verification hashes:*\n"
            summary += f"- Environment: `{finding['environment_hash']}`\n"
            if finding.get('input_data_hash') and finding['input_data_hash'] != 'N/A':
                summary += f"- Input data: `{finding['input_data_hash']}`\n"
            summary += f"- RNG Seed: `{finding['rng_seed']}`\n"
        summary += "\n---\n\n"
        return summary

    def generate_summary(self, output_filepath: str, environment_hash: str = "N/A", global_seed: int = 42) -> None:
        """
        Generates a comprehensive Markdown summary of findings.
        
        Args:
            output_filepath: Path to save the summary markdown file
            environment_hash: Hash of the execution environment for reproducibility
            global_seed: The RNG seed used for this run
        """
        self.logger.info(f"Generating public summary to {output_filepath}")
        
        # Generate report timestamp
        report_time = datetime.utcnow()
        timestamp = report_time.strftime("%Y-%m-%d %H:%M:%S UTC")
        
        # Start building the report
        summary_content = "# AI Model Red-Teaming Analysis Report\n\n"
        
        # Report metadata
        summary_content += "## Report Metadata\n"
        summary_content += f"- **Generated:** {timestamp}\n"
        # Include run metadata if available
        if self.run_metadata:
            if 'start_time' in self.run_metadata:
                try:
                    start_dt = datetime.fromisoformat(self.run_metadata['start_time'].replace('Z', '+00:00'))
                    summary_content += f"- **Analysis Started:** {start_dt.strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
                    # Calculate duration if end time is available
                    if 'end_time' in self.run_metadata:
                        try:
                            end_dt = datetime.fromisoformat(self.run_metadata['end_time'].replace('Z', '+00:00'))
                            duration = end_dt - start_dt
                            summary_content += f"- **Duration:** {str(duration).split('.')[0]}\n"
                        except (ValueError, TypeError):
                            pass
                except (ValueError, TypeError):
                    pass
            

        summary_content += f"- **Environment Hash:** `{environment_hash}`\n"
        summary_content += f"- **Global RNG Seed:** `{global_seed}`\n"
        summary_content += f"- **Findings Count:** {len(self.findings)}\n\n"
        
        if not self.findings:
            summary_content += "## Summary\n\n"
            summary_content += "No critical vulnerabilities were identified in this analysis run.\n\n"
            summary_content += "## Next Steps\n\n"
            summary_content += ("While no critical issues were found, we recommend ongoing monitoring "
                              "and testing as models and threat landscapes evolve. Consider expanding "
                              "test coverage or adjusting detection sensitivity if appropriate.\n\n")
        else:
            # Executive Summary
            summary_content += "## Executive Summary\n\n"
            
            # Count by severity
            severity_counts = {}
            for f in self.findings:
                severity = f.get('severity_score', 0)
                if not isinstance(severity, (int, float)):
                    severity = 0
                # Categories: Low (0-2.9), Medium (3-5.9), High (6-8.9), Critical (9-10)
                if severity >= 9:
                    level_name = "Critical"
                elif severity >= 6:
                    level_name = "High"
                elif severity >= 3:
                    level_name = "Medium"
                else:
                    level_name = "Low"
                severity_counts[level_name] = severity_counts.get(level_name, 0) + 1
            
            summary_content += f"Found {len(self.findings)} potential vulnerabilities:\n"
            # Print in order of severity
            for level in ["Critical", "High", "Medium", "Low"]:
                if level in severity_counts:
                    summary_content += f"- **{level}**: {severity_counts[level]}\n"
            # Top findings - ensure we have at least one finding with a valid severity score
            valid_findings = [f for f in self.findings if isinstance(f.get('severity_score'), (int, float))]
            
            if valid_findings:
                top_findings = sorted(
                    valid_findings,
                    key=lambda x: x['severity_score'],
                    reverse=True
                )[:3]  # Top 3 findings
                
                summary_content += "\n**Most Severe Findings:**\n"
                for i, finding in enumerate(top_findings, 1):
                    vuln_type = finding.get('vulnerability_type', 'Unknown')
                    score = finding.get('severity_score', 0)
                    summary_content += f"{i}. {vuln_type} (Severity: {score:.1f}/10)\n"
            
            # Detailed Findings
            summary_content += "\n## Detailed Findings\n\n"
            
            # Group by vulnerability type
            findings_by_type = {}
            for finding in self.findings:
                vuln_type = finding.get('vulnerability_type', 'Uncategorized')
                if vuln_type not in findings_by_type:
                    findings_by_type[vuln_type] = []
                findings_by_type[vuln_type].append(finding)
            
            # Add findings by type
            for vuln_type, type_findings in findings_by_type.items():
                summary_content += f"### {vuln_type} ({len(type_findings)} finding{'s' if len(type_findings) > 1 else ''})\n\n"
                for finding in type_findings:
                    summary_content += self._generate_finding_summary(finding)
            
            # Add disclaimer
            summary_content += "## Disclaimer\n\n"
            
            summary_content += (
                "This report is provided for research and safety improvement purposes only. "
                "The reproduction of harmful behaviors should only be performed in controlled environments "
                "with appropriate safeguards in place. The findings represent a snapshot of model behavior "
                f"at the time of testing ({timestamp}) and may not reflect current model capabilities.\n\n"
                "For questions or concerns, please contact the research team.\n"
            )
        
        # Write the report
        try:
            with open(output_filepath, 'w', encoding='utf-8') as f:
                f.write(summary_content)
            self.logger.info(f"Successfully generated public summary at {output_filepath}")
        except Exception as e:
            self.logger.error(f"Failed to write public summary to {output_filepath}: {e}")
            raise
