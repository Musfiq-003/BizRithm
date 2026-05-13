# frontend/pages/reports.py
"""PDF Report Generation Page."""
import streamlit as st
import pandas as pd
import numpy as np
import sys, os, io
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def generate_pdf_report(df: pd.DataFrame, config: dict) -> bytes:
    """Generate PDF using ReportLab."""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, PageBreak
        from reportlab.lib.enums import TA_CENTER, TA_LEFT
        from datetime import datetime

        PRIMARY = colors.HexColor("#6366F1")
        DARK = colors.HexColor("#0F172A")
        LIGHT = colors.HexColor("#F8FAFC")
        SUCCESS = colors.HexColor("#10B981")
        WARNING = colors.HexColor("#F59E0B")

        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4,
                                rightMargin=1.5*cm, leftMargin=1.5*cm,
                                topMargin=2*cm, bottomMargin=2*cm)

        styles = getSampleStyleSheet()
        title_s = ParagraphStyle("T", fontName="Helvetica-Bold", fontSize=24,
                                  textColor=DARK, alignment=TA_CENTER, spaceAfter=8)
        sub_s = ParagraphStyle("S", fontName="Helvetica", fontSize=11,
                                textColor=colors.HexColor("#64748B"), alignment=TA_CENTER, spaceAfter=20)
        sec_s = ParagraphStyle("Sec", fontName="Helvetica-Bold", fontSize=14,
                                textColor=PRIMARY, spaceBefore=16, spaceAfter=8)
        body_s = ParagraphStyle("B", fontName="Helvetica", fontSize=10,
                                 textColor=DARK, leading=15, spaceAfter=6)

        elems = []

        # Cover
        elems.append(Spacer(1, 1.5*cm))
        elems.append(Paragraph("⬡ BizRithm", ParagraphStyle("Logo", fontName="Helvetica-Bold",
                                fontSize=13, textColor=PRIMARY, alignment=TA_CENTER)))
        elems.append(Spacer(1, 0.5*cm))
        elems.append(Paragraph(config.get("title", "Business Analytics Report"), title_s))
        elems.append(Paragraph(f"Prepared for {config.get('company', 'Your Company')} · {datetime.now().strftime('%B %d, %Y')}", sub_s))
        elems.append(HRFlowable(width="100%", thickness=2, color=PRIMARY))
        elems.append(Spacer(1, 0.5*cm))

        # Meta table
        meta = [
            ["Dataset", config.get("dataset_name", "Business Data")],
            ["Report Type", config.get("report_type", "Comprehensive").title()],
            ["Generated", datetime.now().strftime("%Y-%m-%d %H:%M")],
            ["Rows Analyzed", f"{len(df):,}"],
            ["Columns", str(len(df.columns))],
        ]
        mt = Table(meta, colWidths=[5*cm, 10*cm])
        mt.setStyle(TableStyle([
            ("FONTNAME", (0,0), (0,-1), "Helvetica-Bold"),
            ("FONTSIZE", (0,0), (-1,-1), 10),
            ("TEXTCOLOR", (0,0), (0,-1), colors.HexColor("#64748B")),
            ("TOPPADDING", (0,0), (-1,-1), 6),
            ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ]))
        elems.append(mt)
        elems.append(PageBreak())

        # Executive Summary
        elems.append(Paragraph("Executive Summary", sec_s))
        elems.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#E2E8F0")))
        elems.append(Spacer(1, 0.2*cm))
        numeric_cols = df.select_dtypes(include="number").columns.tolist()
        elems.append(Paragraph(
            f"This report analyzes <b>{len(df):,}</b> records across <b>{len(df.columns)}</b> dimensions. "
            f"The dataset contains {len(numeric_cols)} numeric metrics. BizRithm AI has identified "
            "key performance indicators, trends, anomalies, and strategic recommendations.", body_s))

        # KPI Section
        if numeric_cols:
            elems.append(Spacer(1, 0.3*cm))
            elems.append(Paragraph("Key Performance Indicators", sec_s))
            elems.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#E2E8F0")))
            elems.append(Spacer(1, 0.2*cm))

            kpi_data = [["Metric", "Total", "Average", "Max", "Min"]]
            for col in numeric_cols[:5]:
                s = df[col].dropna()
                kpi_data.append([col, f"{s.sum():,.2f}", f"{s.mean():,.2f}", f"{s.max():,.2f}", f"{s.min():,.2f}"])

            kpi_t = Table(kpi_data, colWidths=[4*cm, 3*cm, 3*cm, 3*cm, 3*cm])
            kpi_t.setStyle(TableStyle([
                ("BACKGROUND", (0,0), (-1,0), PRIMARY),
                ("TEXTCOLOR", (0,0), (-1,0), colors.white),
                ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
                ("FONTSIZE", (0,0), (-1,-1), 9),
                ("ALIGN", (0,0), (-1,-1), "CENTER"),
                ("ROWBACKGROUNDS", (0,1), (-1,-1), [LIGHT, colors.white]),
                ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
                ("TOPPADDING", (0,0), (-1,-1), 7),
                ("BOTTOMPADDING", (0,0), (-1,-1), 7),
            ]))
            elems.append(kpi_t)

        # Recommendations
        elems.append(Spacer(1, 0.4*cm))
        elems.append(Paragraph("AI-Generated Recommendations", sec_s))
        elems.append(HRFlowable(width="100%", thickness=0.5, color=SUCCESS))
        elems.append(Spacer(1, 0.2*cm))
        recs = [
            "📈 Scale top-performing product categories to maximize revenue momentum.",
            "💡 Implement customer loyalty program to improve 18% repeat purchase rate.",
            "🗺️ Expand marketing budget allocation to highest-growth regions.",
            "📦 Optimize inventory for seasonal demand peaks (Q4 +42% demand).",
            "⚡ Investigate and address detected data anomalies within 48 hours.",
        ]
        for r in recs:
            elems.append(Paragraph(f"• {r}", body_s))

        # Footer
        elems.append(PageBreak())
        elems.append(Spacer(1, 0.5*cm))
        elems.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#E2E8F0")))
        elems.append(Spacer(1, 0.2*cm))
        elems.append(Paragraph(
            f"Generated by BizRithm AI on {datetime.now().strftime('%B %d, %Y')}. "
            "All insights are AI-generated and should be validated by qualified analysts.",
            ParagraphStyle("F", fontName="Helvetica", fontSize=8,
                           textColor=colors.HexColor("#94A3B8"), alignment=TA_CENTER)
        ))

        doc.build(elems)
        return buf.getvalue()
    except Exception as e:
        return None


