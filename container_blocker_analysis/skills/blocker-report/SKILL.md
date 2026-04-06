---
name: blocker-report
description: >
  Analyze code for specific containerization blocker types and generate a focused
  report. Use this skill when the user wants to check for particular blockers
  (e.g., only hardcoded paths and database connections) rather than a full scan.
---

## Targeted Blocker Analysis Workflow

Follow these steps precisely:

### Step 1: Identify Target Blockers

Determine which specific blocker types the user wants to check. Valid blocker types are:
- Hardcoded File Paths
- Local File System Dependencies
- Hardcoded Ports/IP Addresses
- Session State Management (Sticky Sessions)
- Environment-Specific Configurations
- Database Connection Handling
- Logging to Local Files
- Process-Level Dependencies
- OS-Specific System Calls
- Large Binary Dependencies
- Hardcoded Secrets/Credentials
- Shared Memory / IPC Dependencies
- Startup/Shutdown Scripts
- Host-Dependent Networking
- Persistent Local Storage Usage

If the user's request is vague (e.g., "check networking issues"), map it to the relevant blockers (e.g., Hardcoded Ports/IP Addresses, Host-Dependent Networking).

### Step 2: Extract Code

Call `analyze_code` with:
- The appropriate `source_type` and `source`
- `blocker_types`: The specific list of blockers to check
- `app_name`: The application name

### Step 3: Perform Targeted Analysis

Using the returned `analysis_prompt`, analyze the code ONLY for the specified blocker types. Be thorough and reference actual code patterns found.

### Step 4: Generate Report

Ask the user their preferred format:
- **HTML**: Call `generate_html_report` with `blocker_type` set to describe the focus area
- **PDF**: Call `generate_pdf_report` with the same parameters
- **Both**: Generate both formats

If the user doesn't specify, default to HTML.

### Step 5: Present Findings

Present a concise summary:
- Which blockers were checked
- Which were found vs not found
- Impact breakdown
- Report file location(s)
