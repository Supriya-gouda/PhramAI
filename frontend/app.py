import streamlit as st
import requests

st.set_page_config(
    page_title="PharmAI",
    page_icon="💊",
    layout="wide"
)

st.title("💊 PharmAI - Medical Prescription Safety")
st.write("AI-powered prescription validation with 53,755+ drug interactions")

st.sidebar.title("📋 Navigation")
st.sidebar.info("Use the pages above to access different features")

st.markdown("## System Status")

try:
    response = requests.get("http://localhost:8000/health", timeout=2)
    if response.status_code == 200:
        st.success("✅ Backend Server Online")
        st.info("API Docs: http://localhost:8000/docs")
    else:
        st.error("❌ Backend Error")
except:
    st.warning("⚠️ Backend Offline - Start with: python start_backend.py")

st.markdown("---")
st.markdown("## Features")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 🔍 Drug Extraction")
    st.write("Extract medications from prescription text using IBM Granite AI")

with col2:
    st.markdown("### ⚠️ Interaction Checker")
    st.write("53,755+ drug-drug interactions from DrugBank")

with col3:
    st.markdown("### 💊 Dosage Verification")
    st.write("Age-specific dosage validation using WHO DDD standards")

st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 🔄 Alternative Finder")
    st.write("WHO EML-based alternative recommendations")

with col2:
    st.markdown("### 📊 Risk Prediction")
    st.write("Multi-factor safety risk scoring")

with col3:
    st.markdown("### 📚 Database")
    st.write("108 drugs, 194 Indian medicines, 82 age rules")

st.markdown("---")
st.info("👈 **Navigate to the pages in the sidebar to use each feature**")
