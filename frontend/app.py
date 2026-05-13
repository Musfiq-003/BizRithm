# frontend/app.py
"""
BizRithm — AI Business Consultant Agent Platform
Main Streamlit Application Entry Point
"""
import streamlit as st
import sys
import os

# Ensure root is in path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ── Page Configuration ────────────────────────────────────────
st.set_page_config(
    page_title="BizRithm — AI Business Consultant",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://bizrithm.ai/docs",
        "Report a bug": "https://bizrithm.ai/issues",
        "About": "BizRithm — AI-Powered Business Intelligence Platform v1.0",
    },
)

# ── Load Custom CSS ───────────────────────────────────────────
def load_css():
    css_path = os.path.join(os.path.dirname(__file__), "styles", "custom.css")
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# ── Session State Init ────────────────────────────────────────
defaults = {
    "authenticated": False,
    "user": None,
    "token": None,
    "current_dataset": None,
    "chat_session_id": None,
    "chat_messages": [],
    "theme": "dark",
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ── Landing / Auth Page ───────────────────────────────────────
def show_landing():
    """Show the landing / login page."""

    # Hero Section
    st.markdown("""
    <div style="text-align:center; padding: 4rem 2rem 2rem;">
        <div style="
            display: inline-block;
            background: linear-gradient(135deg, rgba(99,102,241,0.15), rgba(139,92,246,0.1));
            border: 1px solid rgba(99,102,241,0.3);
            border-radius: 100px;
            padding: 0.4rem 1.2rem;
            margin-bottom: 1.5rem;
            font-size: 0.75rem;
            font-weight: 600;
            color: #818CF8;
            letter-spacing: 2px;
            text-transform: uppercase;
        ">
            🚀 AI-Powered Business Intelligence
        </div>
        <h1 style="
            font-size: 3.5rem;
            font-weight: 900;
            background: linear-gradient(135deg, #F1F5F9, #818CF8, #06B6D4);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            line-height: 1.1;
            margin-bottom: 1rem;
            letter-spacing: -2px;
        ">
            Your AI Business<br/>Consultant
        </h1>
        <p style="
            font-size: 1.2rem;
            color: #94A3B8;
            max-width: 600px;
            margin: 0 auto 2.5rem;
            line-height: 1.7;
        ">
            Upload your business data and interact with an intelligent AI that analyzes performance,
            predicts trends, generates insights, and creates reports — all in real time.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Feature Pills
    features = [
        ("🤖", "AI Chat", "Ask business questions in plain English"),
        ("🔍", "NL to SQL", "Query your data with natural language"),
        ("📈", "ML Forecasting", "Predict revenue & trends with 5 ML models"),
        ("💡", "Auto Insights", "AI-generated business recommendations"),
        ("📊", "Live Dashboard", "Interactive KPI analytics"),
        ("📄", "PDF Reports", "Professional auto-generated reports"),
    ]

    cols = st.columns(3)
    for i, (icon, title, desc) in enumerate(features):
        with cols[i % 3]:
            st.markdown(f"""
            <div style="
                background: rgba(30,41,59,0.6);
                border: 1px solid rgba(99,102,241,0.2);
                border-radius: 12px;
                padding: 1.25rem;
                margin-bottom: 1rem;
                transition: all 0.25s;
            ">
                <div style="font-size: 1.8rem; margin-bottom: 0.5rem;">{icon}</div>
                <div style="font-size: 0.95rem; font-weight: 700; color: #F1F5F9; margin-bottom: 0.25rem;">{title}</div>
                <div style="font-size: 0.8rem; color: #64748B;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='height: 2rem'></div>", unsafe_allow_html=True)

    # Auth Forms
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="
            background: rgba(15,23,42,0.8);
            border: 1px solid rgba(99,102,241,0.25);
            border-radius: 16px;
            padding: 2rem;
            backdrop-filter: blur(16px);
        ">
        """, unsafe_allow_html=True)

        tab1, tab2 = st.tabs(["🔐 Sign In", "✨ Create Account"])

        with tab1:
            st.markdown("#### Welcome back")
            email = st.text_input("Email", placeholder="you@company.com", key="login_email")
            password = st.text_input("Password", type="password", placeholder="••••••••", key="login_pass")

            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("Sign In", use_container_width=True, key="login_btn"):
                    if email and password:
                        # Demo mode: accept any credentials
                        st.session_state.authenticated = True
                        st.session_state.user = {
                            "id": "demo-user-001",
                            "email": email,
                            "username": email.split("@")[0],
                            "full_name": "Demo User",
                            "role": "analyst",
                            "company_name": "BizRithm Demo",
                        }
                        st.session_state.token = "demo-token"
                        st.success("✅ Welcome back!")
                        st.rerun()
                    else:
                        st.error("Please enter your credentials")
            with col_b:
                if st.button("Demo Login", use_container_width=True, key="demo_btn"):
                    st.session_state.authenticated = True
                    st.session_state.user = {
                        "id": "demo-user-001",
                        "email": "demo@bizrithm.ai",
                        "username": "demo",
                        "full_name": "Demo Analyst",
                        "role": "analyst",
                        "company_name": "BizRithm Inc.",
                    }
                    st.session_state.token = "demo-token"
                    st.rerun()

        with tab2:
            st.markdown("#### Get started free")
            reg_name = st.text_input("Full Name", placeholder="John Doe", key="reg_name")
            reg_email = st.text_input("Email", placeholder="you@company.com", key="reg_email")
            reg_company = st.text_input("Company", placeholder="Your Company", key="reg_company")
            reg_pass = st.text_input("Password", type="password", placeholder="Min. 8 characters", key="reg_pass")

            if st.button("Create Account", use_container_width=True, key="reg_btn"):
                if reg_name and reg_email and reg_pass:
                    st.session_state.authenticated = True
                    st.session_state.user = {
                        "id": "new-user-001",
                        "email": reg_email,
                        "username": reg_email.split("@")[0],
                        "full_name": reg_name,
                        "role": "analyst",
                        "company_name": reg_company or "My Company",
                    }
                    st.session_state.token = "demo-token"
                    st.success("✅ Account created!")
                    st.rerun()
                else:
                    st.warning("Please fill in all required fields")

        st.markdown("</div>", unsafe_allow_html=True)


def show_sidebar():
    """Render the main navigation sidebar."""
    with st.sidebar:
        # Logo
        user = st.session_state.get("user", {})
        st.markdown(f"""
        <div style="padding: 1rem; text-align: center; border-bottom: 1px solid rgba(99,102,241,0.2); margin-bottom: 1rem;">
            <div style="
                font-size: 1.6rem;
                font-weight: 900;
                background: linear-gradient(135deg, #6366F1, #06B6D4);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            ">⬡ BizRithm</div>
            <div style="font-size: 0.65rem; color: #64748B; letter-spacing: 2px; text-transform: uppercase;">AI Business Intelligence</div>
        </div>

        <div style="
            background: rgba(99,102,241,0.08);
            border: 1px solid rgba(99,102,241,0.15);
            border-radius: 10px;
            padding: 0.75rem 1rem;
            margin: 0 0.5rem 1rem;
        ">
            <div style="font-size: 0.85rem; font-weight: 600; color: #F1F5F9;">{user.get('full_name', 'User')}</div>
            <div style="font-size: 0.75rem; color: #64748B;">{user.get('email', '')}</div>
            <div style="
                display: inline-block;
                margin-top: 0.4rem;
                padding: 0.15rem 0.6rem;
                background: rgba(16,185,129,0.15);
                border-radius: 100px;
                font-size: 0.65rem;
                font-weight: 600;
                color: #10B981;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            ">{user.get('role', 'analyst')}</div>
        </div>
        """, unsafe_allow_html=True)

        # Navigation
        pages = [
            ("📊", "Dashboard", "Overview & KPIs"),
            ("🤖", "AI Chat", "Business consultant"),
            ("🔍", "SQL Explorer", "NL to SQL queries"),
            ("📈", "ML Forecasting", "Predict & forecast"),
            ("💡", "Insights", "AI recommendations"),
            ("📄", "Reports", "PDF generation"),
            ("📂", "Data Upload", "Manage datasets"),
        ]

        st.markdown("**Navigation**")
        current = st.session_state.get("current_page", "Dashboard")

        for icon, name, desc in pages:
            is_active = current == name
            style = """
                background: linear-gradient(135deg, rgba(99,102,241,0.2), rgba(139,92,246,0.1));
                border: 1px solid rgba(99,102,241,0.3);
                color: #818CF8;
            """ if is_active else "background: transparent; border: 1px solid transparent; color: #94A3B8;"

            if st.button(
                f"{icon}  {name}",
                key=f"nav_{name}",
                use_container_width=True,
                help=desc,
            ):
                st.session_state.current_page = name
                st.rerun()

        st.markdown("<div style='height: 1rem'></div>", unsafe_allow_html=True)
        st.markdown("""<div style="border-top: 1px solid rgba(99,102,241,0.15); margin: 0.5rem 0; padding-top: 0.75rem;">""", unsafe_allow_html=True)

        # Dataset info in sidebar
        if st.session_state.current_dataset:
            ds = st.session_state.current_dataset
            st.markdown(f"""
            <div style="
                background: rgba(6,182,212,0.08);
                border: 1px solid rgba(6,182,212,0.2);
                border-radius: 8px;
                padding: 0.75rem;
                margin: 0.5rem;
            ">
                <div style="font-size: 0.7rem; color: #64748B; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 0.25rem;">Active Dataset</div>
                <div style="font-size: 0.85rem; font-weight: 600; color: #06B6D4;">{ds.get('name', 'Dataset')}</div>
                <div style="font-size: 0.75rem; color: #64748B;">{ds.get('row_count', 0):,} rows</div>
            </div>
            """, unsafe_allow_html=True)

        # Logout
        if st.button("🚪  Sign Out", use_container_width=True, key="logout"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

        # Footer
        st.markdown("""
        <div style="text-align:center; padding-top: 1rem; font-size: 0.7rem; color: #475569;">
            BizRithm v1.0 • Powered by Gemini AI
        </div>
        """, unsafe_allow_html=True)


# ── Main Router ───────────────────────────────────────────────
def main():
    if not st.session_state.authenticated:
        show_landing()
        return

    show_sidebar()

    # Route to the correct page
    page = st.session_state.get("current_page", "Dashboard")

    if page == "Dashboard":
        from frontend.pages.dashboard import show_dashboard
        show_dashboard()
    elif page == "AI Chat":
        from frontend.pages.ai_chat import show_chat
        show_chat()
    elif page == "SQL Explorer":
        from frontend.pages.sql_explorer import show_sql_explorer
        show_sql_explorer()
    elif page == "ML Forecasting":
        from frontend.pages.ml_forecasting import show_ml_forecasting
        show_ml_forecasting()
    elif page == "Insights":
        from frontend.pages.insights import show_insights
        show_insights()
    elif page == "Reports":
        from frontend.pages.reports import show_reports
        show_reports()
    elif page == "Data Upload":
        from frontend.pages.data_upload import show_data_upload
        show_data_upload()


if __name__ == "__main__":
    main()
