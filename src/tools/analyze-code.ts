import { z } from "zod";
import {
  extractFromZip,
  extractFromGitRepo,
  extractFromDirectory,
  extractFromCodeBlock,
  formatFilesForAnalysis,
  type ExtractedFile,
} from "../utils/code-extractor.js";

export const analyzeCodeSchema = z.object({
  source_type: z
    .enum(["code_block", "zip_file", "git_repo", "local_directory"])
    .describe(
      "Type of source to analyze: 'code_block' for inline code, 'zip_file' for a local zip path, 'git_repo' for a git URL, 'local_directory' for a local folder path"
    ),
  source: z
    .string()
    .describe(
      "The source to analyze. For code_block: the code itself. For zip_file: absolute path to zip. For git_repo: the repository URL. For local_directory: absolute path to directory."
    ),
  language: z
    .string()
    .optional()
    .describe("Programming language (for code_block source type). E.g., 'python', 'java', 'javascript'"),
  blocker_types: z
    .array(z.string())
    .optional()
    .describe(
      "Specific blocker types to check. If not provided, all common blockers are analyzed. Examples: 'hardcoded_file_paths', 'local_filesystem_deps', 'hardcoded_ports', 'session_state', 'env_specific_config', 'db_connection_handling', 'local_logging', 'process_deps', 'os_specific_calls', 'binary_deps'"
    ),
  app_name: z
    .string()
    .optional()
    .describe("Application name for the report. Defaults to 'Application'"),
});

export type AnalyzeCodeInput = z.infer<typeof analyzeCodeSchema>;

const ALL_BLOCKER_TYPES = [
  "Hardcoded File Paths",
  "Local File System Dependencies",
  "Hardcoded Ports/IP Addresses",
  "Session State Management (Sticky Sessions)",
  "Environment-Specific Configurations",
  "Database Connection Handling",
  "Logging to Local Files",
  "Process-Level Dependencies",
  "OS-Specific System Calls",
  "Large Binary Dependencies",
  "Hardcoded Secrets/Credentials",
  "Shared Memory / IPC Dependencies",
  "Startup/Shutdown Scripts",
  "Host-Dependent Networking",
  "Persistent Local Storage Usage",
];

export async function analyzeCode(input: AnalyzeCodeInput): Promise<{
  files: ExtractedFile[];
  formattedCode: string;
  analysisPrompt: string;
  fileCount: number;
  totalLines: number;
}> {
  let files: ExtractedFile[];

  switch (input.source_type) {
    case "code_block":
      files = extractFromCodeBlock(input.source, input.language);
      break;
    case "zip_file":
      files = await extractFromZip(input.source);
      break;
    case "git_repo":
      files = await extractFromGitRepo(input.source);
      break;
    case "local_directory":
      files = await extractFromDirectory(input.source);
      break;
  }

  if (files.length === 0) {
    throw new Error("No code files found in the provided source.");
  }

  const formattedCode = formatFilesForAnalysis(files);
  const totalLines = files.reduce(
    (sum, f) => sum + f.content.split("\n").length,
    0
  );

  const blockerTypes =
    input.blocker_types && input.blocker_types.length > 0
      ? input.blocker_types
      : ALL_BLOCKER_TYPES;

  const blockerList = blockerTypes.map((b) => `- ${b}`).join("\n");

  const analysisPrompt = `You are an expert Enterprise Architect specializing in containerization and cloud-native migration.

Analyze the following application code to identify containerization blockers.

**Application:** ${input.app_name || "Application"}

**Check for these specific blocker types:**
${blockerList}

**Code to analyze:**
${formattedCode}

### Response Instructions:
Respond with ONLY a valid JSON object (no markdown, no code fences, no explanation text outside the JSON).

The JSON must follow this exact schema:
{
  "issues": [
    {
      "issue_name": "Name of the issue",
      "exists_or_not": "Yes" or "No",
      "issue_explanation": "2-3 line explanation of the issue found (or why it doesn't exist)",
      "impact_on_containerization": "Low", "Medium", or "High",
      "recommended_services": "Recommended cloud services or solutions to address this (e.g., GKE Secrets Manager, Cloud SQL Proxy, etc.)"
    }
  ],
  "summary": "A brief overall assessment of the application's container-readiness"
}

Include one entry per blocker type checked. Be thorough and specific - reference actual code patterns found.`;

  return {
    files,
    formattedCode,
    analysisPrompt,
    fileCount: files.length,
    totalLines,
  };
}
