import streamlit as st
import requests

st.set_page_config(page_title="Dosage Checker", page_icon="💊", layout="wide")

# Custom CSS with dark blue theme
st.markdown("""
<style>
    .main { background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%); }
    .page-header {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 2.5rem;
        border-radius: 15px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 8px 16px rgba(0,0,0,0.3);
        text-align: center;
    }
    .page-header h1 { font-size: 2.5rem; margin: 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }
    .metric-card { 
        background: linear-gradient(135deg, #1a2980 0%, #26d0ce 100%); 
        padding: 2rem; 
        border-radius: 15px; 
        border: 2px solid rgba(255,255,255,0.1); 
        text-align: center;
        color: white;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    hr { border: none; height: 2px; background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent); margin: 2rem 0; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="page-header"><h1>💊 Dosage Verification Engine</h1><p style="margin:0.5rem 0 0 0; font-size:1.1rem;">Verify medication dosages against WHO DDD (Defined Daily Dose) standards</p></div>', unsafe_allow_html=True)

BACKEND_URL = "http://localhost:8000"

# Input form
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 👤 Patient Information")
    patient_age = st.number_input("Patient Age", min_value=0, max_value=120, value=45)
    patient_weight = st.number_input("Patient Weight (kg)", min_value=0.0, max_value=300.0, value=70.0, step=0.1)

with col2:
    st.markdown("### 💊 Medication & Dosage")
    medication = st.text_input("Medication Name", placeholder="e.g., Aspirin")
    
    dose_col1, dose_col2 = st.columns([2, 1])
    with dose_col1:
        prescribed_dose = st.number_input("Prescribed Dose", min_value=0.0, value=100.0, step=0.1)
    with dose_col2:
        dose_unit = st.selectbox("Unit", ["mg", "g", "ml", "mcg", "iu"])

# Check button
if st.button("✅ Verify Dosage", type="primary"):
    if not medication:
        st.error("Please enter a medication name")
    else:
        with st.spinner("Verifying dosage..."):
            try:
                response = requests.post(
                    f"{BACKEND_URL}/dosage/check",
                    json={
                        "patient_age": patient_age,
                        "patient_weight_kg": patient_weight,
                        "medication": medication,
                        "prescribed_dose": prescribed_dose,
                        "dose_unit": dose_unit
                    },
                    timeout=10
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    st.markdown("---")
                    st.markdown("### 📊 Dosage Verification Results")
                    
                    # Status indicator
                    status = result['status']
                    if status == 'safe':
                        st.success(f"✅ {result['message']}")
                    elif status in ['high', 'very_high']:
                        st.error(f"⚠️ {result['message']}")
                    elif status == 'low':
                        st.warning(f"⚠️ {result['message']}")
                    else:
                        st.info(result['message'])
                    
                    # Details
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Prescribed Dose", result['prescribed_dose'])
                    with col2:
                        st.metric("WHO DDD", result.get('ddd', 'N/A'))
                    with col3:
                        ratio = result.get('dose_ratio', 0)
                        st.metric("Dose Ratio", f"{ratio:.2f}x", delta=f"{(ratio-1)*100:.0f}%" if ratio else None)
                    
                    # Age group info
                    st.info(f"**Age Group:** {result.get('age_group', 'Unknown')}")
                    st.write(f"**Age Adjustment:** {result.get('age_adjustment', 'N/A')}")
                    
                    # Recommendation
                    st.markdown("### 💡 Recommendation")
                    st.write(result['recommendation'])
                
                else:
                    st.error(f"Error: {response.status_code}")
            
            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot connect to backend")
            except Exception as e:
                st.error(f"Error: {str(e)}")

with st.expander("ℹ️ About Dosage Verification"):
    st.write("""
    **WHO Defined Daily Dose (DDD):**
    - Standard measurement unit for drug utilization
    - Assumed average maintenance dose per day for adults
    - Used for age-specific dose validation
    
    **Dose Ratio Interpretation:**
    - < 0.5: Possibly subtherapeutic
    - 0.5-1.5: Within acceptable range
    - 1.5-2.0: Above standard, monitor
    - > 2.0: Significantly high, verify prescription
    """)
