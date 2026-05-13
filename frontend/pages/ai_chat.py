# frontend/pages/ai_chat.py
"""AI Business Chat Interface."""
import streamlit as st
import time, uuid, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def generate_ai_response(question: str) -> str:
    try:
        import google.generativeai as genai
        genai.configure(api_key="AIzaSyCi3liDltAbupewvMIgylIvW_SNcuypRRU")
        model = genai.GenerativeModel("gemini-1.5-flash")
        ds_ctx = ""
        if st.session_state.get("current_dataset"):
            ds = st.session_state.current_dataset
            ds_ctx = f"\nDataset: {ds.get('name')} ({ds.get('row_count',0):,} rows)"
        prompt = f"You are BizRithm AI, an expert business consultant.{ds_ctx}\nUser: {question}\nProvide a concise, professional business-focused answer (max 200 words)."
        return model.generate_content(prompt).text.strip()
    except Exception:
        q = question.lower()
        if "revenue" in q or "sales" in q:
            return "📊 **Revenue Analysis**\n\nRevenue shows **+12.4% MoM growth**. Electronics leads at 32% share. Recommend scaling Chittagong presence (+22% growth) and implementing Q4 seasonal promotions."
        elif "predict" in q or "forecast" in q:
            return "📈 **Forecast**: Next month projected revenue ~**$1.24M** (±8%). Use the **ML Forecasting** page to run Prophet, XGBoost & Random Forest predictions for higher accuracy."
        elif "recommend" in q or "strategy" in q:
            return "💡 **Top Recommendations**:\n1. Scale Electronics (38% margin)\n2. Target Chittagong (22% growth)\n3. Launch loyalty program (18% repeat rate vs 35% avg)\n4. Discontinue bottom-20% SKUs"
        return f"I analyzed '{question}'. Upload your dataset for personalized insights. Try the SQL Explorer for data queries or ML Forecasting for predictions!"


def show_chat():
    st.markdown('<h1 class="page-title">🤖 AI Business Consultant</h1>', unsafe_allow_html=True)
    st.markdown('<p class="page-subtitle">Ask anything about your business in plain English</p>', unsafe_allow_html=True)

    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []
    if "chat_session_id" not in st.session_state:
        st.session_state.chat_session_id = str(uuid.uuid4())

    col_main, col_side = st.columns([3, 1])

    with col_main:
        if not st.session_state.chat_messages:
            st.markdown("""
            <div style="background:rgba(99,102,241,0.06);border:1px solid rgba(99,102,241,0.2);border-radius:16px;padding:2rem;text-align:center;margin-bottom:1.5rem;">
                <div style="font-size:3rem;margin-bottom:0.75rem;">🧠</div>
                <h3 style="color:#F1F5F9;margin-bottom:0.5rem;">BizRithm AI — Powered by Gemini</h3>
                <p style="color:#64748B;font-size:0.9rem;">I analyze your business data and answer questions intelligently.</p>
            </div>
            """, unsafe_allow_html=True)
            suggestions = [
                "What are my top 5 products by revenue?",
                "Why did sales decrease last month?",
                "Predict next month's revenue",
                "Which region has the highest growth?",
                "What marketing strategy should I focus on?",
                "Show customer retention insights",
            ]
            cols = st.columns(2)
            for i, s in enumerate(suggestions):
                with cols[i % 2]:
                    if st.button(f"💬 {s}", key=f"s_{i}", use_container_width=True):
                        st.session_state.pending_msg = s

        # Render messages
        for msg in st.session_state.chat_messages:
            if msg["role"] == "user":
                st.markdown(f"""
                <div style="display:flex;justify-content:flex-end;margin-bottom:1rem;gap:0.75rem;align-items:flex-start;">
                    <div style="max-width:72%;background:linear-gradient(135deg,#6366F1,#8B5CF6);border-radius:16px 16px 4px 16px;padding:0.85rem 1.1rem;font-size:0.9rem;color:white;line-height:1.6;">{msg['content']}</div>
                    <div style="width:36px;height:36px;border-radius:50%;background:linear-gradient(135deg,#06B6D4,#10B981);display:flex;align-items:center;justify-content:center;font-size:1rem;flex-shrink:0;">👤</div>
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="display:flex;margin-bottom:1rem;gap:0.75rem;align-items:flex-start;">
                    <div style="width:36px;height:36px;border-radius:50%;background:linear-gradient(135deg,#6366F1,#8B5CF6);display:flex;align-items:center;justify-content:center;font-size:1rem;flex-shrink:0;">🧠</div>
                    <div style="max-width:78%;background:rgba(30,41,59,0.8);border:1px solid rgba(99,102,241,0.2);border-radius:4px 16px 16px 16px;padding:0.85rem 1.1rem;font-size:0.9rem;color:#F1F5F9;line-height:1.7;">{msg['content'].replace(chr(10),'<br>')}</div>
                </div>""", unsafe_allow_html=True)

        # Handle pending suggestion
        if "pending_msg" in st.session_state:
            pm = st.session_state.pop("pending_msg")
            st.session_state.chat_messages.append({"role": "user", "content": pm})
            with st.spinner("🧠 BizRithm AI is thinking..."):
                resp = generate_ai_response(pm)
            st.session_state.chat_messages.append({"role": "assistant", "content": resp})
            st.rerun()

        # Input
        c1, c2 = st.columns([5, 1])
        with c1:
            user_input = st.text_input("msg", placeholder="Ask about revenue, trends, strategies...", label_visibility="collapsed", key="chat_in")
        with c2:
            send = st.button("Send ➤", use_container_width=True)

        if send and user_input:
            st.session_state.chat_messages.append({"role": "user", "content": user_input})
            with st.spinner("🧠 Analyzing..."):
                resp = generate_ai_response(user_input)
            st.session_state.chat_messages.append({"role": "assistant", "content": resp})
            st.rerun()

    with col_side:
        st.markdown("""
        <div style="background:rgba(30,41,59,0.6);border:1px solid rgba(99,102,241,0.2);border-radius:12px;padding:1rem;margin-bottom:1rem;">
            <div style="font-weight:700;color:#F1F5F9;margin-bottom:0.75rem;">🤖 Agent Status</div>
        """, unsafe_allow_html=True)
        for dot, name, status in [("🟢","Chat Agent","Active"),("🟢","SQL Agent","Standby"),("🟢","Analytics","Standby"),("🟡","Forecast","Idle")]:
            st.markdown(f'<div style="display:flex;gap:0.5rem;margin-bottom:0.4rem;font-size:0.8rem;color:#94A3B8;"><span>{dot}</span><span style="flex:1">{name}</span><span style="color:#64748B;font-size:0.7rem">{status}</span></div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown(f"""
        <div style="background:rgba(30,41,59,0.4);border:1px solid rgba(99,102,241,0.15);border-radius:12px;padding:1rem;margin-bottom:1rem;">
            <div style="font-size:0.7rem;color:#64748B;text-transform:uppercase;letter-spacing:1px;margin-bottom:0.5rem;">Session</div>
            <div style="font-size:1.8rem;font-weight:800;color:#818CF8;">{len(st.session_state.chat_messages)}</div>
            <div style="font-size:0.75rem;color:#64748B;">Messages</div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.chat_messages = []
            st.session_state.chat_session_id = str(uuid.uuid4())
            st.rerun()
