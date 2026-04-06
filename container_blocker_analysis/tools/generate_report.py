"""Tools for generating HTML and PDF reports from containerization analysis results."""

import json
import os
from typing import Optional

from ..utils.report_generator import (
    AnalysisResult,
    ContainerizationIssue,
    generate_analysis_html,
    generate_analysis_pdf,
    generate_solution_html as _generate_solution_html,
)


def _parse_issues(issues_json: str) -> list[ContainerizationIssue]:
    """Parse issues from a JSON string into ContainerizationIssue objects."""
    if isinstance(issues_json, list):
        issues_list = issues_json
    else:
        issues_list = json.loads(issues_json)

    return [
        ContainerizationIssue(
            issue_name=i["issue_name"],
            exists_or_not=i["exists_or_not"],
            issue_explanation=i["issue_explanation"],
            impact_on_containerization=i["impact_on_containerization"],
            recommended_services=i["recommended_services"],
        )
        for i in issues_list
    ]


def generate_html_report(
    app_name: str,
    issues: list[dict],
    blocker_type: Optional[str] = None,
    summary: Optional[str] = None,
    output_path: Optional[str] = None,
) -> str:
    """Generate a styled HTML report from containerization blocker analysis results.

    Takes the structured issues array and produces a professional HTML report with
    summary statistics, color-coded impact levels, and a detailed issues table.
    Can save to a file or return HTML content directly.

    Args:
        app_name: Application name for the report header.
        issues: Array of containerization issues found during analysis. Each issue must
            be a dict with keys: issue_name (str), exists_or_not ("Yes" or "No"),
            issue_explanation (str), impact_on_containerization ("Low", "Medium", or "High"),
            recommended_services (str).
        blocker_type: Specific blocker type that was analyzed. Optional.
        summary: Overall summary of the analysis. Optional.
        output_path: File path to save the HTML report. If not provided,
            returns HTML content directly.

    Returns:
        If output_path is provided: a confirmation message with the file path.
        If output_path is not provided: the full HTML content as a string.
    """
    try:
        parsed_issues = _parse_issues(issues)
        result = AnalysisResult(
            app_name=app_name,
            issues=parsed_issues,
            blocker_type=blocker_type,
            summary=summary,
        )
        html = generate_analysis_html(result)

        if output_path:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(html)
            return f"HTML report saved to: {output_path}"

        return html

    except Exception as e:
        return f"Error generating HTML report: {e}"


def generate_pdf_report(
    app_name: str,
    issues: list[dict],
    blocker_type: Optional[str] = None,
    summary: Optional[str] = None,
    output_path: Optional[str] = None,
) -> str:
    """Generate a PDF report from containerization blocker analysis results.

    Takes the structured issues array and produces a professional PDF report with
    a structured table layout, color-coded impact levels, and summary statistics.

    Args:
        app_name: Application name for the report header.
        issues: Array of containerization issues found during analysis. Each issue must
            be a dict with keys: issue_name (str), exists_or_not ("Yes" or "No"),
            issue_explanation (str), impact_on_containerization ("Low", "Medium", or "High"),
            recommended_services (str).
        blocker_type: Specific blocker type that was analyzed. Optional.
        summary: Overall summary of the analysis. Optional.
        output_path: File path to save the PDF report. If not provided,
            saves to a temp directory and returns the path.

    Returns:
        A confirmation message with the file path where the PDF was saved.
    """
    try:
        parsed_issues = _parse_issues(issues)
        result = AnalysisResult(
            app_name=app_name,
            issues=parsed_issues,
            blocker_type=blocker_type,
            summary=summary,
        )
        pdf_bytes = generate_analysis_pdf(result)

        if not output_path:
            import tempfile
            output_path = os.path.join(
                tempfile.gettempdir(), f"container-analysis-{app_name}.pdf"
            )

        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(pdf_bytes)

        return f"PDF report saved to: {output_path}"

    except Exception as e:
        return f"Error generating PDF report: {e}"


def generate_solution_report(
    app_name: str,
    blocker_type: str,
    solution_content: str,
    output_path: Optional[str] = None,
) -> str:
    """Generate a styled HTML solution report for a specific containerization blocker.

    Takes the blocker type and solution content (in HTML format) and wraps it in a
    professional, styled document. Use after analyzing a blocker to provide actionable
    remediation steps including code changes, dependencies, and effort estimation.

    Args:
        app_name: Application name for the report header.
        blocker_type: The specific blocker type being solved (e.g., 'Hardcoded File Paths').
        solution_content: The solution content in HTML format. Can include h2, p, ul, li,
            pre, and code tags for structured formatting.
        output_path: File path to save the HTML report. If not provided,
            returns HTML content directly.

    Returns:
        If output_path is provided: a confirmation message with the file path.
        If output_path is not provided: the full HTML content as a string.
    """
    try:
        html = _generate_solution_html(app_name, blocker_type, solution_content)

        if output_path:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(html)
            return f"Solution HTML report saved to: {output_path}"

        return html

    except Exception as e:
        return f"Error generating solution report: {e}"