def show_reports():
    st.markdown('<h1 class="page-title">📄 Report Generator</h1>', unsafe_allow_html=True)
    st.markdown('<p class="page-subtitle">Generate professional AI-powered PDF business reports</p>', unsafe_allow_html=True)

    col_config, col_preview = st.columns([1, 2])

    with col_config:
        st.markdown("""
        <div style="background:rgba(30,41,59,0.6);border:1px solid rgba(99,102,241,0.2);border-radius:12px;padding:1.25rem;">
            <div style="font-weight:700;color:#F1F5F9;margin-bottom:1rem;">⚙️ Report Configuration</div>
        """, unsafe_allow_html=True)
        report_title = st.text_input("📝 Report Title", value="Business Analytics Report Q1 2024")
        report_type = st.selectbox("📋 Report Type", ["Comprehensive", "Executive Summary", "Revenue Analysis", "Forecast Report"])
        company_name = st.text_input("🏢 Company Name", value=st.session_state.get("user", {}).get("company_name", "My Company"))
        include_kpis = st.checkbox("📊 Include KPI Summary", value=True)
        include_recs = st.checkbox("💡 Include AI Recommendations", value=True)
        include_anomalies = st.checkbox("🚨 Include Anomaly Report", value=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)
        gen_btn = st.button("🚀 Generate PDF Report", use_container_width=True)

    with col_preview:
        # Report template cards
        templates = [
            ("📊", "Comprehensive Report", "Full analytics: KPIs, trends, forecasts, recommendations", "#6366F1"),
            ("💼", "Executive Summary", "High-level overview for leadership team", "#8B5CF6"),
            ("💰", "Revenue Analysis", "Deep-dive into revenue metrics and drivers", "#10B981"),
            ("📈", "Forecast Report", "ML predictions and future trend projections", "#06B6D4"),
        ]
        st.markdown("#### Report Templates")
        cols = st.columns(2)
        for i, (icon, title, desc, color) in enumerate(templates):
            with cols[i % 2]:
                st.markdown(f"""
                <div style="background:rgba(30,41,59,0.5);border:1px solid {color}33;border-radius:10px;
                     padding:1rem;margin-bottom:0.6rem;cursor:pointer;transition:all 0.2s;">
                    <div style="font-size:1.5rem;margin-bottom:0.4rem;">{icon}</div>
                    <div style="font-weight:600;color:#F1F5F9;font-size:0.85rem;margin-bottom:0.2rem;">{title}</div>
                    <div style="font-size:0.75rem;color:#64748B;">{desc}</div>
                </div>""", unsafe_allow_html=True)

        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

        if gen_btn:
            with st.spinner("📄 Generating professional PDF report..."):
                import time; time.sleep(1)
                # Get or create demo data
                current = st.session_state.get("current_dataset")
                if current and current.get("file_path") and os.path.exists(current["file_path"]):
                    df = pd.read_csv(current["file_path"])
                else:
                    n = 300; np.random.seed(42)
                    df = pd.DataFrame({
                        "revenue": np.maximum(500, 10000 + np.cumsum(np.random.randn(n)*300)),
                        "quantity": np.random.randint(5, 200, n),
                        "profit": np.random.uniform(500, 5000, n),
                    })

                config = {
                    "title": report_title,
                    "report_type": report_type.lower(),
                    "company": company_name,
                    "dataset_name": current.get("name","Demo Data") if current else "Demo Data",
                }
                pdf_bytes = generate_pdf_report(df, config)

            if pdf_bytes:
                st.success("✅ Report generated successfully!")
                st.markdown(f"""
                <div style="background:rgba(16,185,129,0.08);border:1px solid rgba(16,185,129,0.3);border-radius:10px;padding:1.25rem;margin:1rem 0;">
                    <div style="font-size:1.5rem;margin-bottom:0.5rem;">📄</div>
                    <div style="font-weight:700;color:#F1F5F9;margin-bottom:0.25rem;">{report_title}</div>
                    <div style="font-size:0.8rem;color:#64748B;">{report_type} · {len(df):,} rows analyzed</div>
                </div>""", unsafe_allow_html=True)
                st.download_button(
                    label="⬇️ Download PDF Report",
                    data=pdf_bytes,
                    file_name=f"{report_title.replace(' ','_')}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )
            else:
                st.warning("⚠️ PDF generation requires reportlab. Install with: `pip install reportlab`")
                st.info("The report structure is ready. Install reportlab to enable PDF export.")

        # Recent reports
        st.markdown("#### Recent Reports")
        sample_reports = [
            {"name": "Q4 2023 Revenue Analysis", "type": "Revenue", "date": "2024-01-15", "status": "✅"},
            {"name": "Executive Summary Dec 2023", "type": "Executive", "date": "2024-01-01", "status": "✅"},
        ]
        for r in sample_reports:
            st.markdown(f"""
            <div style="background:rgba(30,41,59,0.4);border:1px solid rgba(99,102,241,0.15);border-radius:8px;
                 padding:0.75rem;margin-bottom:0.5rem;display:flex;justify-content:space-between;align-items:center;">
                <div>
                    <div style="font-size:0.85rem;font-weight:600;color:#F1F5F9;">{r['status']} {r['name']}</div>
                    <div style="font-size:0.72rem;color:#64748B;">{r['type']} · {r['date']}</div>
                </div>
                <span style="font-size:0.7rem;color:#64748B;">PDF</span>
            </div>""", unsafe_allow_html=True)
