"""
Streamlit Dashboard - Week 1 Skeleton
Module 21: Streamlit UI (pages added incrementally)
Currently: Upload + Problem Detection
"""

import streamlit as st
import requests
import json
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Page config
st.set_page_config(
    page_title="Autonomous AI Data Scientist",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# API base URL
API_URL = "http://localhost:8000"

# Custom CSS
st.markdown(
    """
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #0066cc;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        font-size: 1.1rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.25rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 0.25rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 0.25rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================================
# SIDEBAR
# ============================================================================

with st.sidebar:
    st.markdown("## 🚀 Autonomous AI")
    st.markdown("**ML Pipeline v0.1.0**")

    st.divider()

    st.markdown("### 📊 Available Pages")
    page = st.radio(
        "Navigate:",
        [
            "🔼 Upload Data",
            "🔍 Problem Detection",
            "📈 EDA (Coming W2)",
            "⚙️ Model Training (Coming W2)",
            "📊 Results (Coming W3)",
            "💬 Chat with Data (Coming W3)",
            "📄 Report (Coming W4)",
        ],
        label_visibility="collapsed",
    )

    st.divider()

    st.markdown("### ℹ️ Info")
    st.markdown("[GitHub](https://github.com) | [Docs](./docs/)")

    # API Status
    try:
        response = requests.get(f"{API_URL}/health", timeout=2)
        if response.status_code == 200:
            st.success("✅ API Connected")
        else:
            st.error("❌ API Error")
    except:
        st.error("❌ API Offline")


# ============================================================================
# PAGE: UPLOAD DATA (Module 1)
# ============================================================================

if page == "🔼 Upload Data":
    st.markdown(
        '<p class="main-header">📤 Upload Your Dataset</p>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="subtitle">CSV files up to 100MB. System will auto-detect problem type.</p>',
        unsafe_allow_html=True,
    )

    st.divider()

    # Upload section
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Step 1️⃣: Upload CSV")
        uploaded_file = st.file_uploader("Choose CSV file", type="csv", key="csv_upload")

        if uploaded_file is not None:
            st.markdown(f"**File:** {uploaded_file.name}")
            st.markdown(f"**Size:** {uploaded_file.size / 1024:.1f} KB")

    with col2:
        st.markdown("### ℹ️ Requirements")
        st.info(
            """
            - **Format:** CSV (comma-separated)
            - **Min rows:** 10
            - **Min cols:** 2
            - **Max rows:** 1M
            - **Max cols:** 1000
            """
        )

    st.divider()

    # Process button
    if uploaded_file is not None:
        if st.button("🚀 Process & Detect Problem Type", key="process_btn", use_container_width=True):
            with st.spinner("Uploading and analyzing..."):
                try:
                    # Read file
                    file_content = uploaded_file.read().decode("utf-8")

                    # Upload to API
                    files = {"file": (uploaded_file.name, file_content)}
                    response = requests.post(f"{API_URL}/api/v1/upload", files=files)

                    if response.status_code == 200:
                        result = response.json()

                        # Store in session
                        st.session_state.job_id = result["job_id"]
                        st.session_state.upload_result = result

                        st.markdown(
                            '<div class="success-box">✅ <b>Upload Successful!</b></div>',
                            unsafe_allow_html=True,
                        )

                        # Display results
                        st.markdown("### 📊 Dataset Overview")

                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Rows", result["rows"])
                        with col2:
                            st.metric("Columns", result["cols"])
                        with col3:
                            st.metric("Job ID", result["job_id"])

                        # Schema table
                        st.markdown("### 📋 Column Schema")

                        schema_data = []
                        for col, info in result["schema"].items():
                            schema_data.append(
                                {
                                    "Column": col,
                                    "Type": info["detected_type"].upper(),
                                    "Unique": info["unique_values"],
                                    "Nulls %": f"{info['null_percentage']:.1f}%",
                                }
                            )

                        st.dataframe(schema_data, use_container_width=True)

                        # Metadata
                        st.markdown("### 📈 Summary Statistics")
                        metadata = result["metadata"]

                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.markdown(
                                f"**Memory:** {metadata['memory_usage_mb']:.1f} MB"
                            )
                        with col2:
                            st.markdown(
                                f"**Duplicates:** {metadata['duplicate_rows']}"
                            )
                        with col3:
                            st.markdown(
                                f"**Numeric Cols:** {len(metadata['numeric_columns'])}"
                            )

                        # Validation results
                        st.markdown("### ✅ Data Quality Checks")

                        for check in result["validation_results"]:
                            status = "✅" if check["passed"] else "⚠️"
                            st.write(
                                f"{status} **{check['name']}**  \n"
                                f"```{check['message']}```"
                            )

                        # Next step button
                        st.divider()
                        st.markdown("### Next: Problem Detection")

                        if st.button(
                            "🤖 Auto-Detect Problem Type →",
                            key="detect_problem",
                            use_container_width=True,
                        ):
                            st.switch_page("pages/2_problem_detection.py")

                    else:
                        st.error(f"❌ Upload failed: {response.json()}")

                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")


# ============================================================================
# PAGE: PROBLEM DETECTION
# ============================================================================

elif page == "🔍 Problem Detection":
    st.markdown(
        '<p class="main-header">🤖 Auto Problem Detection</p>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="subtitle">System automatically detects target column and problem type (classification/regression)</p>',
        unsafe_allow_html=True,
    )

    st.divider()

    # Check if we have a job
    if "job_id" not in st.session_state:
        st.warning("⚠️ Please upload a dataset first (← Use Upload Data tab)")
        st.stop()

    job_id = st.session_state.job_id

    st.markdown(f"**Current Job:** `{job_id}`")

    # Get job status
    try:
        response = requests.get(f"{API_URL}/api/v1/jobs/{job_id}")
        if response.status_code == 200:
            job_data = response.json()

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("### 🎯 Detection Results")
                st.markdown(
                    f"**Status:** Coming soon  \n"
                    f"**Rows:** {job_data['rows']}  \n"
                    f"**Columns:** {job_data['cols']}"
                )

            with col2:
                st.markdown("### 📊 Available Data")
                st.markdown(
                    f"**Shape:** {job_data['shape']}  \n"
                    f"**Memory:** {job_data['metadata']['memory_usage_mb']:.1f} MB  \n"
                    f"**Duplicates:** {job_data['metadata']['duplicate_rows']}"
                )

            st.divider()

            # Feature breakdown
            st.markdown("### 📝 Column Categories")

            col1, col2, col3 = st.columns(3)
            with col1:
                st.write(f"**Numeric:** {len(job_data['metadata']['numeric_columns'])}")
                for col in job_data['metadata']['numeric_columns'][:3]:
                    st.code(col)
            with col2:
                st.write(f"**Categorical:** {len(job_data['metadata']['categorical_columns'])}")
                for col in job_data['metadata']['categorical_columns'][:3]:
                    st.code(col)
            with col3:
                st.write(f"**Datetime:** {len(job_data['metadata']['datetime_columns'])}")
                for col in job_data['metadata']['datetime_columns'][:3]:
                    st.code(col)

            st.divider()

            st.info(
                "🔄 Problem detection will be implemented in Week 1 using LangGraph + LLM"
            )

        else:
            st.error("Failed to fetch job data")

    except Exception as e:
        st.error(f"Error: {str(e)}")


# ============================================================================
# PAGE: COMING SOON PAGES
# ============================================================================

else:
    st.markdown('<p class="main-header">⏳ Coming Soon</p>', unsafe_allow_html=True)
    st.markdown(
        """
    This page is under development.
    
    **Development Timeline:**
    - Week 1: Upload + Problem Detection ✅
    - Week 2: EDA + Model Training
    - Week 3: Results + Chat
    - Week 4: Report + Full Dashboard
    
    Check back soon!
    """
    )

    st.divider()

    st.markdown("### 📊 Module Status")

    modules = {
        "1": ("Data Ingestion", "✅ Week 1"),
        "2": ("Business Context", "⏳ Week 1"),
        "3": ("Problem Detection", "✅ Week 1"),
        "4": ("Airflow DAG", "⏳ Week 1"),
        "5": ("Data Cleaning", "⏳ Week 2"),
        "6": ("EDA Engine", "⏳ Week 2"),
        "7": ("Features", "⏳ Week 2"),
        "8": ("AutoML Training", "⏳ Week 2"),
        "9": ("Evaluation", "⏳ Week 3"),
        "10": ("SHAP", "⏳ Week 3"),
        "11": ("Insights", "⏳ Week 3"),
        "12": ("Critique", "⏳ Week 3"),
        "13": ("Drift", "⏳ Week 3"),
        "14": ("Chat/RAG", "⏳ Week 3"),
        "15": ("MLflow", "⏳ Week 4"),
        "16": ("DVC", "⏳ Week 4"),
        "17": ("Job Queue", "⏳ Week 4"),
        "18": ("PDF Report", "⏳ Week 4"),
        "19": ("API Endpoints", "⏳ Week 4"),
        "20": ("LLM Provider", "✅ Week 1"),
        "21": ("Dashboard", "⏳ Week 4"),
        "22": ("K8s + Tests", "⏳ Week 4"),
    }

    cols = st.columns(3)
    for i, (num, (name, status)) in enumerate(modules.items()):
        with cols[i % 3]:
            if "✅" in status:
                st.success(f"**M{num}:** {name}")
            else:
                st.info(f"**M{num}:** {name}")
