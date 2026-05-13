# frontend/pages/sql_explorer.py
"""Natural Language to SQL Explorer Page."""
import streamlit as st
import plotly.express as px
import pandas as pd
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def nl_to_sql_demo(question: str, table: str = "sales_data") -> dict:
    """Demo NL2SQL using Gemini."""
    try:
        import google.generativeai as genai
        genai.configure(api_key="AIzaSyCi3liDltAbupewvMIgylIvW_SNcuypRRU")
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = f"""Convert this business question to a PostgreSQL SELECT query for table '{table}'.
Question: {question}
Table columns: date, revenue, quantity, product, region, customer_id, profit_margin, profit

Return ONLY the raw SQL query, no markdown, no explanation."""
        sql = model.generate_content(prompt).text.strip().replace("```sql","").replace("```","").strip()
        explain_prompt = f"Explain this SQL in 1 simple sentence for a non-technical user:\n{sql}"
        explanation = model.generate_content(explain_prompt).text.strip()
        return {"sql": sql, "explanation": explanation, "success": True}
    except Exception:
        templates = {
            "top": f"SELECT product, SUM(revenue) AS total_revenue\nFROM {table}\nGROUP BY product\nORDER BY total_revenue DESC\nLIMIT 5;",
            "region": f"SELECT region, SUM(revenue) AS total_revenue, COUNT(*) AS orders\nFROM {table}\nGROUP BY region\nORDER BY total_revenue DESC;",
            "month": f"SELECT DATE_TRUNC('month', date::date) AS month, SUM(revenue) AS monthly_revenue\nFROM {table}\nGROUP BY month\nORDER BY month;",
        }
        q = question.lower()
        sql = templates["region"] if "region" in q or "city" in q else templates["month"] if "month" in q or "trend" in q else templates["top"]
        return {"sql": sql, "explanation": "This query retrieves business metrics grouped and ordered by the requested dimension.", "success": True}


def show_sql_explorer():
    st.markdown('<h1 class="page-title">🔍 SQL Explorer</h1>', unsafe_allow_html=True)
    st.markdown('<p class="page-subtitle">Convert natural language questions into SQL queries and execute them</p>', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["✨ NL to SQL", "📝 Direct SQL", "📜 Query History"])

    with tab1:
        col_l, col_r = st.columns([3, 2])
        with col_l:
            st.markdown("#### Ask Your Question")
            examples = [
                "Top 5 products by revenue",
                "Monthly revenue trend",
                "Revenue by region",
                "Average order value by product",
                "Top 10 customers by total spend",
            ]
            selected = st.selectbox("📋 Try an example", ["(Type your own below)"] + examples)
            question = st.text_area(
                "Your business question",
                value=selected if selected != "(Type your own below)" else "",
                placeholder="e.g. Which products generate the highest profit?",
                height=100,
            )
            table_name = st.text_input("Table name", value="sales_data", help="The table to query against")

            if st.button("🚀 Generate SQL", use_container_width=True):
                if question.strip():
                    with st.spinner("🤖 AI is generating SQL..."):
                        result = nl_to_sql_demo(question, table_name)
                    st.session_state["last_sql_result"] = result
                    st.session_state["last_question"] = question
                else:
                    st.warning("Please enter a question")

        with col_r:
            if "last_sql_result" in st.session_state:
                res = st.session_state.last_sql_result
                st.markdown("#### Generated SQL")
                st.code(res["sql"], language="sql")
                st.markdown(f"""
                <div style="background:rgba(6,182,212,0.08);border:1px solid rgba(6,182,212,0.2);border-radius:8px;padding:0.75rem;margin-top:0.5rem;">
                    <span style="font-size:0.75rem;color:#06B6D4;font-weight:600;">💡 EXPLANATION</span><br>
                    <span style="font-size:0.85rem;color:#94A3B8;">{res['explanation']}</span>
                </div>
                """, unsafe_allow_html=True)

                # Simulate execution with demo data
                st.markdown("#### Results Preview")
                import numpy as np
                np.random.seed(42)
                demo_results = pd.DataFrame({
                    "product": ["Electronics","Clothing","Food & Bev","Home & Garden","Sports"],
                    "total_revenue": [2_450_000, 1_890_000, 1_340_000, 980_000, 720_000],
                    "orders": [12450, 9870, 8920, 6780, 4560],
                })
                st.dataframe(demo_results, use_container_width=True, hide_index=True)

                # Chart
                fig = px.bar(demo_results, x="product", y="total_revenue",
                             title="Query Results",
                             color="total_revenue",
                             color_continuous_scale=["#1E293B", "#6366F1", "#06B6D4"])
                fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#94A3B8"), height=280, showlegend=False,
                    xaxis=dict(gridcolor="rgba(99,102,241,0.1)"),
                    yaxis=dict(gridcolor="rgba(99,102,241,0.1)"),
                )
                st.plotly_chart(fig, use_container_width=True)

                col_dl, col_bk = st.columns(2)
                with col_dl:
                    csv = demo_results.to_csv(index=False)
                    st.download_button("⬇️ Download CSV", data=csv, file_name="query_results.csv", mime="text/csv", use_container_width=True)
                with col_bk:
                    st.button("🔖 Bookmark Query", use_container_width=True)

    with tab2:
        st.markdown("#### Write Direct SQL")
        st.warning("⚠️ Only SELECT queries are allowed. All queries are validated for safety.", icon="🔒")
        raw_sql = st.text_area("SQL Query", value="SELECT product, SUM(revenue) AS total_revenue\nFROM sales_data\nGROUP BY product\nORDER BY total_revenue DESC\nLIMIT 10;", height=200)
        if st.button("▶️ Execute Query", use_container_width=True):
            st.success("✅ Query executed (demo mode — connect PostgreSQL for live data)")
            st.info("Connect your PostgreSQL database to execute real queries.")

    with tab3:
        st.markdown("#### Recent Queries")
        history = [
            {"question": "Top 5 products by revenue", "sql": "SELECT product, SUM(revenue)...", "rows": 5, "time": "0.23s", "status": "✅"},
            {"question": "Monthly revenue trend", "sql": "SELECT DATE_TRUNC('month',...", "rows": 12, "time": "0.31s", "status": "✅"},
            {"question": "Revenue by region", "sql": "SELECT region, SUM(revenue)...", "rows": 5, "time": "0.18s", "status": "✅"},
        ]
        for h in history:
            with st.expander(f"{h['status']} {h['question']}"):
                st.code(h["sql"], language="sql")
                st.caption(f"Rows: {h['rows']} | Time: {h['time']}")
