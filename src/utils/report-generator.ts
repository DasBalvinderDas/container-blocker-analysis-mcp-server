import { PDFDocument, StandardFonts, rgb, PDFPage, PDFFont } from "pdf-lib";

export interface ContainerizationIssue {
  issue_name: string;
  exists_or_not: "Yes" | "No";
  issue_explanation: string;
  impact_on_containerization: "Low" | "Medium" | "High";
  recommended_services: string;
}

export interface AnalysisResult {
  app_name: string;
  blocker_type?: string;
  issues: ContainerizationIssue[];
  summary?: string;
}

export function generateAnalysisHTML(result: AnalysisResult): string {
  const tableRows = result.issues
    .map(
      (issue) => `
            <tr class="${issue.exists_or_not === "Yes" ? (issue.impact_on_containerization === "High" ? "high" : issue.impact_on_containerization === "Medium" ? "medium" : "low") : "none"}">
                <td>${escapeHtml(issue.issue_name)}</td>
                <td class="status-${issue.exists_or_not.toLowerCase()}">${escapeHtml(issue.exists_or_not)}</td>
                <td>${escapeHtml(issue.issue_explanation)}</td>
                <td><span class="badge badge-${issue.impact_on_containerization.toLowerCase()}">${escapeHtml(issue.impact_on_containerization)}</span></td>
                <td>${escapeHtml(issue.recommended_services)}</td>
            </tr>`
    )
    .join("\n");

  const issueCount = result.issues.filter((i) => i.exists_or_not === "Yes").length;
  const highCount = result.issues.filter(
    (i) => i.exists_or_not === "Yes" && i.impact_on_containerization === "High"
  ).length;
  const mediumCount = result.issues.filter(
    (i) => i.exists_or_not === "Yes" && i.impact_on_containerization === "Medium"
  ).length;
  const lowCount = result.issues.filter(
    (i) => i.exists_or_not === "Yes" && i.impact_on_containerization === "Low"
  ).length;

  return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Container Blocker Analysis - ${escapeHtml(result.app_name)}</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background-color: #f0f2f5;
            color: #1a1a2e;
            line-height: 1.6;
            padding: 40px 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: #ffffff;
            border-radius: 12px;
            box-shadow: 0 4px 24px rgba(0, 0, 0, 0.08);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
            color: white;
            padding: 32px 40px;
        }
        .header h1 { font-size: 28px; font-weight: 700; margin-bottom: 8px; }
        .header p { font-size: 15px; opacity: 0.85; }
        .stats {
            display: flex;
            gap: 16px;
            padding: 24px 40px;
            background: #f8f9fa;
            border-bottom: 1px solid #e9ecef;
            flex-wrap: wrap;
        }
        .stat-card {
            background: white;
            border-radius: 8px;
            padding: 16px 24px;
            flex: 1;
            min-width: 140px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
            border-left: 4px solid #dee2e6;
        }
        .stat-card.high { border-left-color: #dc3545; }
        .stat-card.medium { border-left-color: #fd7e14; }
        .stat-card.low { border-left-color: #28a745; }
        .stat-card.total { border-left-color: #007bff; }
        .stat-card .stat-value { font-size: 28px; font-weight: 700; }
        .stat-card .stat-label { font-size: 13px; color: #6c757d; text-transform: uppercase; letter-spacing: 0.5px; }
        .content { padding: 24px 40px 40px; }
        ${result.blocker_type ? `.blocker-type {
            display: inline-block;
            background: #e3f2fd;
            color: #1565c0;
            padding: 6px 16px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: 500;
            margin-bottom: 20px;
        }` : ""}
        table {
            width: 100%;
            border-collapse: separate;
            border-spacing: 0;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            overflow: hidden;
        }
        th {
            background: #f8f9fa;
            padding: 14px 16px;
            text-align: left;
            font-weight: 600;
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: #495057;
            border-bottom: 2px solid #dee2e6;
        }
        td {
            padding: 14px 16px;
            border-bottom: 1px solid #f0f0f0;
            font-size: 14px;
            vertical-align: top;
        }
        tr:last-child td { border-bottom: none; }
        tr:hover td { background-color: #f8f9fa; }
        tr.high td { background-color: #fff5f5; }
        tr.medium td { background-color: #fff8f0; }
        tr.none td { opacity: 0.65; }
        .badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
        }
        .badge-high { background: #fee2e2; color: #991b1b; }
        .badge-medium { background: #ffedd5; color: #9a3412; }
        .badge-low { background: #dcfce7; color: #166534; }
        .status-yes { color: #dc3545; font-weight: 600; }
        .status-no { color: #28a745; font-weight: 600; }
        .summary {
            margin-top: 24px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
            border-left: 4px solid #007bff;
        }
        .summary h3 { margin-bottom: 8px; color: #2c5364; }
        .footer {
            text-align: center;
            padding: 20px;
            color: #adb5bd;
            font-size: 12px;
            border-top: 1px solid #f0f0f0;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Container Blocker Analysis Report</h1>
            <p>Application: ${escapeHtml(result.app_name)} | Generated: ${new Date().toISOString().split("T")[0]}</p>
        </div>
        <div class="stats">
            <div class="stat-card total">
                <div class="stat-value">${issueCount}</div>
                <div class="stat-label">Issues Found</div>
            </div>
            <div class="stat-card high">
                <div class="stat-value">${highCount}</div>
                <div class="stat-label">High Impact</div>
            </div>
            <div class="stat-card medium">
                <div class="stat-value">${mediumCount}</div>
                <div class="stat-label">Medium Impact</div>
            </div>
            <div class="stat-card low">
                <div class="stat-value">${lowCount}</div>
                <div class="stat-label">Low Impact</div>
            </div>
        </div>
        <div class="content">
            ${result.blocker_type ? `<div class="blocker-type">Blocker Type: ${escapeHtml(result.blocker_type)}</div>` : ""}
            <table>
                <thead>
                    <tr>
                        <th>Issue Name</th>
                        <th>Exists</th>
                        <th>Issue Explanation</th>
                        <th>Impact on Containerization</th>
                        <th>Recommended Services</th>
                    </tr>
                </thead>
                <tbody>
                    ${tableRows}
                </tbody>
            </table>
            ${result.summary ? `<div class="summary"><h3>Summary</h3><p>${escapeHtml(result.summary)}</p></div>` : ""}
        </div>
        <div class="footer">
            Generated by Container Blocker Analysis MCP Server
        </div>
    </div>
</body>
</html>`;
}

export function generateSolutionHTML(
  appName: string,
  blockerType: string,
  solutionContent: string
): string {
  return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Solution Report - ${escapeHtml(blockerType)}</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background-color: #f0f2f5;
            color: #1a1a2e;
            line-height: 1.8;
            padding: 40px 20px;
        }
        .container {
            max-width: 900px;
            margin: 0 auto;
            padding: 40px;
            background: #ffffff;
            box-shadow: 0 4px 24px rgba(0, 0, 0, 0.08);
            border-radius: 12px;
        }
        h1 { font-size: 28px; text-align: center; margin-bottom: 8px; color: #2c5364; }
        .subtitle { text-align: center; color: #6c757d; margin-bottom: 32px; font-size: 14px; }
        h2 {
            font-size: 20px;
            margin-top: 28px;
            margin-bottom: 12px;
            color: #203a43;
            border-bottom: 2px solid #e9ecef;
            padding-bottom: 8px;
        }
        p { margin: 10px 0; font-size: 15px; color: #495057; }
        ul, ol { margin: 10px 0 10px 24px; }
        li { margin-bottom: 6px; font-size: 15px; color: #495057; }
        pre {
            background: #f4f4f4;
            padding: 16px;
            border-radius: 8px;
            overflow-x: auto;
            font-size: 13px;
            line-height: 1.5;
            border: 1px solid #e9ecef;
        }
        code { background: #f4f4f4; padding: 2px 6px; border-radius: 4px; font-size: 13px; }
        .highlight {
            background-color: #e3f2fd;
            padding: 16px;
            border-left: 4px solid #1565c0;
            border-radius: 4px;
            margin: 16px 0;
        }
        .footer {
            text-align: center;
            padding-top: 24px;
            margin-top: 32px;
            color: #adb5bd;
            font-size: 12px;
            border-top: 1px solid #f0f0f0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Solution Report</h1>
        <p class="subtitle">Application: ${escapeHtml(appName)} | Blocker: ${escapeHtml(blockerType)}</p>
        ${solutionContent}
        <div class="footer">
            Generated by Container Blocker Analysis MCP Server
        </div>
    </div>
</body>
</html>`;
}

// --- PDF Generation using pdf-lib ---

function wrapText(text: string, font: PDFFont, fontSize: number, maxWidth: number): string[] {
  const words = text.split(/\s+/);
  const lines: string[] = [];
  let currentLine = "";

  for (const word of words) {
    const testLine = currentLine ? `${currentLine} ${word}` : word;
    const width = font.widthOfTextAtSize(testLine, fontSize);
    if (width > maxWidth && currentLine) {
      lines.push(currentLine);
      currentLine = word;
    } else {
      currentLine = testLine;
    }
  }
  if (currentLine) lines.push(currentLine);
  return lines.length > 0 ? lines : [""];
}

interface PDFContext {
  doc: PDFDocument;
  page: PDFPage;
  y: number;
  font: PDFFont;
  boldFont: PDFFont;
  pageWidth: number;
  pageHeight: number;
  margin: number;
}

function ensureSpace(ctx: PDFContext, needed: number): PDFContext {
  if (ctx.y - needed < ctx.margin) {
    const newPage = ctx.doc.addPage([ctx.pageWidth, ctx.pageHeight]);
    return { ...ctx, page: newPage, y: ctx.pageHeight - ctx.margin };
  }
  return ctx;
}

export async function generateAnalysisPDF(result: AnalysisResult): Promise<Uint8Array> {
  const doc = await PDFDocument.create();
  const font = await doc.embedFont(StandardFonts.Helvetica);
  const boldFont = await doc.embedFont(StandardFonts.HelveticaBold);

  const pageWidth = 842; // A4 landscape for table
  const pageHeight = 595;
  const margin = 40;
  const contentWidth = pageWidth - 2 * margin;

  let page = doc.addPage([pageWidth, pageHeight]);
  let ctx: PDFContext = { doc, page, y: pageHeight - margin, font, boldFont, pageWidth, pageHeight, margin };

  // Title
  ctx.page.drawText("Container Blocker Analysis Report", {
    x: margin,
    y: ctx.y,
    size: 20,
    font: boldFont,
    color: rgb(0.17, 0.24, 0.31),
  });
  ctx.y -= 28;

  // Subtitle
  ctx.page.drawText(`Application: ${result.app_name} | Generated: ${new Date().toISOString().split("T")[0]}`, {
    x: margin,
    y: ctx.y,
    size: 10,
    font,
    color: rgb(0.42, 0.46, 0.49),
  });
  ctx.y -= 24;

  if (result.blocker_type) {
    ctx.page.drawText(`Blocker Type: ${result.blocker_type}`, {
      x: margin,
      y: ctx.y,
      size: 10,
      font: boldFont,
      color: rgb(0.08, 0.4, 0.75),
    });
    ctx.y -= 20;
  }

  // Summary stats
  const issueCount = result.issues.filter((i) => i.exists_or_not === "Yes").length;
  const highCount = result.issues.filter((i) => i.exists_or_not === "Yes" && i.impact_on_containerization === "High").length;
  const mediumCount = result.issues.filter((i) => i.exists_or_not === "Yes" && i.impact_on_containerization === "Medium").length;
  const lowCount = result.issues.filter((i) => i.exists_or_not === "Yes" && i.impact_on_containerization === "Low").length;

  const statsText = `Issues Found: ${issueCount}  |  High: ${highCount}  |  Medium: ${mediumCount}  |  Low: ${lowCount}`;
  ctx.page.drawText(statsText, {
    x: margin,
    y: ctx.y,
    size: 11,
    font: boldFont,
    color: rgb(0.2, 0.2, 0.2),
  });
  ctx.y -= 8;

  // Separator line
  ctx.page.drawLine({
    start: { x: margin, y: ctx.y },
    end: { x: pageWidth - margin, y: ctx.y },
    thickness: 1,
    color: rgb(0.85, 0.85, 0.85),
  });
  ctx.y -= 20;

  // Table header
  const colWidths = [130, 50, 230, 80, 180]; // Adjusted for landscape
  const headers = ["Issue Name", "Exists", "Issue Explanation", "Impact", "Recommended Services"];
  const headerFontSize = 9;
  const cellFontSize = 8;
  const cellPadding = 6;

  function drawTableHeader(ctx: PDFContext) {
    // Header background
    ctx.page.drawRectangle({
      x: margin,
      y: ctx.y - 16,
      width: contentWidth,
      height: 20,
      color: rgb(0.95, 0.95, 0.95),
    });

    let x = margin + cellPadding;
    for (let i = 0; i < headers.length; i++) {
      ctx.page.drawText(headers[i], {
        x,
        y: ctx.y - 12,
        size: headerFontSize,
        font: boldFont,
        color: rgb(0.29, 0.33, 0.37),
      });
      x += colWidths[i];
    }
    ctx.y -= 24;
    return ctx;
  }

  ctx = drawTableHeader(ctx);

  // Table rows
  for (const issue of result.issues) {
    const cellTexts = [
      issue.issue_name,
      issue.exists_or_not,
      issue.issue_explanation,
      issue.impact_on_containerization,
      issue.recommended_services,
    ];

    // Calculate row height based on wrapped text
    const wrappedCells = cellTexts.map((text, i) =>
      wrapText(text, font, cellFontSize, colWidths[i] - 2 * cellPadding)
    );
    const maxLines = Math.max(...wrappedCells.map((c) => c.length));
    const rowHeight = maxLines * (cellFontSize + 3) + 2 * cellPadding;

    // Check if we need a new page
    ctx = ensureSpace(ctx, rowHeight + 30);
    if (ctx.y === ctx.pageHeight - ctx.margin) {
      ctx = drawTableHeader(ctx);
    }

    // Row background for high impact issues
    if (issue.exists_or_not === "Yes" && issue.impact_on_containerization === "High") {
      ctx.page.drawRectangle({
        x: margin,
        y: ctx.y - rowHeight + cellPadding,
        width: contentWidth,
        height: rowHeight,
        color: rgb(1, 0.96, 0.96),
      });
    }

    // Draw cell text
    let x = margin + cellPadding;
    for (let i = 0; i < wrappedCells.length; i++) {
      const lines = wrappedCells[i];
      let cellY = ctx.y;

      // Color coding for exists and impact columns
      let textColor = rgb(0.2, 0.2, 0.2);
      if (i === 1) {
        textColor = issue.exists_or_not === "Yes" ? rgb(0.86, 0.21, 0.27) : rgb(0.16, 0.65, 0.27);
      } else if (i === 3) {
        if (issue.impact_on_containerization === "High") textColor = rgb(0.86, 0.21, 0.27);
        else if (issue.impact_on_containerization === "Medium") textColor = rgb(0.99, 0.49, 0.08);
        else textColor = rgb(0.16, 0.65, 0.27);
      }

      const cellFont = i === 1 || i === 3 ? boldFont : font;

      for (const line of lines) {
        ctx.page.drawText(line, {
          x,
          y: cellY,
          size: cellFontSize,
          font: cellFont,
          color: textColor,
        });
        cellY -= cellFontSize + 3;
      }
      x += colWidths[i];
    }

    ctx.y -= rowHeight;

    // Row separator
    ctx.page.drawLine({
      start: { x: margin, y: ctx.y + cellPadding },
      end: { x: pageWidth - margin, y: ctx.y + cellPadding },
      thickness: 0.5,
      color: rgb(0.9, 0.9, 0.9),
    });
  }

  // Summary section
  if (result.summary) {
    ctx.y -= 16;
    ctx = ensureSpace(ctx, 60);

    ctx.page.drawText("Summary", {
      x: margin,
      y: ctx.y,
      size: 13,
      font: boldFont,
      color: rgb(0.17, 0.33, 0.39),
    });
    ctx.y -= 16;

    const summaryLines = wrapText(result.summary, font, 10, contentWidth);
    for (const line of summaryLines) {
      ctx = ensureSpace(ctx, 16);
      ctx.page.drawText(line, {
        x: margin,
        y: ctx.y,
        size: 10,
        font,
        color: rgb(0.29, 0.33, 0.37),
      });
      ctx.y -= 14;
    }
  }

  // Footer on last page
  ctx.page.drawText("Generated by Container Blocker Analysis MCP Server", {
    x: margin,
    y: margin - 20,
    size: 8,
    font,
    color: rgb(0.68, 0.71, 0.74),
  });

  return doc.save();
}

function escapeHtml(text: string): string {
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
