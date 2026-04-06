"""Utilities for generating HTML and PDF reports for containerization analysis."""

import html
from dataclasses import dataclass
from datetime import date
from io import BytesIO
from typing import Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch, mm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


@dataclass
class ContainerizationIssue:
    """A single containerization blocker issue."""

    issue_name: str
    exists_or_not: str  # "Yes" or "No"
    issue_explanation: str
    impact_on_containerization: str  # "Low", "Medium", or "High"
    recommended_services: str


@dataclass
class AnalysisResult:
    """Complete analysis result."""

    app_name: str
    issues: list[ContainerizationIssue]
    blocker_type: Optional[str] = None
    summary: Optional[str] = None


def _escape(text: str) -> str:
    return html.escape(text)


def generate_analysis_html(result: AnalysisResult) -> str:
    """Generate a styled HTML report from analysis results."""
    yes_issues = [i for i in result.issues if i.exists_or_not == "Yes"]
    issue_count = len(yes_issues)
    high_count = sum(1 for i in yes_issues if i.impact_on_containerization == "High")
    medium_count = sum(1 for i in yes_issues if i.impact_on_containerization == "Medium")
    low_count = sum(1 for i in yes_issues if i.impact_on_containerization == "Low")

    table_rows = ""
    for issue in result.issues:
        if issue.exists_or_not == "Yes":
            row_class = {
                "High": "high", "Medium": "medium", "Low": "low"
            }.get(issue.impact_on_containerization, "low")
        else:
            row_class = "none"

        table_rows += f"""
            <tr class="{row_class}">
                <td>{_escape(issue.issue_name)}</td>
                <td class="status-{issue.exists_or_not.lower()}">{_escape(issue.exists_or_not)}</td>
                <td>{_escape(issue.issue_explanation)}</td>
                <td><span class="badge badge-{issue.impact_on_containerization.lower()}">{_escape(issue.impact_on_containerization)}</span></td>
                <td>{_escape(issue.recommended_services)}</td>
            </tr>"""

    blocker_type_html = ""
    if result.blocker_type:
        blocker_type_html = f'<div class="blocker-type">Blocker Type: {_escape(result.blocker_type)}</div>'

    blocker_type_css = ""
    if result.blocker_type:
        blocker_type_css = """.blocker-type {
            display: inline-block;
            background: #e3f2fd;
            color: #1565c0;
            padding: 6px 16px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: 500;
            margin-bottom: 20px;
        }"""

    summary_html = ""
    if result.summary:
        summary_html = f'<div class="summary"><h3>Summary</h3><p>{_escape(result.summary)}</p></div>'

    today = date.today().isoformat()

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Container Blocker Analysis - {_escape(result.app_name)}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background-color: #f0f2f5;
            color: #1a1a2e;
            line-height: 1.6;
            padding: 40px 20px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: #ffffff;
            border-radius: 12px;
            box-shadow: 0 4px 24px rgba(0, 0, 0, 0.08);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
            color: white;
            padding: 32px 40px;
        }}
        .header h1 {{ font-size: 28px; font-weight: 700; margin-bottom: 8px; }}
        .header p {{ font-size: 15px; opacity: 0.85; }}
        .stats {{
            display: flex;
            gap: 16px;
            padding: 24px 40px;
            background: #f8f9fa;
            border-bottom: 1px solid #e9ecef;
            flex-wrap: wrap;
        }}
        .stat-card {{
            background: white;
            border-radius: 8px;
            padding: 16px 24px;
            flex: 1;
            min-width: 140px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
            border-left: 4px solid #dee2e6;
        }}
        .stat-card.high {{ border-left-color: #dc3545; }}
        .stat-card.medium {{ border-left-color: #fd7e14; }}
        .stat-card.low {{ border-left-color: #28a745; }}
        .stat-card.total {{ border-left-color: #007bff; }}
        .stat-card .stat-value {{ font-size: 28px; font-weight: 700; }}
        .stat-card .stat-label {{ font-size: 13px; color: #6c757d; text-transform: uppercase; letter-spacing: 0.5px; }}
        .content {{ padding: 24px 40px 40px; }}
        {blocker_type_css}
        table {{
            width: 100%;
            border-collapse: separate;
            border-spacing: 0;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            overflow: hidden;
        }}
        th {{
            background: #f8f9fa;
            padding: 14px 16px;
            text-align: left;
            font-weight: 600;
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: #495057;
            border-bottom: 2px solid #dee2e6;
        }}
        td {{
            padding: 14px 16px;
            border-bottom: 1px solid #f0f0f0;
            font-size: 14px;
            vertical-align: top;
        }}
        tr:last-child td {{ border-bottom: none; }}
        tr:hover td {{ background-color: #f8f9fa; }}
        tr.high td {{ background-color: #fff5f5; }}
        tr.medium td {{ background-color: #fff8f0; }}
        tr.none td {{ opacity: 0.65; }}
        .badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
        }}
        .badge-high {{ background: #fee2e2; color: #991b1b; }}
        .badge-medium {{ background: #ffedd5; color: #9a3412; }}
        .badge-low {{ background: #dcfce7; color: #166534; }}
        .status-yes {{ color: #dc3545; font-weight: 600; }}
        .status-no {{ color: #28a745; font-weight: 600; }}
        .summary {{
            margin-top: 24px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
            border-left: 4px solid #007bff;
        }}
        .summary h3 {{ margin-bottom: 8px; color: #2c5364; }}
        .footer {{
            text-align: center;
            padding: 20px;
            color: #adb5bd;
            font-size: 12px;
            border-top: 1px solid #f0f0f0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Container Blocker Analysis Report</h1>
            <p>Application: {_escape(result.app_name)} | Generated: {today}</p>
        </div>
        <div class="stats">
            <div class="stat-card total">
                <div class="stat-value">{issue_count}</div>
                <div class="stat-label">Issues Found</div>
            </div>
            <div class="stat-card high">
                <div class="stat-value">{high_count}</div>
                <div class="stat-label">High Impact</div>
            </div>
            <div class="stat-card medium">
                <div class="stat-value">{medium_count}</div>
                <div class="stat-label">Medium Impact</div>
            </div>
            <div class="stat-card low">
                <div class="stat-value">{low_count}</div>
                <div class="stat-label">Low Impact</div>
            </div>
        </div>
        <div class="content">
            {blocker_type_html}
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
                    {table_rows}
                </tbody>
            </table>
            {summary_html}
        </div>
        <div class="footer">
            Generated by Container Blocker Analysis MCP Server
        </div>
    </div>
</body>
</html>"""


def generate_solution_html(
    app_name: str,
    blocker_type: str,
    solution_content: str,
) -> str:
    """Generate a styled HTML solution report."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Solution Report - {_escape(blocker_type)}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background-color: #f0f2f5;
            color: #1a1a2e;
            line-height: 1.8;
            padding: 40px 20px;
        }}
        .container {{
            max-width: 900px;
            margin: 0 auto;
            padding: 40px;
            background: #ffffff;
            box-shadow: 0 4px 24px rgba(0, 0, 0, 0.08);
            border-radius: 12px;
        }}
        h1 {{ font-size: 28px; text-align: center; margin-bottom: 8px; color: #2c5364; }}
        .subtitle {{ text-align: center; color: #6c757d; margin-bottom: 32px; font-size: 14px; }}
        h2 {{
            font-size: 20px;
            margin-top: 28px;
            margin-bottom: 12px;
            color: #203a43;
            border-bottom: 2px solid #e9ecef;
            padding-bottom: 8px;
        }}
        p {{ margin: 10px 0; font-size: 15px; color: #495057; }}
        ul, ol {{ margin: 10px 0 10px 24px; }}
        li {{ margin-bottom: 6px; font-size: 15px; color: #495057; }}
        pre {{
            background: #f4f4f4;
            padding: 16px;
            border-radius: 8px;
            overflow-x: auto;
            font-size: 13px;
            line-height: 1.5;
            border: 1px solid #e9ecef;
        }}
        code {{ background: #f4f4f4; padding: 2px 6px; border-radius: 4px; font-size: 13px; }}
        .highlight {{
            background-color: #e3f2fd;
            padding: 16px;
            border-left: 4px solid #1565c0;
            border-radius: 4px;
            margin: 16px 0;
        }}
        .footer {{
            text-align: center;
            padding-top: 24px;
            margin-top: 32px;
            color: #adb5bd;
            font-size: 12px;
            border-top: 1px solid #f0f0f0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Solution Report</h1>
        <p class="subtitle">Application: {_escape(app_name)} | Blocker: {_escape(blocker_type)}</p>
        {solution_content}
        <div class="footer">
            Generated by Container Blocker Analysis MCP Server
        </div>
    </div>
</body>
</html>"""


def generate_analysis_pdf(result: AnalysisResult) -> bytes:
    """Generate a PDF report from analysis results using ReportLab."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        leftMargin=20 * mm,
        rightMargin=20 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Title"],
        fontSize=22,
        textColor=colors.HexColor("#2c5364"),
        spaceAfter=6,
    )
    subtitle_style = ParagraphStyle(
        "CustomSubtitle",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.HexColor("#6c757d"),
        spaceAfter=16,
    )
    cell_style = ParagraphStyle(
        "CellStyle",
        parent=styles["Normal"],
        fontSize=8,
        leading=11,
    )
    header_cell_style = ParagraphStyle(
        "HeaderCellStyle",
        parent=styles["Normal"],
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#495057"),
        fontName="Helvetica-Bold",
    )
    summary_style = ParagraphStyle(
        "SummaryStyle",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.HexColor("#495057"),
        leading=14,
        spaceBefore=12,
    )

    elements = []

    # Title
    elements.append(Paragraph("Container Blocker Analysis Report", title_style))
    today = date.today().isoformat()
    elements.append(
        Paragraph(f"Application: {_escape(result.app_name)} | Generated: {today}", subtitle_style)
    )

    if result.blocker_type:
        bt_style = ParagraphStyle(
            "BlockerType",
            parent=styles["Normal"],
            fontSize=10,
            textColor=colors.HexColor("#1565c0"),
            fontName="Helvetica-Bold",
            spaceAfter=12,
        )
        elements.append(Paragraph(f"Blocker Type: {_escape(result.blocker_type)}", bt_style))

    # Stats
    yes_issues = [i for i in result.issues if i.exists_or_not == "Yes"]
    issue_count = len(yes_issues)
    high_count = sum(1 for i in yes_issues if i.impact_on_containerization == "High")
    medium_count = sum(1 for i in yes_issues if i.impact_on_containerization == "Medium")
    low_count = sum(1 for i in yes_issues if i.impact_on_containerization == "Low")

    stats_style = ParagraphStyle(
        "Stats",
        parent=styles["Normal"],
        fontSize=11,
        fontName="Helvetica-Bold",
        spaceAfter=16,
    )
    elements.append(
        Paragraph(
            f"Issues Found: {issue_count} &nbsp;|&nbsp; "
            f'<font color="#dc3545">High: {high_count}</font> &nbsp;|&nbsp; '
            f'<font color="#fd7e14">Medium: {medium_count}</font> &nbsp;|&nbsp; '
            f'<font color="#28a745">Low: {low_count}</font>',
            stats_style,
        )
    )

    # Table
    col_widths = [120, 40, 250, 70, 200]  # Landscape A4 gives us ~760 usable
    header_row = [
        Paragraph("Issue Name", header_cell_style),
        Paragraph("Exists", header_cell_style),
        Paragraph("Issue Explanation", header_cell_style),
        Paragraph("Impact", header_cell_style),
        Paragraph("Recommended Services", header_cell_style),
    ]

    data = [header_row]
    row_colors = []

    for issue in result.issues:
        # Color coding for impact
        exists_color = "#dc3545" if issue.exists_or_not == "Yes" else "#28a745"
        impact_color_map = {"High": "#dc3545", "Medium": "#fd7e14", "Low": "#28a745"}
        impact_color = impact_color_map.get(issue.impact_on_containerization, "#333333")

        row = [
            Paragraph(_escape(issue.issue_name), cell_style),
            Paragraph(f'<font color="{exists_color}"><b>{_escape(issue.exists_or_not)}</b></font>', cell_style),
            Paragraph(_escape(issue.issue_explanation), cell_style),
            Paragraph(f'<font color="{impact_color}"><b>{_escape(issue.impact_on_containerization)}</b></font>', cell_style),
            Paragraph(_escape(issue.recommended_services), cell_style),
        ]
        data.append(row)

        # Track row background colors
        if issue.exists_or_not == "Yes" and issue.impact_on_containerization == "High":
            row_colors.append(colors.HexColor("#fff5f5"))
        elif issue.exists_or_not == "Yes" and issue.impact_on_containerization == "Medium":
            row_colors.append(colors.HexColor("#fff8f0"))
        else:
            row_colors.append(colors.white)

    table = Table(data, colWidths=col_widths, repeatRows=1)

    # Table styling
    style_commands = [
        # Header
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f8f9fa")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#495057")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
        ("TOPPADDING", (0, 0), (-1, 0), 10),
        # All cells
        ("FONTSIZE", (0, 1), (-1, -1), 8),
        ("TOPPADDING", (0, 1), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        # Grid
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e9ecef")),
        ("LINEBELOW", (0, 0), (-1, 0), 1.5, colors.HexColor("#dee2e6")),
    ]

    # Apply row background colors
    for idx, bg_color in enumerate(row_colors):
        style_commands.append(("BACKGROUND", (0, idx + 1), (-1, idx + 1), bg_color))

    table.setStyle(TableStyle(style_commands))
    elements.append(table)

    # Summary
    if result.summary:
        elements.append(Spacer(1, 16))
        elements.append(
            Paragraph(f"<b>Summary:</b> {_escape(result.summary)}", summary_style)
        )

    # Footer
    footer_style = ParagraphStyle(
        "Footer",
        parent=styles["Normal"],
        fontSize=8,
        textColor=colors.HexColor("#adb5bd"),
        alignment=1,  # center
        spaceBefore=24,
    )
    elements.append(Spacer(1, 20))
    elements.append(
        Paragraph("Generated by Container Blocker Analysis MCP Server", footer_style)
    )

    doc.build(elements)
    return buffer.getvalue()
