import { z } from "zod";
import fs from "fs/promises";
import path from "path";
import os from "os";
import {
  generateAnalysisHTML,
  generateSolutionHTML,
  generateAnalysisPDF,
  type AnalysisResult,
  type ContainerizationIssue,
} from "../utils/report-generator.js";

const issueSchema = z.object({
  issue_name: z.string(),
  exists_or_not: z.enum(["Yes", "No"]),
  issue_explanation: z.string(),
  impact_on_containerization: z.enum(["Low", "Medium", "High"]),
  recommended_services: z.string(),
});

export const generateHtmlReportSchema = z.object({
  app_name: z.string().describe("Application name for the report header"),
  blocker_type: z
    .string()
    .optional()
    .describe("Specific blocker type that was analyzed (optional)"),
  issues: z
    .array(issueSchema)
    .describe("Array of containerization issues found during analysis"),
  summary: z
    .string()
    .optional()
    .describe("Overall summary of the analysis"),
  output_path: z
    .string()
    .optional()
    .describe(
      "File path to save the HTML report. If not provided, returns HTML content directly."
    ),
});

export const generatePdfReportSchema = z.object({
  app_name: z.string().describe("Application name for the report header"),
  blocker_type: z
    .string()
    .optional()
    .describe("Specific blocker type that was analyzed (optional)"),
  issues: z
    .array(issueSchema)
    .describe("Array of containerization issues found during analysis"),
  summary: z
    .string()
    .optional()
    .describe("Overall summary of the analysis"),
  output_path: z
    .string()
    .optional()
    .describe(
      "File path to save the PDF report. If not provided, saves to a temp directory and returns the path."
    ),
});

export const generateSolutionHtmlSchema = z.object({
  app_name: z.string().describe("Application name"),
  blocker_type: z.string().describe("The blocker type being solved"),
  solution_content: z
    .string()
    .describe(
      "The solution content in HTML format (can include h2, p, ul, li, pre, code tags)"
    ),
  output_path: z
    .string()
    .optional()
    .describe("File path to save the HTML report. If not provided, returns HTML content directly."),
});

export type GenerateHtmlReportInput = z.infer<typeof generateHtmlReportSchema>;
export type GeneratePdfReportInput = z.infer<typeof generatePdfReportSchema>;
export type GenerateSolutionHtmlInput = z.infer<typeof generateSolutionHtmlSchema>;

export async function handleGenerateHtmlReport(
  input: GenerateHtmlReportInput
): Promise<string> {
  const result: AnalysisResult = {
    app_name: input.app_name,
    blocker_type: input.blocker_type,
    issues: input.issues as ContainerizationIssue[],
    summary: input.summary,
  };

  const html = generateAnalysisHTML(result);

  if (input.output_path) {
    await fs.mkdir(path.dirname(input.output_path), { recursive: true });
    await fs.writeFile(input.output_path, html, "utf-8");
    return `HTML report saved to: ${input.output_path}`;
  }

  return html;
}

export async function handleGeneratePdfReport(
  input: GeneratePdfReportInput
): Promise<string> {
  const result: AnalysisResult = {
    app_name: input.app_name,
    blocker_type: input.blocker_type,
    issues: input.issues as ContainerizationIssue[],
    summary: input.summary,
  };

  const pdfBytes = await generateAnalysisPDF(result);

  const outputPath =
    input.output_path ||
    path.join(os.tmpdir(), `container-analysis-${Date.now()}.pdf`);

  await fs.mkdir(path.dirname(outputPath), { recursive: true });
  await fs.writeFile(outputPath, pdfBytes);

  return `PDF report saved to: ${outputPath}`;
}

export async function handleGenerateSolutionHtml(
  input: GenerateSolutionHtmlInput
): Promise<string> {
  const html = generateSolutionHTML(
    input.app_name,
    input.blocker_type,
    input.solution_content
  );

  if (input.output_path) {
    await fs.mkdir(path.dirname(input.output_path), { recursive: true });
    await fs.writeFile(input.output_path, html, "utf-8");
    return `Solution HTML report saved to: ${input.output_path}`;
  }

  return html;
}
