---
name: quick-scan
description: >
  Quick containerization readiness scan that provides a fast summary without
  generating full reports. Returns a text-based overview of the most critical
  blockers found. Use this for a rapid assessment before deciding on a full analysis.
---

## Quick Scan Workflow

Follow these steps precisely:

### Step 1: Extract Code

Call `analyze_code` with the user's provided source. Use default blocker types (all 15).

### Step 2: Rapid Assessment

Using the returned code and analysis prompt, perform a focused evaluation looking for the **most impactful** blockers. Prioritize:

1. **Critical** (likely High impact):
   - Hardcoded Secrets/Credentials
   - Hardcoded File Paths
   - Local File System Dependencies
   - Database Connection Handling

2. **Important** (likely Medium impact):
   - Hardcoded Ports/IP Addresses
   - Environment-Specific Configurations
   - Logging to Local Files
   - Session State Management

3. **Advisory** (likely Low impact):
   - OS-Specific System Calls
   - Process-Level Dependencies
   - Large Binary Dependencies
   - Others

### Step 3: Present Quick Summary

Present results in a concise text format (NO report file generation):

```
Container Readiness: [READY / NEEDS WORK / NOT READY]

Critical Issues (X found):
  - [Issue]: [one-line explanation]

Important Issues (X found):
  - [Issue]: [one-line explanation]

Advisory Issues (X found):
  - [Issue]: [one-line explanation]

Recommendation: [Brief next steps]
```

### Step 4: Suggest Next Steps

Based on the results, suggest:
- If many issues: "Run the `full-analysis` skill for detailed reports"
- If specific blockers: "Run the `solution-generator` skill for fix: [blocker name]"
- If few/no issues: "Your application appears container-ready. Consider creating a Dockerfile."
