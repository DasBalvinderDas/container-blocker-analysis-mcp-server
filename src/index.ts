#!/usr/bin/env node

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { analyzeCode, analyzeCodeSchema } from "./tools/analyze-code.js";
import {
  handleGenerateHtmlReport,
  handleGeneratePdfReport,
  handleGenerateSolutionHtml,
  generateHtmlReportSchema,
  generatePdfReportSchema,
  generateSolutionHtmlSchema,
} from "./tools/generate-report.js";

const server = new McpServer({
  name: "container-blocker-analysis",
  version: "1.0.0",
});

// Tool 1: Analyze Code for Containerization Blockers
server.tool(
  "analyze_code",
  `Analyze application code for containerization blockers and migration issues.
Extracts code from various sources (inline code, zip files, git repos, local directories),
then returns the code content with a structured analysis prompt. The LLM should evaluate
the code for containerization readiness and return the structured JSON result, which can
then be passed to generate_html_report or generate_pdf_report.`,
  analyzeCodeSchema.shape,
  async ({ source_type, source, language, blocker_types, app_name }) => {
    try {
      const result = await analyzeCode({
        source_type,
        source,
        language,
        blocker_types,
        app_name,
      });

      return {
        content: [
          {
            type: "text" as const,
            text: JSON.stringify(
              {
                status: "success",
                file_count: result.fileCount,
                total_lines: result.totalLines,
                files_analyzed: result.files.map((f) => ({
                  path: f.relativePath,
                  language: f.language,
                  lines: f.content.split("\n").length,
                })),
                analysis_prompt: result.analysisPrompt,
                instructions:
                  "Execute the analysis described in 'analysis_prompt' and return the JSON result. Then use 'generate_html_report' or 'generate_pdf_report' to create a report from the results.",
              },
              null,
              2
            ),
          },
        ],
      };
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      return {
        content: [{ type: "text" as const, text: `Error: ${message}` }],
        isError: true,
      };
    }
  }
);

// Tool 2: Generate HTML Report
server.tool(
  "generate_html_report",
  `Generate a styled HTML report from containerization blocker analysis results.
Takes the structured issues array and produces a professional HTML report with
summary statistics, color-coded impact levels, and a detailed issues table.
Can save to a file or return HTML content directly.`,
  generateHtmlReportSchema.shape,
  async (input) => {
    try {
      const result = await handleGenerateHtmlReport(input);
      return {
        content: [{ type: "text" as const, text: result }],
      };
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      return {
        content: [{ type: "text" as const, text: `Error: ${message}` }],
        isError: true,
      };
    }
  }
);

// Tool 3: Generate PDF Report
server.tool(
  "generate_pdf_report",
  `Generate a PDF report from containerization blocker analysis results.
Takes the structured issues array and produces a professional PDF report with
a structured table layout, color-coded impact levels, and summary statistics.`,
  generatePdfReportSchema.shape,
  async (input) => {
    try {
      const result = await handleGeneratePdfReport(input);
      return {
        content: [{ type: "text" as const, text: result }],
      };
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      return {
        content: [{ type: "text" as const, text: `Error: ${message}` }],
        isError: true,
      };
    }
  }
);

// Tool 4: Generate Solution HTML
server.tool(
  "generate_solution_html",
  `Generate a styled HTML solution report for a specific containerization blocker.
Takes the blocker type and solution content (in HTML format) and wraps it in a
professional, styled document. Use after analyzing a blocker to provide actionable
remediation steps including code changes, dependencies, and effort estimation.`,
  generateSolutionHtmlSchema.shape,
  async (input) => {
    try {
      const result = await handleGenerateSolutionHtml(input);
      return {
        content: [{ type: "text" as const, text: result }],
      };
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      return {
        content: [{ type: "text" as const, text: `Error: ${message}` }],
        isError: true,
      };
    }
  }
);

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("Container Blocker Analysis MCP Server running on stdio");
}

main().catch((error) => {
  console.error("Fatal error:", error);
  process.exit(1);
});
