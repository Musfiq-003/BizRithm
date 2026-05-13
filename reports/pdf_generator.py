# reports/pdf_generator.py
"""Professional PDF Report Generator using ReportLab."""
import os
import io
from datetime import datetime
from typing import Dict, Any, Optional
import pandas as pd
import numpy as np

from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, Image
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.graphics import renderPDF

from analytics.kpi_calculator import calculate_revenue_kpis
from analytics.trend_analyzer import detect_trend_direction
from analytics.anomaly_detector import detect_all_anomalies
from analytics.recommendation_engine import get_recommendation_engine
from utils.data_processor import detect_numeric_columns, detect_date_columns
from backend.core.logger import logger

# Color Palette
PRIMARY = colors.HexColor("#6366F1")       # Indigo
SECONDARY = colors.HexColor("#8B5CF6")    # Purple
ACCENT = colors.HexColor("#06B6D4")       # Cyan
SUCCESS = colors.HexColor("#10B981")      # Green
WARNING = colors.HexColor("#F59E0B")      # Amber
DANGER = colors.HexColor("#EF4444")       # Red
DARK = colors.HexColor("#0F172A")         # Dark navy
LIGHT_BG = colors.HexColor("#F8FAFC")     # Light gray
CARD_BG = colors.HexColor("#1E293B")      # Dark card


