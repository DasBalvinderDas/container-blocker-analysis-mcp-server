"""Tool for analyzing application code for containerization blockers."""

import json
from typing import Optional

from ..utils.code_extractor import (
    extract_from_code_block,
    extract_from_directory,
    extract_from_git_repo,
    extract_from_zip,
    format_files_for_analysis,
)

ALL_BLOCKER_TYPES = [
    "Hardcoded File Paths",
    "Local File System Dependencies",
    "Hardcoded Ports/IP Addresses",
    "Session State Management (Sticky Sessions)",
    "Environment-Specific Configurations",
    "Database Connection Handling",
    "Logging to Local Files",
    "Process-Level Dependencies",
    "OS-Specific System Calls",
    "Large Binary Dependencies",
    "Hardcoded Secrets/Credentials",
    "Shared Memory / IPC Dependencies",
    "Startup/Shutdown Scripts",
    "Host-Dependent Networking",
    "Persistent Local Storage Usage",
]


def analyze_code(
    source_type: str,
    source: str,
    language: Optional[str] = None,
    blocker_types: Optional[list[str]] = None,
    app_name: Optional[str] = None,
) -> dict:
    """Analyze application code for containerization blockers and migration issues.

    Extracts code from various sources (inline code, zip files, git repos, local directories),
    then returns the code content with a structured analysis prompt for evaluating
    containerization readiness. After calling this tool, evaluate the code using the
    returned analysis_prompt and then pass the structured JSON result to
    generate_html_report or generate_pdf_report to create a report.

    Args:
        source_type: Type of source to analyze. Must be one of:
            'code_block' for inline code,
            'zip_file' for a local zip file path,
            'git_repo' for a git repository URL,
            'local_directory' for a local folder path.
        source: The source to analyze. For code_block: the code itself.
            For zip_file: absolute path to the zip file.
            For git_repo: the repository URL.
            For local_directory: absolute path to the directory.
        language: Programming language hint (for code_block source type).
            E.g., 'python', 'java', 'javascript'. Optional.
        blocker_types: Specific blocker types to check. If not provided, all 15 common
            blockers are analyzed. Examples: 'Hardcoded File Paths',
            'Local File System Dependencies', 'Hardcoded Ports/IP Addresses'.
        app_name: Application name for the report. Defaults to 'Application'.

    Returns:
        A dictionary with extraction status, file metadata, and the analysis prompt
        for the LLM to execute.
    """
    try:
        if source_type == "code_block":
            files = extract_from_code_block(source, language)
        elif source_type == "zip_file":
            files = extract_from_zip(source)
        elif source_type == "git_repo":
            files = extract_from_git_repo(source)
        elif source_type == "local_directory":
            files = extract_from_directory(source)
        else:
            return {"status": "error", "message": f"Invalid source_type: {source_type}. Must be one of: code_block, zip_file, git_repo, local_directory"}

        if not files:
            return {"status": "error", "message": "No code files found in the provided source."}

        formatted_code = format_files_for_analysis(files)
        total_lines = sum(f.content.count("\n") + 1 for f in files)

        effective_blocker_types = blocker_types if blocker_types else ALL_BLOCKER_TYPES
        blocker_list = "\n".join(f"- {b}" for b in effective_blocker_types)
        effective_app_name = app_name or "Application"

        analysis_prompt = f"""You are an expert Enterprise Architect specializing in containerization and cloud-native migration.

Analyze the following application code to identify containerization blockers.

**Application:** {effective_app_name}

**Check for these specific blocker types:**
{blocker_list}

**Code to analyze:**
{formatted_code}

### Response Instructions:
Respond with ONLY a valid JSON object (no markdown, no code fences, no explanation text outside the JSON).

The JSON must follow this exact schema:
{{
  "issues": [
    {{
      "issue_name": "Name of the issue",
      "exists_or_not": "Yes" or "No",
      "issue_explanation": "2-3 line explanation of the issue found (or why it doesn't exist)",
      "impact_on_containerization": "Low", "Medium", or "High",
      "recommended_services": "Recommended cloud services or solutions to address this (e.g., GKE Secrets Manager, Cloud SQL Proxy, etc.)"
    }}
  ],
  "summary": "A brief overall assessment of the application's container-readiness"
}}

Include one entry per blocker type checked. Be thorough and specific - reference actual code patterns found."""

        return {
            "status": "success",
            "file_count": len(files),
            "total_lines": total_lines,
            "files_analyzed": [
                {
                    "path": f.relative_path,
                    "language": f.language,
                    "lines": f.content.count("\n") + 1,
                }
                for f in files
            ],
            "analysis_prompt": analysis_prompt,
            "instructions": (
                "Execute the analysis described in 'analysis_prompt' and return the JSON result. "
                "Then use 'generate_html_report' or 'generate_pdf_report' to create a report from the results."
            ),
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}
