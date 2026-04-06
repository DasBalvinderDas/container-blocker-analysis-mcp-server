---
name: full-analysis
description: >
  Complete end-to-end containerization blocker analysis workflow. Extracts code
  from any source (zip, git repo, directory, or inline code), analyzes it for all
  15 containerization blockers, and generates both HTML and PDF reports. Use this
  skill when the user wants a comprehensive container-readiness assessment.
---

## Full Containerization Blocker Analysis Workflow

Follow these steps precisely:

### Step 1: Extract and Analyze Code

Call the `analyze_code` tool with the user's provided source:
- If they provide a **git repo URL**, use `source_type: "git_repo"`
- If they provide a **zip file path**, use `source_type: "zip_file"`
- If they provide a **local directory path**, use `source_type: "local_directory"`
- If they provide **inline code**, use `source_type: "code_block"`

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
