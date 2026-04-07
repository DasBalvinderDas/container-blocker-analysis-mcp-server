# Container Blocker Analysis MCP Server (Google ADK)

An MCP server built with [Google Agent Development Kit (ADK)](https://google.github.io/adk-docs/) that analyzes application code for containerization blockers and generates professional reports to assist with container migration.

## Features

- **Code Analysis**: Analyze code from multiple sources (inline code, zip files, git repos, local directories) for containerization blockers
- **HTML Report Generation**: Professional, styled HTML reports with color-coded impact levels and summary statistics
- **PDF Report Generation**: Structured PDF reports using ReportLab with tables and color-coded formatting
- **Solution Reports**: Detailed solution/remediation HTML reports for specific blockers
- **Skills (Workflows)**: Pre-defined step-by-step workflows using ADK Skills for common tasks

## Blocker Types Analyzed

The agent checks for 15 common containerization blockers:

| # | Blocker | Description |
|---|---------|-------------|
| 1 | Hardcoded File Paths | Absolute paths that won't exist in containers |
| 2 | Local File System Dependencies | Direct filesystem reads/writes |
| 3 | Hardcoded Ports/IP Addresses | Static network configurations |
| 4 | Session State Management | Sticky sessions incompatible with scaling |
| 5 | Environment-Specific Configurations | Configs tied to specific environments |
| 6 | Database Connection Handling | Non-portable DB connection strings |
| 7 | Logging to Local Files | File-based logging instead of stdout |
| 8 | Process-Level Dependencies | Dependencies on host processes |
| 9 | OS-Specific System Calls | Platform-specific OS calls |
| 10 | Large Binary Dependencies | Large binaries that bloat container images |
| 11 | Hardcoded Secrets/Credentials | Embedded secrets in code |
| 12 | Shared Memory / IPC Dependencies | Inter-process communication patterns |
| 13 | Startup/Shutdown Scripts | Host-dependent lifecycle scripts |
| 14 | Host-Dependent Networking | Network configs tied to host |
| 15 | Persistent Local Storage Usage | Data stored locally instead of external storage |

## Tools

### `analyze_code`
Extracts code from the provided source and returns a structured analysis prompt for the LLM to evaluate.

For git repositories, the agent uses the **Git MCP server** to fetch code first, then passes it to this tool. No git commands are run directly.

**Parameters:**
- `source_type` (required): `"code_block"` | `"zip_file"` | `"git_repo"` | `"local_directory"`
- `source` (required): The code, file path, git URL, or directory path
- `language` (optional): Programming language hint for code blocks
- `blocker_types` (optional): Specific blockers to check (defaults to all 15)
- `app_name` (optional): Application name for reports

### `generate_html_report`
Generates a styled HTML report from analysis results.

**Parameters:**
- `app_name` (required): Application name
- `issues` (required): List of issue dicts with `issue_name`, `exists_or_not`, `issue_explanation`, `impact_on_containerization`, `recommended_services`
- `blocker_type` (optional): Specific blocker type analyzed
- `summary` (optional): Overall summary
- `output_path` (optional): File path to save (returns HTML content if not provided)

### `generate_pdf_report`
Generates a PDF report from analysis results.

**Parameters:** Same as `generate_html_report`

### `generate_solution_report`
Generates a styled HTML solution report for a specific blocker.

**Parameters:**
- `app_name` (required): Application name
- `blocker_type` (required): The blocker being solved
- `solution_content` (required): HTML-formatted solution content
- `output_path` (optional): File path to save

## Skills (Workflows)

Skills are pre-defined step-by-step workflows powered by [ADK Skills](https://google.github.io/adk-docs/skills/). The agent automatically discovers them via `SkillToolset` and exposes `list_skills` / `load_skill` tools.

| Skill | Description | When to Use |
|-------|-------------|-------------|
| `full-analysis` | Complete end-to-end analysis: extract code, check all 15 blockers, generate HTML + PDF reports | "Analyze my app for containerization issues" |
| `blocker-report` | Targeted analysis for specific blocker types with focused reports | "Check for hardcoded paths and DB connection issues" |
| `solution-generator` | Generate detailed remediation steps with code changes, effort estimation, and risks | "How do I fix the hardcoded secrets blocker?" |
| `quick-scan` | Fast text-based assessment without generating report files | "Is my app ready for containers?" |

### Skill Structure

Each skill is a directory under `skills/` with a `SKILL.md` file:

```
skills/
├── full-analysis/
│   ├── SKILL.md                        # Workflow instructions
│   ├── references/
│   │   └── blocker_definitions.md      # Detailed blocker descriptions
│   └── assets/
│       └── issue_schema.json           # JSON schema for analysis output
├── blocker-report/
│   └── SKILL.md
├── solution-generator/
│   ├── SKILL.md
│   └── references/
│       └── solution_template.md        # HTML template guide for solutions
└── quick-scan/
    └── SKILL.md
```

## Installation

### Prerequisites
- Python >= 3.10
- Google Cloud project with Vertex AI API enabled (for Gemini model access)

### Setup

```bash
# Clone the repo
git clone https://github.com/DasBalvinderDas/container-blocker-analysis-mcp-server.git
cd container-blocker-analysis-mcp-server

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your GCP project details
```

### Google Cloud Authentication

```bash
# Authenticate with Google Cloud
gcloud auth application-default login

# Or set service account key
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/key.json"
```

## Usage

### Run with ADK CLI

```bash
# Start the ADK development UI
adk web container_blocker_analysis

# Or run via CLI
adk run container_blocker_analysis
```

### Project Structure

```
container_blocker_analysis/
├── __init__.py
├── agent.py                   # ADK agent definition (root_agent + SkillToolset)
├── tools/
│   ├── __init__.py
│   ├── analyze_code.py        # Code extraction + analysis prompt builder
│   └── generate_report.py     # HTML/PDF/Solution report generation
├── utils/
│   ├── __init__.py
│   ├── code_extractor.py      # Extract code from zip/git/directory/inline
│   └── report_generator.py    # HTML templates + PDF generation (ReportLab)
└── skills/                    # ADK Skills (workflows)
    ├── full-analysis/         # Complete analysis workflow
    ├── blocker-report/        # Targeted blocker analysis
    ├── solution-generator/    # Solution/remediation generation
    └── quick-scan/            # Quick readiness assessment
```

### Git MCP Server Configuration

All git operations (clone, fetch, browse) are handled by an external **Git MCP server** - no git commands run in this codebase.

Configure in `.env`:

```bash
# Option A: Stdio-based (recommended for local dev)
GIT_MCP_SERVER_CMD=npx
GIT_MCP_SERVER_ARGS=-y @modelcontextprotocol/server-github
GITHUB_TOKEN=ghp_your_token_here

# Option B: SSE-based (for remote/hosted MCP servers)
GIT_MCP_SERVER_URL=http://localhost:3000/sse
```

### Workflow Example

1. User asks the agent to analyze their application code
2. If source is a git repo: agent uses **Git MCP server** tools to fetch the code
3. Agent calls `analyze_code` to prepare code for analysis
4. Agent evaluates the code for containerization blockers
5. Agent calls `generate_html_report` or `generate_pdf_report` to create reports
6. For specific blockers, agent uses `generate_solution_report` for remediation steps

### Example Prompts

```
"Analyze the code in /path/to/my/app for containerization blockers and generate an HTML report"

"Analyze https://github.com/user/repo and check for hardcoded file paths and database connection issues"

"Generate a PDF report for my-app with these issues: [paste JSON]"

"Provide a solution for the hardcoded database connection blocker found in my-app"
```

## Development

```bash
# Install dev dependencies
pip install -r requirements.txt
pip install pytest ruff mypy

# Lint
ruff check .

# Format
ruff format .

# Type check
mypy container_blocker_analysis/
```

## License

Apache 2.0
