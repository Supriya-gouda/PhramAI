import streamlit as st
import requests

st.set_page_config(page_title="Alternative Medicines", page_icon="🔄", layout="wide")

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
    .alt-card { 
        background: linear-gradient(135deg, #1a2980 0%, #26d0ce 100%); 
        padding: 1.5rem; 
        border-radius: 15px; 
        border: 2px solid rgba(255,255,255,0.1); 
        margin: 1rem 0; 
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        color: white;
    }
    hr { border: none; height: 2px; background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent); margin: 2rem 0; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="page-header"><h1>🔄 Alternative Medicine Recommender</h1><p style="margin:0.5rem 0 0 0; font-size:1.1rem;">Find safer or more cost-effective alternatives based on ATC classification & WHO Essential Medicines List</p></div>', unsafe_allow_html=True)

BACKEND_URL = "http://localhost:8000"

# Input
col1, col2 = st.columns([2, 1])

with col1:
    medication = st.text_input("Enter Medication Name", placeholder="e.g., Aspirin")

with col2:
    reason = st.selectbox(
        "Reason for Alternative",
        ["general", "interaction", "allergy", "cost"]
    )

if st.button("🔍 Find Alternatives", type="primary"):
    if not medication:
        st.error("Please enter a medication name")
    else:
        with st.spinner("Searching for alternatives..."):
            try:
                response = requests.post(
                    f"{BACKEND_URL}/alternatives/suggest",
                    json={"medication": medication, "reason": reason},
                    timeout=10
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    st.markdown("---")
                    st.markdown(f"### 💊 Alternatives for **{result['medication']}**")
                    
                    if result['total_found'] == 0:
                        st.warning("No alternatives found in database")
                    else:
                        st.success(f"Found {result['total_found']} alternative(s)")
                        
                        # Display alternatives
                        for i, alt in enumerate(result['alternatives'], 1):
                            with st.container():
                                col1, col2, col3 = st.columns([3, 1, 1])
                                
                                with col1:
                                    st.markdown(f"**{i}. {alt['name']}**")
                                    st.caption(f"ATC Code: {alt.get('atc_code', 'N/A')}")
                                
                                with col2:
                                    if alt['is_eml']:
                                        st.success("✅ WHO EML")
                                    else:
                                        st.info("Standard")
                                
                                with col3:
                                    priority = alt['priority']
                                    color = "🟢" if priority == "high" else "🟡" if priority == "medium" else "🔴"
                                    st.write(f"{color} {priority.title()}")
                                
                                st.write(f"**Reason:** {alt['reason']}")
                                if alt.get('notes'):
                                    st.write(f"*{alt['notes']}*")
                                st.markdown("---")
                
                else:
                    st.error(f"Error: {response.status_code}")
            
            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot connect to backend")
            except Exception as e:
                st.error(f"Error: {str(e)}")

with st.expander("ℹ️ About Alternative Recommendations"):
    st.write("""
    **How Alternatives are Selected:**
    - **Same Therapeutic Class**: Medications with same ATC code prefix
    - **WHO EML Priority**: Essential Medicines List drugs prioritized
    - **Reason-Based**: Adjusted for interactions, allergies, or cost
    
    **WHO Essential Medicines List (EML):**
    - Core list of most effective and safe medicines
    - Cost-effective options
    - Meets priority health needs
    """)
