# frontend/pages/data_upload.py
"""Data Upload & Management Page."""
import streamlit as st
import pandas as pd
import numpy as np
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def show_data_upload():
    st.markdown('<h1 class="page-title">📂 Data Management</h1>', unsafe_allow_html=True)
    st.markdown('<p class="page-subtitle">Upload and manage your business datasets</p>', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["⬆️ Upload Dataset", "📋 My Datasets", "🔍 Data Explorer"])

    with tab1:
        col_up, col_info = st.columns([3, 2])
        with col_up:
            st.markdown("#### Upload Your Business Data")
            uploaded_file = st.file_uploader("Choose a file", type=["csv","xlsx","xls","json"], help="Max 100MB")
            dataset_name = st.text_input("📝 Dataset Name", placeholder="e.g. Q1 Sales 2024")
            dataset_desc = st.text_area("📋 Description (optional)", height=70)

            if uploaded_file and dataset_name:
                if st.button("🚀 Upload & Process", use_container_width=True):
                    with st.spinner("⚙️ Processing..."):
                        try:
                            ext = uploaded_file.name.split(".")[-1].lower()
                            if ext == "csv":
                                df = pd.read_csv(uploaded_file)
                            elif ext in ["xlsx","xls"]:
                                df = pd.read_excel(uploaded_file)
                            else:
                                df = pd.read_json(uploaded_file)
                            os.makedirs("./uploads", exist_ok=True)
                            fp = f"./uploads/{dataset_name.replace(' ','_')}.csv"
                            df.to_csv(fp, index=False)
                            ds_info = {"name": dataset_name, "description": dataset_desc,
                                       "file_path": fp, "file_type": ext,
                                       "file_size_mb": round(uploaded_file.size/1024/1024, 2),
                                       "row_count": len(df), "column_count": len(df.columns),
                                       "columns": list(df.columns), "status": "ready"}
                            st.session_state.current_dataset = ds_info
                            if "datasets" not in st.session_state:
                                st.session_state.datasets = []
                            st.session_state.datasets.append(ds_info)
                            st.success(f"✅ {dataset_name} uploaded! {len(df):,} rows × {len(df.columns)} columns")
                        except Exception as e:
                            st.error(f"❌ Error: {e}")

        with col_info:
            st.markdown("#### Supported Formats")
            for fmt, desc in [("📄 CSV","Comma-separated values"),("📊 Excel",".xlsx / .xls files"),("📋 JSON","JSON arrays or objects")]:
                st.markdown(f'<div style="background:rgba(30,41,59,0.5);border:1px solid rgba(99,102,241,0.2);border-radius:8px;padding:0.75rem;margin-bottom:0.5rem;"><b style="color:#F1F5F9">{fmt}</b><br><span style="font-size:0.78rem;color:#64748B">{desc}</span></div>', unsafe_allow_html=True)

            st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
            st.markdown("**Load Demo Dataset:**")
            if st.button("📊 Load E-Commerce Demo", use_container_width=True):
                n = 1000
                np.random.seed(42)
                demo = pd.DataFrame({
                    "date": pd.date_range("2023-01-01", periods=n, freq="D"),
                    "revenue": np.maximum(500, 10000 + np.cumsum(np.random.randn(n)*300) + 2000*np.sin(2*np.pi*np.arange(n)/365)),
                    "quantity": np.random.randint(5, 200, n),
                    "product": np.random.choice(["Electronics","Clothing","Food & Bev","Home & Garden","Sports"], n),
                    "region": np.random.choice(["Dhaka","Chittagong","Rajshahi","Sylhet","Khulna"], n),
                    "customer_id": np.random.randint(1000, 8000, n),
                    "profit_margin": np.random.uniform(0.08, 0.45, n),
                })
                demo["profit"] = demo["revenue"] * demo["profit_margin"]
                os.makedirs("./uploads", exist_ok=True)
                demo.to_csv("./uploads/ecommerce_demo.csv", index=False)
                st.session_state.current_dataset = {"name":"E-Commerce Demo","file_path":"./uploads/ecommerce_demo.csv","row_count":len(demo),"column_count":len(demo.columns),"columns":list(demo.columns),"status":"ready"}
                st.success("✅ Demo loaded! Go to Dashboard to explore.")
                st.rerun()

    with tab2:
        st.markdown("#### My Datasets")
        current = st.session_state.get("current_dataset")
        datasets = st.session_state.get("datasets", [])
        all_ds = [current] + [d for d in datasets if d and d.get("name") != (current or {}).get("name")] if current else datasets
        if not all_ds:
            st.info("No datasets yet. Upload one above or load the demo.")
        else:
            for i, ds in enumerate(all_ds):
                if not ds:
                    continue
                is_active = current and ds.get("name") == current.get("name")
                border = "rgba(16,185,129,0.4)" if is_active else "rgba(99,102,241,0.2)"
                st.markdown(f"""
                <div style="background:rgba(30,41,59,0.6);border:1px solid {border};border-radius:12px;padding:1rem;margin-bottom:0.6rem;">
                    <b style="color:#F1F5F9">📊 {ds.get('name','')} {'<span style="color:#10B981;font-size:0.7rem">[ACTIVE]</span>' if is_active else ''}</b><br>
                    <span style="font-size:0.78rem;color:#64748B">{ds.get('row_count',0):,} rows · {ds.get('column_count',0)} cols</span>
                </div>""", unsafe_allow_html=True)
                if not is_active:
                    if st.button(f"Set Active", key=f"act_{i}", use_container_width=True):
                        st.session_state.current_dataset = ds
                        st.rerun()

    with tab3:
        st.markdown("#### Data Explorer")
        current = st.session_state.get("current_dataset")
        if current and current.get("file_path") and os.path.exists(current["file_path"]):
            try:
                df = pd.read_csv(current["file_path"])
                st.markdown(f"**{len(df):,}** rows × **{len(df.columns)}** columns")
                cols = st.multiselect("Columns to view", df.columns.tolist(), default=list(df.columns[:7]))
                if cols:
                    st.dataframe(df[cols].head(100), use_container_width=True, hide_index=True)
                st.markdown("#### Statistics")
                st.dataframe(df.select_dtypes(include="number").describe().T.round(3), use_container_width=True)
            except Exception as e:
                st.error(f"Error loading data: {e}")
        else:
            st.info("Upload a dataset or load the demo to explore it here.")
