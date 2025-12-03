import streamlit as st
import requests

st.set_page_config(page_title="Prescription Extraction & Risk Analysis", page_icon="🔍", layout="wide")

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
    .med-card { 
        background: linear-gradient(135deg, #1a2980 0%, #26d0ce 100%); 
        padding: 1.5rem; 
        border-radius: 12px; 
        border-left: 5px solid #26d0ce; 
        margin: 0.8rem 0;
        color: white;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }
    .risk-card { 
        padding: 2.5rem; 
        border-radius: 15px; 
        text-align: center; 
        margin: 2rem 0;
        box-shadow: 0 8px 20px rgba(0,0,0,0.3);
        border: 2px solid rgba(255,255,255,0.1);
    }
    hr { border: none; height: 2px; background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent); margin: 2rem 0; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="page-header"><h1>🔍 AI Prescription Extraction & Risk Analysis</h1><p style="margin:0.5rem 0 0 0; font-size:1.1rem;">Extract medications from prescription text using IBM Granite AI and get comprehensive safety analysis</p></div>', unsafe_allow_html=True)

BACKEND_URL = "http://localhost:8000"

# Tabs for different input methods
tab1, tab2 = st.tabs(["📝 Text Input", "🎤 Voice Input (Coming Soon)"])

with tab1:
    st.markdown("### Enter Prescription Text")
    
    prescription_text = st.text_area(
        "Paste prescription text or clinical notes",
        placeholder="""Example:
1. Aspirin 100mg once daily
2. Metformin 500mg twice daily
3. Lisinopril 10mg once daily""",
        height=200
    )
    
    # Patient info for risk analysis
    with st.expander("➕ Add Patient Information (for risk analysis)"):
        col1, col2 = st.columns(2)
        with col1:
            patient_age = st.number_input("Patient Age", 0, 120, 45)
        with col2:
            patient_weight = st.number_input("Weight (kg)", 0.0, 300.0, 70.0)
    
    if st.button("🚀 Extract & Analyze", type="primary"):
        if not prescription_text:
            st.error("Please enter prescription text")
        else:
            with st.spinner("Analyzing prescription with IBM Granite AI..."):
                try:
                    # Step 1: Extract medications
                    extract_response = requests.post(
                        f"{BACKEND_URL}/extraction/extract",
                        json={"text": prescription_text},
                        timeout=30
                    )
                    
                    if extract_response.status_code == 200:
                        extraction_result = extract_response.json()
                        
                        st.markdown("---")
                        st.markdown("### ✅ Extracted Medications")
                        st.success(f"Found {extraction_result['total_extracted']} medication(s)")
                        
                        # Display extracted medications
                        medications = extraction_result['medications']
                        
                        for i, med in enumerate(medications, 1):
                            with st.expander(f"💊 {i}. {med['drug_name']}", expanded=True):
                                col1, col2, col3, col4 = st.columns(4)
                                with col1:
                                    st.write(f"**Dosage:** {med.get('dosage', 'N/A')}")
                                with col2:
                                    st.write(f"**Frequency:** {med.get('frequency', 'N/A')}")
                                with col3:
                                    st.write(f"**Route:** {med.get('route', 'oral')}")
                                with col4:
                                    st.write(f"**Duration:** {med.get('duration', 'N/A')}")
                        
                        # Step 2: Run risk prediction
                        if len(medications) > 0:
                            st.markdown("---")
                            st.markdown("### 📊 Comprehensive Risk Analysis")
                            
                            with st.spinner("Calculating risk score..."):
                                # Prepare medications for risk API
                                risk_meds = []
                                for med in medications:
                                    # Extract numeric dose
                                    import re
                                    dosage_str = med.get('dosage', '0mg')
                                    match = re.search(r'(\d+(?:\.\d+)?)', dosage_str)
                                    dose_value = float(match.group(1)) if match else 0
                                    
                                    unit_match = re.search(r'(mg|g|ml|mcg)', dosage_str.lower())
                                    dose_unit = unit_match.group(1) if unit_match else 'mg'
                                    
                                    risk_meds.append({
                                        "name": med['drug_name'],
                                        "dose": dose_value,
                                        "unit": dose_unit
                                    })
                                
                                risk_response = requests.post(
                                    f"{BACKEND_URL}/risk/predict",
                                    json={
                                        "medications": risk_meds,
                                        "patient_info": {
                                            "patient_age": patient_age,
                                            "patient_weight_kg": patient_weight
                                        }
                                    },
                                    timeout=15
                                )
                                
                                if risk_response.status_code == 200:
                                    risk_result = risk_response.json()
                                    
                                    # Risk Score Display
                                    col1, col2, col3 = st.columns([1, 2, 1])
                                    
                                    with col2:
                                        risk_score = risk_result['risk_score']
                                        risk_level = risk_result['risk_level']
                                        
                                        # Color based on safety score (10=safe, 0=critical)
                                        if risk_score >= 8:
                                            color = "#28a745"  # Green - SAFE
                                        elif risk_score >= 6:
                                            color = "#17a2b8"  # Blue - LOW RISK
                                        elif risk_score >= 4:
                                            color = "#ffc107"  # Yellow - MODERATE RISK
                                        elif risk_score >= 2:
                                            color = "#fd7e14"  # Orange - HIGH RISK
                                        else:
                                            color = "#dc3545"  # Red - CRITICAL
                                        
                                        st.markdown(f"""
                                        <div style='text-align: center; padding: 2rem; background-color: {color}20; border-radius: 10px; border: 3px solid {color};'>
                                            <h1 style='color: {color}; margin: 0;'>{risk_score}/10</h1>
                                            <h3 style='color: {color}; margin: 0;'>{risk_level}</h3>
                                            <p style='color: #666; margin-top: 0.5rem;'>Safety Score (10 = Fully Safe, 0 = Critical)</p>
                                        </div>
                                        """, unsafe_allow_html=True)
                                    
                                    # Safety interpretation
                                    if risk_score >= 8:
                                        st.success("✅ **SAFE** - Prescription appears safe with current information")
                                    elif risk_score >= 6:
                                        st.info("ℹ️ **LOW RISK** - Minor concerns, generally safe")
                                    elif risk_score >= 4:
                                        st.warning("⚠️ **MODERATE RISK** - Review recommendations carefully")
                                    elif risk_score >= 2:
                                        st.error("🚨 **HIGH RISK** - Significant concerns, careful monitoring required")
                                    else:
                                        st.error("🚨 **CRITICAL RISK** - Urgent review required before dispensing")
                                    
                                    st.markdown("---")
                                    
                                    # Risk Factors Breakdown
                                    st.markdown("### 📈 Risk Factors Breakdown")
                                    
                                    factors = risk_result['factors']
                                    
                                    col1, col2, col3 = st.columns(3)
                                    
                                    with col1:
                                        inter_risk = factors['interaction_risk']
                                        st.metric("Interaction Risk", f"{inter_risk['score']:.1f}", delta=f"Weight: {inter_risk['weight']}")
                                        st.caption(inter_risk['details'].get('message', ''))
                                    
                                    with col2:
                                        dose_risk = factors['dosage_risk']
                                        st.metric("Dosage Risk", f"{dose_risk['score']:.1f}", delta=f"Weight: {dose_risk['weight']}")
                                        st.caption(dose_risk['details'].get('message', ''))
                                    
                                    with col3:
                                        poly_risk = factors['polypharmacy_risk']
                                        st.metric("Polypharmacy Risk", f"{poly_risk['score']:.1f}", delta=f"Weight: {poly_risk['weight']}")
                                        st.caption(poly_risk['details'].get('message', ''))
                                    
                                    # Recommendations
                                    st.markdown("---")
                                    st.markdown("### 💡 Clinical Recommendations")
                                    
                                    for rec in risk_result['recommendations']:
                                        if '⚠️' in rec or 'URGENT' in rec:
                                            st.error(rec)
                                        elif '✓' in rec:
                                            st.success(rec)
                                        else:
                                            st.warning(rec)
                    
                    else:
                        st.error(f"Extraction failed: {extract_response.status_code}")
                
                except requests.exceptions.ConnectionError:
                    st.error("❌ Cannot connect to backend. Please start backend: `python backend/main.py`")
                except Exception as e:
                    st.error(f"Error: {str(e)}")

with tab2:
    st.info("🎤 Voice input feature coming soon! Will use OpenAI Whisper for speech-to-text.")

# Info section
with st.expander("ℹ️ About This System"):
    st.write("""
    **PharmAI** uses multiple AI models and medical databases:
    
    - **IBM Granite 3.2-2B**: Drug extraction from text
    - **DrugBank**: Interaction database
    - **WHO ATC/DDD**: Dosage standards
    - **WHO EML**: Essential medicines list
    - **Risk Prediction**: Multi-factor analysis (interactions + dosage + polypharmacy)
    
    **Risk Score Components:**
    - Interaction Risk (60% weight)
    - Dosage Deviation (30% weight)
    - Polypharmacy Risk (10% weight)
    """)
