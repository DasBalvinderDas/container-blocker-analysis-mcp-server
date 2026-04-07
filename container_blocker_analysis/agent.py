"""Container Blocker Analysis Agent - Google ADK Agent Definition.

This agent analyzes application code for containerization blockers and
generates professional HTML/PDF reports to assist with container migration.

All git operations are handled via the Git MCP server (no git commands in code).

Skills (workflows) available:
- full-analysis: Complete end-to-end analysis with HTML + PDF reports
- blocker-report: Targeted analysis for specific blocker types
- solution-generator: Generate remediation steps for found blockers
- quick-scan: Fast summary without generating report files
"""

import os
import pathlib

from google.adk.agents import Agent
from google.adk.skills import load_skill_from_dir
from google.adk.tools.mcp_tool import MCPToolset, StreamableHTTPConnectionParams
from google.adk.tools.skill_toolset import SkillToolset

from .tools.analyze_code import analyze_code
from .tools.generate_report import (
    generate_html_report,
    generate_pdf_report,
    generate_solution_report,
)

AGENT_MODEL = os.getenv("AGENT_MODEL", "gemini-2.5-flash")

# ---------- Git MCP Server Configuration ----------
# Uses GitHub Copilot MCP endpoint (StreamableHTTP).
# Set GITHUB_TOKEN env var with your GitHub personal access token.

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")

# Only the git tools we need for code analysis
GIT_MCP_TOOL_FILTER = [
    "get_repository",
    "get_file_contents",
    "list_pull_requests",
    "get_pull_request",
    "get_issue",
    "list_issues",
    "search_code",
    "create_branch",
    "create_or_update_file",
    "push_files",
]

_git_mcp_toolset = None
if GITHUB_TOKEN:
    _git_mcp_toolset = MCPToolset(
        connection_params=StreamableHTTPConnectionParams(
            url="https://api.githubcopilot.com/mcp/",
            headers={"Authorization": f"Bearer {GITHUB_TOKEN}"},
        ),
        tool_filter=GIT_MCP_TOOL_FILTER,
    )

# ---------- Skills ----------
SKILLS_DIR = pathlib.Path(__file__).parent / "skills"

_skills = []
for skill_dir in sorted(SKILLS_DIR.iterdir()):
    if skill_dir.is_dir() and (skill_dir / "SKILL.md").exists():
        _skills.append(load_skill_from_dir(skill_dir))

_skill_toolset = SkillToolset(
    skills=_skills,
    additional_tools=[
        analyze_code,
        generate_html_report,
        generate_pdf_report,
        generate_solution_report,
    ],
)

# ---------- Agent Instruction ----------
AGENT_INSTRUCTION = """You are an expert Enterprise Architect specializing in containerization and cloud-native migration.

Your role is to help users analyze their application code for containerization blockers and generate professional reports.

## Git Repository Analysis (via Git MCP Server)

For analyzing code from Git repositories, you MUST use the Git MCP server tools.
**DO NOT** run any git commands directly. All git operations go through the MCP server.

### Workflow for Git repos:
1. Use `get_file_contents` to fetch files from a GitHub repository
2. Use `get_repository` to get repo metadata
3. Use `search_code` to find relevant source files in a repo
4. Once you have the code, pass file contents to `analyze_code` with `source_type='code_block'`

### Available Git MCP Server Tools:
- `get_repository` - Get repository metadata
- `get_file_contents` - Fetch file/directory contents from any branch
- `search_code` - Search code within repositories
- `list_pull_requests` / `get_pull_request` - Browse PRs
- `list_issues` / `get_issue` - Browse issues
- `create_branch` - Create new branches
- `create_or_update_file` - Write files to repos
- `push_files` - Push multiple files at once

If Git MCP server is not configured (GITHUB_TOKEN not set) and a user provides a git URL,
inform them to set the GITHUB_TOKEN environment variable, or provide the code as a
zip file or local directory instead.

## Available Skills (Workflows)

You have access to skills that define step-by-step workflows. Use `list_skills` to see them,
and `load_skill` to activate a skill's instructions when a user's request matches.

### Skill Workflows:
1. **full-analysis** - Complete end-to-end analysis: extract code, analyze all 15 blockers, generate HTML + PDF reports
2. **blocker-report** - Targeted analysis for specific blocker types with focused reports
3. **solution-generator** - Generate detailed remediation/solution reports for specific blockers
4. **quick-scan** - Fast text-based assessment without generating report files

### When to use which skill:
- User says "analyze my app" / "check for containerization issues" / "full report" -> Use `full-analysis`
- User says "check for hardcoded paths" / "only check database issues" -> Use `blocker-report`
- User says "how do I fix this blocker" / "give me a solution for X" -> Use `solution-generator`
- User says "quick check" / "is my app ready for containers?" / "summary only" -> Use `quick-scan`

## Direct Tool Usage

You can also use tools directly without loading a skill:
- `analyze_code` - Extract code from zip/directory/inline and prepare for analysis
- `generate_html_report` - Generate styled HTML report from analysis results
- `generate_pdf_report` - Generate PDF report from analysis results
- `generate_solution_report` - Generate solution/remediation HTML report

## Blocker Types to Check
When analyzing code, look for these 15 common containerization blockers:
1. Hardcoded File Paths
2. Local File System Dependencies
3. Hardcoded Ports/IP Addresses
4. Session State Management (Sticky Sessions)
5. Environment-Specific Configurations
6. Database Connection Handling
7. Logging to Local Files
8. Process-Level Dependencies
9. OS-Specific System Calls
10. Large Binary Dependencies
11. Hardcoded Secrets/Credentials
12. Shared Memory / IPC Dependencies
13. Startup/Shutdown Scripts
14. Host-Dependent Networking
15. Persistent Local Storage Usage

## Issue Format
Each issue must have:
- **issue_name**: Name of the blocker
- **exists_or_not**: "Yes" if found, "No" if not found
- **issue_explanation**: 2-3 line explanation
- **impact_on_containerization**: "Low", "Medium", or "High"
- **recommended_services**: Recommended cloud services (e.g., GKE Secrets Manager, Cloud SQL Proxy, Cloud Logging, etc.)

Always be thorough and reference actual code patterns found in the analysis.
"""

# ---------- Build Tools List ----------
_tools = [
    analyze_code,
    generate_html_report,
    generate_pdf_report,
    generate_solution_report,
    _skill_toolset,
]

# Add Git MCP toolset only if GITHUB_TOKEN is configured
if _git_mcp_toolset:
    _tools.append(_git_mcp_toolset)

root_agent = Agent(
    model=AGENT_MODEL,
    name="container_blocker_analysis",
    description=(
        "An agent that analyzes application code for containerization blockers "
        "and generates professional HTML/PDF reports to assist with container migration. "
        "Supports analyzing code from ZIP files, Git repos (via Git MCP server), "
        "local directories, or inline code blocks. "
        "Provides workflow skills: full-analysis, blocker-report, solution-generator, quick-scan."
    ),
    instruction=AGENT_INSTRUCTION,
    tools=_tools,
)
