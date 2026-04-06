---
name: solution-generator
description: >
  Generate detailed solution and remediation steps for specific containerization
  blockers found in application code. Produces a professional HTML solution report
  with code changes, dependencies, infrastructure requirements, effort estimation,
  and potential risks. Use this after running an analysis to fix identified issues.
---

## Solution Generation Workflow

Follow these steps precisely:

### Step 1: Identify the Blocker

Determine which specific blocker the user wants a solution for. If the user hasn't run an analysis yet, first use the `analyze_code` tool to extract the code and identify the blocker.

### Step 2: Extract Code (if needed)

If you don't already have the code content from a prior analysis, call `analyze_code` to extract it. You need the actual code to provide specific, actionable solutions.

### Step 3: Generate Solution Content

For the identified blocker, create a detailed solution in HTML format covering these sections:

**Code Changes:**
- Specific line-by-line modifications required
- Show before/after code snippets using `<pre><code>` blocks
- Explain each change

**Dependencies:**
- New libraries or packages needed
- Changes to requirements.txt, pom.xml, package.json, etc.
- Version requirements

**Infrastructure/Configuration:**
- Cloud service setup required (e.g., Cloud SQL Proxy, Secret Manager)
- Kubernetes manifests or Docker configuration changes
- Environment variable definitions
- ConfigMap or Secret definitions

**Effort Estimation:**
- Categorize as Low (< 1 day), Medium (1-3 days), or High (> 3 days)
- Justify the estimate

**Potential Risks:**
- Runtime issues that may arise
- Deployment concerns
- Backward compatibility impacts
- Testing requirements

Refer to the `references/solution_template.md` for the expected HTML structure.

### Step 4: Generate Solution Report

Call `generate_solution_report` with:
- `app_name`: The application name
- `blocker_type`: The specific blocker being addressed
- `solution_content`: The HTML-formatted solution from Step 3
- `output_path`: A path like `./reports/<app_name>_solution_<blocker>.html`

### Step 5: Present Summary

Provide the user with:
- The blocker that was addressed
- Key changes required (brief summary)
- Effort estimation
- Top risks to watch for
- Report file location
- Suggest running a follow-up analysis after implementing changes
