---
name: full-analysis
description: >
  Complete end-to-end containerization blocker analysis workflow. Extracts code
  from any source (zip, git repo via Git MCP server, directory, or inline code),
  analyzes it for all 15 containerization blockers, and generates both HTML and
  PDF reports. Use this skill for a comprehensive container-readiness assessment.
---

## Full Containerization Blocker Analysis Workflow

Follow these steps precisely:

### Step 1: Extract and Analyze Code

Determine the source type and extract code accordingly:

- **Zip file path** -> Call `analyze_code` with `source_type: "zip_file"`
- **Local directory path** -> Call `analyze_code` with `source_type: "local_directory"`
- **Inline code** -> Call `analyze_code` with `source_type: "code_block"`
- **Git repository URL** -> Use the **Git MCP server** workflow:
  1. Use Git MCP server tools to browse/fetch the repository contents
     (e.g., `get_file_contents`, `search_code`, `list_files`)
  2. Once you have the code, call `analyze_code` with either:
     - `source_type: "local_directory"` if the repo was cloned locally
     - `source_type: "code_block"` with the combined file contents

**IMPORTANT:** Never run git commands directly. All git operations MUST go through
the Git MCP server tools.

Set `app_name` to the application name if provided, otherwise derive it from the source.

### Step 2: Perform the Blocker Analysis

Using the `analysis_prompt` returned by `analyze_code`, carefully evaluate the code for ALL 15 containerization blockers:

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

For each blocker, determine:
- Whether it exists in the code ("Yes"/"No")
- A 2-3 line explanation referencing specific code patterns
- Impact level ("Low"/"Medium"/"High")
- Recommended cloud services to address it

Also produce an overall summary of container-readiness.

### Step 3: Generate HTML Report

Call `generate_html_report` with:
- `app_name`: The application name
- `issues`: The list of all issues found in Step 2
- `summary`: The overall assessment summary
- `output_path`: Ask the user where to save, or use a sensible default like `./reports/<app_name>_analysis.html`

### Step 4: Generate PDF Report

Call `generate_pdf_report` with the same parameters but with a `.pdf` extension for `output_path`.

### Step 5: Present Results

Summarize the findings to the user:
- Total issues found (with exists_or_not = "Yes")
- Breakdown by impact level (High/Medium/Low)
- Top 3 most critical issues
- Report file locations
- Recommend next steps (e.g., "Use the solution-generator skill to get fixes for specific blockers")