class PDFReportGenerator:
    """Generates professional business analytics PDF reports."""

    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Configure custom paragraph styles."""
        self.title_style = ParagraphStyle(
            "BizTitle",
            fontName="Helvetica-Bold",
            fontSize=28,
            textColor=DARK,
            alignment=TA_CENTER,
            spaceAfter=8,
        )
        self.subtitle_style = ParagraphStyle(
            "BizSubtitle",
            fontName="Helvetica",
            fontSize=12,
            textColor=colors.HexColor("#64748B"),
            alignment=TA_CENTER,
            spaceAfter=20,
        )
        self.section_style = ParagraphStyle(
            "BizSection",
            fontName="Helvetica-Bold",
            fontSize=16,
            textColor=PRIMARY,
            spaceBefore=20,
            spaceAfter=10,
            borderPad=5,
        )
        self.body_style = ParagraphStyle(
            "BizBody",
            fontName="Helvetica",
            fontSize=10,
            textColor=DARK,
            leading=16,
            spaceAfter=8,
            alignment=TA_JUSTIFY,
        )
        self.insight_style = ParagraphStyle(
            "BizInsight",
            fontName="Helvetica",
            fontSize=10,
            textColor=colors.HexColor("#1E40AF"),
            leading=16,
            leftIndent=10,
            borderPad=8,
            backColor=colors.HexColor("#EFF6FF"),
        )
        self.metric_label_style = ParagraphStyle(
            "MetricLabel",
            fontName="Helvetica",
            fontSize=9,
            textColor=colors.HexColor("#64748B"),
            alignment=TA_CENTER,
        )
        self.metric_value_style = ParagraphStyle(
            "MetricValue",
            fontName="Helvetica-Bold",
            fontSize=20,
            textColor=PRIMARY,
            alignment=TA_CENTER,
        )

    async def generate(
        self,
        df: pd.DataFrame,
        output_path: str,
        config: Dict[str, Any],
    ) -> str:
        """Generate full PDF report."""
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=1.5 * cm,
            leftMargin=1.5 * cm,
            topMargin=2 * cm,
            bottomMargin=2 * cm,
        )

        elements = []
        elements.extend(self._build_cover_page(config))
        elements.append(PageBreak())
        elements.extend(self._build_executive_summary(df, config))
        elements.append(PageBreak())
        elements.extend(self._build_kpi_section(df))
        elements.extend(self._build_top_performers_section(df))
        elements.extend(self._build_anomalies_section(df))
        elements.extend(self._build_recommendations_section(df))
        elements.extend(self._build_footer_section(config))

        doc.build(elements, onFirstPage=self._header_footer, onLaterPages=self._header_footer)
        logger.info(f"PDF report generated: {output_path}")
        return output_path

    def _build_cover_page(self, config: Dict) -> list:
        elements = []
        elements.append(Spacer(1, 2 * inch))

        # Logo / Brand name
        elements.append(Paragraph("BizRithm", ParagraphStyle(
            "Brand", fontName="Helvetica-Bold", fontSize=14,
            textColor=PRIMARY, alignment=TA_CENTER
        )))
        elements.append(Spacer(1, 0.3 * inch))

        # Title
        elements.append(Paragraph(config.get("title", "Business Analytics Report"), self.title_style))
        elements.append(Spacer(1, 0.1 * inch))

        # Subtitle
        date_str = datetime.now().strftime("%B %d, %Y")
        elements.append(Paragraph(
            f"Prepared for {config.get('company', 'Your Company')} | {date_str}",
            self.subtitle_style
        ))
        elements.append(Spacer(1, 0.3 * inch))
        elements.append(HRFlowable(width="100%", thickness=2, color=PRIMARY))
        elements.append(Spacer(1, 0.3 * inch))

        # Report metadata table
        meta_data = [
            ["Dataset:", config.get("dataset_name", "Uploaded Dataset")],
            ["Prepared By:", config.get("user_name", "BizRithm AI")],
            ["Report Type:", config.get("report_type", "Comprehensive").title()],
            ["Generated:", datetime.now().strftime("%Y-%m-%d %H:%M")],
            ["Platform:", "BizRithm AI Business Consultant"],
        ]
        meta_table = Table(meta_data, colWidths=[2 * inch, 4 * inch])
        meta_table.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 11),
            ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#64748B")),
            ("TEXTCOLOR", (1, 0), (1, -1), DARK),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        elements.append(meta_table)
        elements.append(Spacer(1, 0.5 * inch))

        # Confidential notice
        elements.append(Paragraph(
            "CONFIDENTIAL — This report contains proprietary business intelligence generated by BizRithm AI.",
            ParagraphStyle("Conf", fontName="Helvetica-Oblique", fontSize=8,
                           textColor=colors.HexColor("#94A3B8"), alignment=TA_CENTER)
        ))
        return elements

    def _build_executive_summary(self, df: pd.DataFrame, config: Dict) -> list:
        elements = []
        elements.append(Paragraph("Executive Summary", self.section_style))
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#E2E8F0")))
        elements.append(Spacer(1, 0.2 * inch))

        numeric_cols = detect_numeric_columns(df)
        date_cols = detect_date_columns(df)

        summary_text = f"""
        This report presents a comprehensive analysis of the dataset "{config.get('dataset_name', 'Business Data')}" 
        containing <b>{len(df):,}</b> records across <b>{len(df.columns)}</b> dimensions. 
        The analysis covers {len(numeric_cols)} numeric metrics and {len(date_cols)} temporal dimensions.
        
        The BizRithm AI engine has processed this data to extract key performance indicators, 
        identify trends and anomalies, and generate actionable business recommendations.
        """
        elements.append(Paragraph(summary_text.strip(), self.body_style))
        elements.append(Spacer(1, 0.2 * inch))

        # Data overview table
        overview_data = [
            ["Metric", "Value"],
            ["Total Records", f"{len(df):,}"],
            ["Total Columns", str(len(df.columns))],
            ["Numeric Columns", str(len(numeric_cols))],
            ["Date Columns", str(len(date_cols))],
            ["Missing Values", f"{int(df.isna().sum().sum()):,}"],
            ["Duplicate Records", f"{int(df.duplicated().sum()):,}"],
        ]
        overview_table = Table(overview_data, colWidths=[3 * inch, 3 * inch])
        overview_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [LIGHT_BG, colors.white]),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("ROUNDEDCORNERS", [4]),
        ]))
        elements.append(overview_table)
        return elements

    def _build_kpi_section(self, df: pd.DataFrame) -> list:
        elements = []
        numeric_cols = detect_numeric_columns(df)
        date_cols = detect_date_columns(df)

        if not numeric_cols:
            return elements

        revenue_col = next(
            (c for c in numeric_cols if any(kw in c.lower() for kw in ["revenue", "sales", "amount", "total"])),
            numeric_cols[0],
        )
        date_col = date_cols[0] if date_cols else None

        elements.append(Spacer(1, 0.3 * inch))
        elements.append(Paragraph("Key Performance Indicators", self.section_style))
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#E2E8F0")))
        elements.append(Spacer(1, 0.2 * inch))

        kpis = calculate_revenue_kpis(df, revenue_col, date_col)

        kpi_data = [
            [
                Paragraph("Total Revenue", self.metric_label_style),
                Paragraph("Avg Transaction", self.metric_label_style),
                Paragraph("Total Transactions", self.metric_label_style),
            ],
            [
                Paragraph(f"${kpis.get('total_revenue', 0):,.0f}", self.metric_value_style),
                Paragraph(f"${kpis.get('avg_revenue', 0):,.0f}", self.metric_value_style),
                Paragraph(f"{len(df):,}", self.metric_value_style),
            ],
        ]

        kpi_table = Table(kpi_data, colWidths=[2.2 * inch, 2.2 * inch, 2.2 * inch])
        kpi_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), LIGHT_BG),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("TOPPADDING", (0, 0), (-1, -1), 12),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
            ("GRID", (0, 0), (-1, -1), 1, colors.white),
            ("ROUNDEDCORNERS", [8]),
        ]))
        elements.append(kpi_table)
        return elements

    def _build_top_performers_section(self, df: pd.DataFrame) -> list:
        elements = []
        elements.append(Spacer(1, 0.3 * inch))
        elements.append(Paragraph("Column Statistics", self.section_style))
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#E2E8F0")))
        elements.append(Spacer(1, 0.2 * inch))

        numeric_cols = detect_numeric_columns(df)[:5]
        if not numeric_cols:
            return elements

        stats_data = [["Column", "Min", "Max", "Mean", "Std Dev"]]
        for col in numeric_cols:
            series = df[col].dropna()
            stats_data.append([
                col,
                f"{series.min():,.2f}",
                f"{series.max():,.2f}",
                f"{series.mean():,.2f}",
                f"{series.std():,.2f}",
            ])

        stats_table = Table(stats_data, colWidths=[2 * inch, 1.5 * inch, 1.5 * inch, 1.5 * inch, 1.5 * inch])
        stats_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), SECONDARY),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [LIGHT_BG, colors.white]),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ("TOPPADDING", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ]))
        elements.append(stats_table)
        return elements

    def _build_anomalies_section(self, df: pd.DataFrame) -> list:
        elements = []
        numeric_cols = detect_numeric_columns(df)
        if not numeric_cols:
            return elements

        anomalies = detect_all_anomalies(df, numeric_cols[:3])[:5]
        if not anomalies:
            return elements

        elements.append(Spacer(1, 0.3 * inch))
        elements.append(Paragraph("⚠ Detected Anomalies", self.section_style))
        elements.append(HRFlowable(width="100%", thickness=1, color=WARNING))
        elements.append(Spacer(1, 0.15 * inch))

        for a in anomalies:
            severity_color = DANGER if a["severity"] == "high" else WARNING
            text = (
                f"<b>{a['column']}</b>: Detected {a['severity']}-severity anomaly. "
                f"Value: {a['value']:,.2f} (Z-score: {a['z_score']:.2f}, "
                f"mean: {a['mean']:,.2f})"
            )
            elements.append(Paragraph(text, ParagraphStyle(
                "AnomalyText", fontName="Helvetica", fontSize=10,
                textColor=severity_color, spaceAfter=6
            )))
        return elements

    def _build_recommendations_section(self, df: pd.DataFrame) -> list:
        elements = []
        elements.append(Spacer(1, 0.3 * inch))
        elements.append(Paragraph("AI-Generated Recommendations", self.section_style))
        elements.append(HRFlowable(width="100%", thickness=1, color=SUCCESS))
        elements.append(Spacer(1, 0.15 * inch))

        rec_engine = get_recommendation_engine()
        recs = rec_engine.generate_recommendations({}, [], {})[:5]

        for i, rec in enumerate(recs, 1):
            icon = rec.get("icon", "•")
            elements.append(Paragraph(
                f"<b>{i}. {icon} {rec['title']}</b>",
                ParagraphStyle("RecTitle", fontName="Helvetica-Bold", fontSize=11,
                               textColor=PRIMARY, spaceBefore=8, spaceAfter=3)
            ))
            elements.append(Paragraph(rec["description"], self.body_style))
            elements.append(Paragraph(
                f"→ <b>Action:</b> {rec['action']}",
                ParagraphStyle("RecAction", fontName="Helvetica-Oblique", fontSize=10,
                               textColor=SUCCESS, leftIndent=10, spaceAfter=8)
            ))

        return elements

    def _build_footer_section(self, config: Dict) -> list:
        elements = []
        elements.append(PageBreak())
        elements.append(Spacer(1, 0.5 * inch))
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#E2E8F0")))
        elements.append(Spacer(1, 0.2 * inch))
        elements.append(Paragraph(
            f"This report was automatically generated by <b>BizRithm AI</b> on "
            f"{datetime.now().strftime('%B %d, %Y at %H:%M')}. "
            f"All insights and recommendations are AI-generated and should be validated by qualified business analysts.",
            ParagraphStyle("Footer", fontName="Helvetica", fontSize=9,
                           textColor=colors.HexColor("#94A3B8"), alignment=TA_CENTER, leading=14)
        ))
        return elements

    def _header_footer(self, canvas, doc):
        """Add header and footer to each page."""
        canvas.saveState()
        # Header
        canvas.setFont("Helvetica-Bold", 9)
        canvas.setFillColor(PRIMARY)
        canvas.drawString(1.5 * cm, A4[1] - 1.2 * cm, "BizRithm AI")
        canvas.setFont("Helvetica", 9)
        canvas.setFillColor(colors.HexColor("#94A3B8"))
        canvas.drawRightString(A4[0] - 1.5 * cm, A4[1] - 1.2 * cm, "Business Analytics Report")
        canvas.setLineWidth(0.5)
        canvas.setStrokeColor(colors.HexColor("#E2E8F0"))
        canvas.line(1.5 * cm, A4[1] - 1.5 * cm, A4[0] - 1.5 * cm, A4[1] - 1.5 * cm)

        # Footer
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#94A3B8"))
        canvas.drawString(1.5 * cm, 1 * cm, f"Generated: {datetime.now().strftime('%Y-%m-%d')}")
        canvas.drawCentredString(A4[0] / 2, 1 * cm, f"Page {doc.page}")
        canvas.drawRightString(A4[0] - 1.5 * cm, 1 * cm, "Confidential")
        canvas.restoreState()
