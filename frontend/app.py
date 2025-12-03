import streamlit as st
import requests

st.set_page_config(
    page_title="PharmAI",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS with consistent dark blue theme
st.markdown("""
<style>
    /* Main background */
    .main {
        background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 2.5rem;
        border-radius: 15px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 8px 16px rgba(0,0,0,0.3);
        text-align: center;
    }
    
    .main-header h1 {
        font-size: 3rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    /* Feature cards */
    .feature-card {
        background: linear-gradient(135deg, #1a2980 0%, #26d0ce 100%);
        padding: 2rem;
        border-radius: 15px;
        border: 2px solid rgba(255,255,255,0.1);
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        margin-bottom: 1.5rem;
        transition: all 0.3s ease;
        color: white;
    }
    
    .feature-card:hover {
        transform: translateY(-5px) scale(1.02);
        box-shadow: 0 8px 25px rgba(26,41,128,0.4);
        border-color: rgba(255,255,255,0.3);
    }
    
    .feature-card h3 {
        color: #ffffff;
        margin-top: 0;
        font-size: 1.5rem;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
    }
    
    .feature-card p {
        color: rgba(255,255,255,0.9);
        margin: 1rem 0;
    }
    
    /* Status badges */
    .status-badge {
        display: inline-block;
        padding: 0.8rem 2rem;
        border-radius: 25px;
        font-weight: 700;
        font-size: 1.1rem;
        margin: 0.5rem 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.4);
    }
    
    .status-online {
        background: #11998e;
        color: white;
    }
    
    .status-offline {
        background: #eb3349;
        color: white;
    }
    
    /* Stat box - smaller and compact */
    .stat-box {
        background: rgba(44, 83, 100, 0.9);
        padding: 1rem;
        border-radius: 12px;
        text-align: center;
        border: 2px solid rgba(255,255,255,0.2);
        box-shadow: 0 3px 10px rgba(0,0,0,0.3);
    }
    
    .stat-box h3 {
        font-size: 2rem;
        margin: 0;
    }
    
    .stat-box p {
        color: #ffffff;
        margin: 0.3rem 0 0 0;
        font-size: 0.95rem;
    }
    
    /* Section headers */
    .section-header {
        color: #ffffff;
        font-size: 2rem;
        font-weight: 600;
        margin: 2rem 0 1rem 0;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
    }
    
    /* Feature badge */
    .feature-badge {
        background: rgba(255,255,255,0.2);
        color: white;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        border: 1px solid rgba(255,255,255,0.3);
        display: inline-block;
        margin-top: 0.5rem;
    }
    
    /* CTA Box */
    .cta-box {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        color: white;
        box-shadow: 0 8px 20px rgba(0,0,0,0.3);
        border: 2px solid rgba(255,255,255,0.1);
    }
    
    .cta-box h3 {
        margin: 0;
        font-size: 2rem;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
    }
    
    .cta-box p {
        margin: 0.5rem 0 0 0;
        font-size: 1.2rem;
    }
    
    /* Divider */
    hr {
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
        margin: 2rem 0;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('''
<div class="main-header">
    <h1>💊 PharmAI</h1>
    <p style="margin:0; font-size:1.3rem; font-weight:300;">AI-Powered Medical Prescription Safety System</p>
    <p style="margin:0.5rem 0 0 0; font-size:1rem; opacity:0.9;">Powered by IBM Granite AI • 53,755+ Drug Interactions • WHO Standards</p>
</div>
''', unsafe_allow_html=True)

st.sidebar.markdown('<h2 style="color: #26d0ce; font-size: 2.2rem; margin-bottom: 1rem; font-weight: 700;">🧭 Navigation</h2>', unsafe_allow_html=True)
st.sidebar.markdown("---")
st.sidebar.markdown('<p style="font-size: 1.3rem; color: #2c2c2c; font-weight: 500;">👈 Select a page above to access different features</p>', unsafe_allow_html=True)

st.markdown('<p style="color: #1a1a1a; font-size: 2.5rem; font-weight: 600; margin: 2rem 0 1rem 0; text-shadow: 1px 1px 2px rgba(0,0,0,0.3);">🔌 System Status</p>', unsafe_allow_html=True)

try:
    response = requests.get("http://localhost:8000/health", timeout=2)
    if response.status_code == 200:
        st.markdown('<div class="status-badge status-online">✅ Backend Server Online</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-badge status-offline">❌ Backend Error</div>', unsafe_allow_html=True)
except:
    st.markdown('<div class="status-badge status-offline">⚠️ Backend Offline</div>', unsafe_allow_html=True)
    st.markdown('<p style="color: rgba(255,255,255,0.95); margin-top: 0.8rem; font-size: 1.05rem;">Start with: start_backend.bat</p>', unsafe_allow_html=True)

st.markdown("---")
st.markdown('<p style="color: #1a1a1a; font-size: 2.5rem; font-weight: 600; margin: 2rem 0 1rem 0; text-shadow: 1px 1px 2px rgba(0,0,0,0.3);">✨ Core Features</p>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown('''
    <div style="background: linear-gradient(135deg, #1a2980 0%, #26d0ce 100%); padding: 1.5rem; border-radius: 12px; margin-bottom: 1.2rem; box-shadow: 0 4px 12px rgba(0,0,0,0.3);">
        <h3 style="color: #ffffff; font-size: 1.6rem; margin: 0 0 0.5rem 0; font-weight: 600;">🔍 Drug Extraction</h3>
        <p style="color: #ffffff; font-size: 1.15rem; margin: 0; font-weight: 400;">Extract medications from prescription text using IBM Granite AI</p>
    </div>
    ''', unsafe_allow_html=True)
    
    st.markdown('''
    <div style="background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%); padding: 1.5rem; border-radius: 12px; margin-bottom: 1.2rem; box-shadow: 0 4px 12px rgba(0,0,0,0.3);">
        <h3 style="color: #ffffff; font-size: 1.6rem; margin: 0 0 0.5rem 0; font-weight: 600;">💊 Dosage Verification</h3>
        <p style="color: #ffffff; font-size: 1.15rem; margin: 0; font-weight: 400;">Age-specific dosage validation using WHO DDD standards</p>
    </div>
    ''', unsafe_allow_html=True)
    
    st.markdown('''
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1.5rem; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.3);">
        <h3 style="color: #ffffff; font-size: 1.6rem; margin: 0 0 0.5rem 0; font-weight: 600;">📊 Risk Prediction</h3>
        <p style="color: #ffffff; font-size: 1.15rem; margin: 0; font-weight: 400;">Multi-factor safety risk scoring system</p>
    </div>
    ''', unsafe_allow_html=True)

with col2:
    st.markdown('''
    <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 1.5rem; border-radius: 12px; margin-bottom: 1.2rem; box-shadow: 0 4px 12px rgba(0,0,0,0.3);">
        <h3 style="color: #ffffff; font-size: 1.6rem; margin: 0 0 0.5rem 0; font-weight: 600;">⚠️ Interaction Checker</h3>
        <p style="color: #ffffff; font-size: 1.15rem; margin: 0; font-weight: 400;">53,755+ drug-drug interactions from DrugBank</p>
    </div>
    ''', unsafe_allow_html=True)
    
    st.markdown('''
    <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); padding: 1.5rem; border-radius: 12px; margin-bottom: 1.2rem; box-shadow: 0 4px 12px rgba(0,0,0,0.3);">
        <h3 style="color: #ffffff; font-size: 1.6rem; margin: 0 0 0.5rem 0; font-weight: 600;">🔄 Alternative Finder</h3>
        <p style="color: #ffffff; font-size: 1.15rem; margin: 0; font-weight: 400;">WHO Essential Medicines List recommendations</p>
    </div>
    ''', unsafe_allow_html=True)
    
    st.markdown('''
    <div style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); padding: 1.5rem; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.3);">
        <h3 style="color: #ffffff; font-size: 1.6rem; margin: 0 0 0.5rem 0; font-weight: 600;">📚 Database</h3>
        <p style="color: #ffffff; font-size: 1.15rem; margin: 0; font-weight: 400;">400+ medicines with validated information</p>
    </div>
    ''', unsafe_allow_html=True)
st.markdown("---")
st.markdown("""
<div class="cta-box">
    <h3>🚀 Get Started</h3>
    <p>Navigate to the pages in the sidebar to use each feature →</p>
</div>
""", unsafe_allow_html=True)
