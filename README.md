# Container Blocker Analysis MCP Server

An MCP (Model Context Protocol) server that helps analyze application code for containerization blockers and generates professional reports to assist with container migration.

## Features

- **Code Analysis**: Analyze code from multiple sources (inline code, zip files, git repos, local directories) for containerization blockers
- **HTML Report Generation**: Generate professional, styled HTML reports with color-coded impact levels
- **PDF Report Generation**: Generate structured PDF reports using pdf-lib
- **Solution Reports**: Generate detailed solution/remediation HTML reports for specific blockers

## Blocker Types Analyzed

The server checks for 15 common containerization blockers:

| Blocker | Description |
|---------|-------------|
| Hardcoded File Paths | Absolute paths that won't exist in containers |
| Local File System Dependencies | Direct filesystem reads/writes |
| Hardcoded Ports/IP Addresses | Static network configurations |
| Session State Management | Sticky sessions incompatible with scaling |
| Environment-Specific Configurations | Configs tied to specific environments |
| Database Connection Handling | Non-portable DB connection strings |
| Logging to Local Files | File-based logging instead of stdout |
| Process-Level Dependencies | Dependencies on host processes |
| OS-Specific System Calls | Platform-specific OS calls |
| Large Binary Dependencies | Large binaries that bloat container images |
| Hardcoded Secrets/Credentials | Embedded secrets in code |
| Shared Memory / IPC Dependencies | Inter-process communication patterns |
| Startup/Shutdown Scripts | Host-dependent lifecycle scripts |
| Host-Dependent Networking | Network configs tied to host |
| Persistent Local Storage Usage | Data stored locally instead of external storage |

## Tools

### `analyze_code`
Extracts code from the provided source and returns a structured analysis prompt for the LLM to evaluate.

**Input:**
- `source_type`: `"code_block"` | `"zip_file"` | `"git_repo"` | `"local_directory"`
- `source`: The code, file path, git URL, or directory path
- `language` (optional): Programming language for code blocks
- `blocker_types` (optional): Specific blockers to check
- `app_name` (optional): Application name for reports

### `generate_html_report`
Generates a styled HTML report from analysis results.

**Input:**
- `app_name`: Application name
- `issues`: Array of issue objects with `issue_name`, `exists_or_not`, `issue_explanation`, `impact_on_containerization`, `recommended_services`
- `summary` (optional): Overall summary
- `output_path` (optional): File path to save (returns HTML content if not provided)

### `generate_pdf_report`
Generates a PDF report from analysis results.

**Input:** Same as `generate_html_report`

### `generate_solution_html`
Generates a styled HTML solution report for a specific blocker.

**Input:**
- `app_name`: Application name
- `blocker_type`: The blocker being solved
- `solution_content`: HTML-formatted solution content
- `output_path` (optional): File path to save

## Installation

```bash
npm install
npm run build
```

## Usage

### With Claude Desktop

Add to your Claude Desktop config (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "container-blocker-analysis": {
      "command": "node",
      "args": ["/path/to/container-blocker-analysis-mcp-server/dist/index.js"]
    }
  }
}
```

### With Claude Code

Add to your Claude Code MCP settings:

```json
{
  "mcpServers": {
    "container-blocker-analysis": {
      "command": "node",
      "args": ["/path/to/container-blocker-analysis-mcp-server/dist/index.js"]
    }
  }
}
```

### Workflow Example

1. Use `analyze_code` to extract and prepare code for analysis
2. The LLM evaluates the code using the returned analysis prompt
3. Pass the structured results to `generate_html_report` or `generate_pdf_report`
4. For specific blockers, use `generate_solution_html` to create remediation reports

## Development

```bash
npm run dev    # Watch mode for TypeScript
npm run build  # Build
npm start      # Run the server
```

## License

MIT
