import streamlit as st
import requests
import json

st.set_page_config(page_title="Drug Interactions", page_icon="⚠️", layout="wide")

st.title("⚠️ Drug-Drug Interaction Checker")
st.write("Check for potentially harmful interactions between medications")

# Backend URL
BACKEND_URL = "http://localhost:8000"

# Input section
st.markdown("### 📝 Enter Medications")
col1, col2 = st.columns([3, 1])

with col1:
    medications_input = st.text_area(
        "Enter medications (one per line or comma-separated)",
        placeholder="Example:\nAspirin\nWarfarin\nMetformin",
        height=150
    )

with col2:
    st.info("""
    **Tips:**
    - Enter at least 2 medications
    - One medication per line
    - Or use commas to separate
    """)

# Process button
if st.button("🔍 Check Interactions", type="primary"):
    if not medications_input:
        st.error("Please enter at least one medication")
    else:
        # Parse medications
        medications = [med.strip() for med in medications_input.replace(',', '\n').split('\n') if med.strip()]
        
        if len(medications) < 2:
            st.warning("Please enter at least 2 medications to check for interactions")
        else:
            with st.spinner("Analyzing drug interactions..."):
                try:
                    # Call backend API
                    response = requests.post(
                        f"{BACKEND_URL}/interactions/check",
                        json={"medications": medications},
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        
                        # Display results
                        st.markdown("---")
                        st.markdown("### 📊 Interaction Analysis Results")
                        
                        if result['ok']:
                            st.success("✅ No known drug interactions detected!")
                        else:
                            st.error(f"⚠️ {result['total_interactions']} interaction(s) detected")
                            
                            # Severity summary
                            col1, col2, col3 = st.columns(3)
                            severity_summary = result['severity_summary']
                            
                            with col1:
                                st.metric("Major", severity_summary.get('Major', 0), delta=None, delta_color="inverse")
                            with col2:
                                st.metric("Moderate", severity_summary.get('Moderate', 0))
                            with col3:
                                st.metric("Minor", severity_summary.get('Minor', 0))
                            
                            # Display each interaction
                            st.markdown("### ⚠️ Detected Interactions")
                            for i, issue in enumerate(result['issues'], 1):
                                severity = issue['severity']
                                
                                # Color code by severity
                                if severity == 'Major':
                                    st.error(f"**{i}. {issue['drug_1']} + {issue['drug_2']}** (MAJOR)")
                                elif severity == 'Moderate':
                                    st.warning(f"**{i}. {issue['drug_1']} + {issue['drug_2']}** (Moderate)")
                                else:
                                    st.info(f"**{i}. {issue['drug_1']} + {issue['drug_2']}** (Minor)")
                                
                                st.write(f"**Description:** {issue['description']}")
                                st.write(f"**Recommendation:** {issue['recommendation']}")
                                st.markdown("---")
                    
                    else:
                        st.error(f"Error: {response.status_code} - {response.text}")
                
                except requests.exceptions.ConnectionError:
                    st.error("❌ Cannot connect to backend. Please ensure the backend is running on http://localhost:8000")
                except Exception as e:
                    st.error(f"Error: {str(e)}")

# Information section
with st.expander("ℹ️ About Drug Interactions"):
    st.write("""
    **Drug Interaction Severity Levels:**
    
    - **Major**: Avoid combination. May cause serious harm. Alternative therapy recommended.
    - **Moderate**: Use with caution. Monitor patient closely. Dosage adjustment may be needed.
    - **Minor**: Generally safe but monitor for potential effects.
    
    **Data Source:** DrugBank interaction database
    """)
