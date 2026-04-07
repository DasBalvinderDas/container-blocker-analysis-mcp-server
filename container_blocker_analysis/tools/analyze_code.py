"""Tool for analyzing application code for containerization blockers."""

from typing import Optional

from ..utils.code_extractor import (
    extract_from_code_block,
    extract_from_directory,
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

    Extracts code from various sources (inline code, zip files, local directories),
    then returns the code content with a structured analysis prompt for evaluating
    containerization readiness. After calling this tool, evaluate the code using the
    returned analysis_prompt and then pass the structured JSON result to
    generate_html_report or generate_pdf_report to create a report.

    For git repositories: Do NOT use this tool directly. Instead, use the Git MCP
    server tools to clone/fetch the repository first, then call this tool with
    source_type='local_directory' pointing to the cloned repo path.

    Args:
        source_type: Type of source to analyze. Must be one of:
            'code_block' for inline code,
            'zip_file' for a local zip file path,
            'git_repo' for a git repository URL (requires Git MCP server - see instructions),
            'local_directory' for a local folder path.
        source: The source to analyze. For code_block: the code itself.
            For zip_file: absolute path to the zip file.
            For git_repo: the repository URL (will return MCP server instructions).
            For local_directory: absolute path to the directory.
        language: Programming language hint (for code_block source type).
            E.g., 'python', 'java', 'javascript'. Optional.
        blocker_types: Specific blocker types to check. If not provided, all 15 common
            blockers are analyzed. Examples: 'Hardcoded File Paths',
            'Local File System Dependencies', 'Hardcoded Ports/IP Addresses'.
        app_name: Application name for the report. Defaults to 'Application'.

    Returns:
        A dictionary with extraction status, file metadata, and the analysis prompt
        for the LLM to execute. For git_repo source_type, returns instructions to
        use the Git MCP server tools instead.
    """
    try:
        # For git repos, delegate to Git MCP server
        if source_type == "git_repo":
            return {
                "status": "requires_git_mcp",
                "repo_url": source,
                "app_name": app_name or _derive_app_name_from_url(source),
                "blocker_types": blocker_types,
                "instructions": (
                    f"To analyze the git repository '{source}', follow these steps:\n"
                    "1. Use the Git MCP server to fetch the repository contents. You can:\n"
                    "   a. Use 'git_clone' to clone the repo to a local directory, OR\n"
                    "   b. Use 'get_file_contents' to browse and fetch files from the repo directly\n"
                    "2. Once you have the code locally, call 'analyze_code' again with:\n"
                    "   - source_type='local_directory'\n"
                    "   - source=<path to cloned repo>\n"
                    f"   - app_name='{app_name or _derive_app_name_from_url(source)}'\n"
                    "   OR if you fetched individual files, call with:\n"
                    "   - source_type='code_block'\n"
                    "   - source=<combined file contents>\n"
                    "\n"
                    "The Git MCP server handles all git operations (clone, fetch, browse).\n"
                    "No git commands are run directly from this tool."
                ),
            }

        if source_type == "code_block":
            files = extract_from_code_block(source, language)
        elif source_type == "zip_file":
            files = extract_from_zip(source)
        elif source_type == "local_directory":
            files = extract_from_directory(source)
        else:
            return {
                "status": "error",
                "message": (
                    f"Invalid source_type: {source_type}. "
                    "Must be one of: code_block, zip_file, git_repo, local_directory"
                ),
            }

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


def _derive_app_name_from_url(url: str) -> str:
    """Derive an application name from a git repository URL."""
    # https://github.com/user/repo.git -> repo
    name = url.rstrip("/").split("/")[-1]
    if name.endswith(".git"):
        name = name[:-4]
    return name
