import streamlit as st
import requests

st.set_page_config(page_title="Alternative Medicines", page_icon="🔄", layout="wide")

st.title("🔄 Alternative Medicine Recommender")
st.write("Find safer or more cost-effective alternatives based on ATC classification & WHO Essential Medicines List")

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
