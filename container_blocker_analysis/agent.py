"""Container Blocker Analysis Agent - Google ADK Agent Definition.

This agent analyzes application code for containerization blockers and
generates professional HTML/PDF reports to assist with container migration.

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
from google.adk.tools.skill_toolset import SkillToolset

from .tools.analyze_code import analyze_code
from .tools.generate_report import (
    generate_html_report,
    generate_pdf_report,
    generate_solution_report,
)

AGENT_MODEL = os.getenv("AGENT_MODEL", "gemini-2.5-flash")

# Load skills from the skills/ directory
SKILLS_DIR = pathlib.Path(__file__).parent / "skills"

_skills = []
for skill_dir in sorted(SKILLS_DIR.iterdir()):
    if skill_dir.is_dir() and (skill_dir / "SKILL.md").exists():
        _skills.append(load_skill_from_dir(skill_dir))

# Create the SkillToolset with our function tools available as additional tools
_skill_toolset = SkillToolset(
    skills=_skills,
    additional_tools=[
        analyze_code,
        generate_html_report,
        generate_pdf_report,
        generate_solution_report,
    ],
)

AGENT_INSTRUCTION = """You are an expert Enterprise Architect specializing in containerization and cloud-native migration.

Your role is to help users analyze their application code for containerization blockers and generate professional reports.

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
- `analyze_code` - Extract code from zip/git/directory/inline and prepare for analysis
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

root_agent = Agent(
    model=AGENT_MODEL,
    name="container_blocker_analysis",
    description=(
        "An agent that analyzes application code for containerization blockers "
        "and generates professional HTML/PDF reports to assist with container migration. "
        "Supports analyzing code from ZIP files, Git repos, local directories, or inline code blocks. "
        "Provides workflow skills: full-analysis, blocker-report, solution-generator, quick-scan."
    ),
    instruction=AGENT_INSTRUCTION,
    tools=[
        analyze_code,
        generate_html_report,
        generate_pdf_report,
        generate_solution_report,
        _skill_toolset,
    ],
)
