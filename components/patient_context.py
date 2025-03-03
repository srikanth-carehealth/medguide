# =====================================
# components/patient_context.py
# =====================================
import streamlit as st

def render_patient_context(patient):
    st.markdown(f"""
    <div class="patient-banner">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h3 style="font-size: 0.875rem; font-weight: 500; margin: 0; color: #1e40af;">{patient['name']}, {patient['age']}</h3>
                <p style="font-size: 0.75rem; margin: 0; color: #3b82f6;">{patient['diagnosis']}</p>
            </div>
            <div style="font-size: 0.75rem; color: #3b82f6;">
                <span style="font-weight: 500;">Recent:</span> {get_patient_labs_string(patient)}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def get_patient_labs_string(patient):
    labs = patient.get('recentLabs', {})
    labs_strings = []
    for key, value in labs.items():
        labs_strings.append(f"{key}: {value}")
    return ", ".join(labs_strings)