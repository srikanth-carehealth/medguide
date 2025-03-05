import streamlit as st
import requests
import re
import html
import json
from datetime import datetime

from components.sidebar import render_sidebar
from components.document_viewer import render_document_viewer
from components.clinician_prompts import render_clinician_prompts
from components.note_generator import render_note_generator
from components.patient_context import render_patient_context
from data.sample_data import get_sample_patient

# Helper function to sanitize text values
def sanitize_text(text):
    """Thoroughly sanitize any text by removing HTML tags and escaping content"""
    if text is None:
        return ""
    # Convert to string if not already
    text_str = str(text)
    # Remove all HTML tags aggressively
    stripped = re.sub(r'</?[^>]+/?>', '', text_str, flags=re.IGNORECASE)
    # Remove any remaining HTML entities
    stripped = re.sub(r'&[a-zA-Z0-9#]+;', '', stripped)
    # Trim whitespace
    stripped = stripped.strip()
    # Escape any remaining special characters
    return html.escape(stripped)

# Function to extract patient name
def get_patient_name(patient_data):
    if not patient_data or 'name' not in patient_data:
        return "Unknown Patient"
    
    # Start with a default value
    result = "Unknown Patient"
    
    try:
        # Safely extract the name
        names = patient_data.get('name', [])
        
        # Check if it's a list with elements
        if isinstance(names, list) and names:
            name = names[0]
        else:
            name = names  # If it's not a list, use it directly
            
        # Try different ways to get the name, but sanitize at each step
        if isinstance(name, dict):
            if 'text' in name and name['text']:
                result = sanitize_text(name['text'])
            else:
                given = []
                if 'given' in name and name['given']:
                    if isinstance(name['given'], list):
                        given = [sanitize_text(g) for g in name['given']]
                    else:
                        given = [sanitize_text(name['given'])]
                
                family = sanitize_text(name.get('family', ''))
                
                if given and family:
                    result = f"{' '.join(given)} {family}"
                elif family:
                    result = family
                elif given:
                    result = ' '.join(given)
        elif isinstance(name, str):
            # If the name is a string directly
            result = sanitize_text(name)
        
        # Final sanitization
        result = sanitize_text(result)
        print(f"Processed patient name: {result}")
    except Exception as e:
        print(f"Error processing patient name: {e}")
        result = "Unknown Patient"
    
    return result

# Function to create the patient object
def create_patient_object(fhir_patient):
    try:
        patient_obj = {
            'name': get_patient_name(fhir_patient),
            'age': sanitize_text(get_patient_age(fhir_patient)),
            'diagnosis': sanitize_text(get_patient_diagnosis(fhir_patient)),
            'recentLabs': get_patient_labs(fhir_patient)
        }
        
        # Log the patient object for debugging
        print(f"Created patient object: {patient_obj}")
        
        return patient_obj
    except Exception as e:
        print(f"Error creating patient object: {e}")
        return {
            'name': 'Error loading patient',
            'age': '',
            'diagnosis': '',
            'recentLabs': {}
        }

def get_patient_age(patient_data):
    if not patient_data or 'birthDate' not in patient_data:
        return "Unknown"
    
    try:
        birth_date = datetime.strptime(patient_data['birthDate'], '%Y-%m-%d')
        today = datetime.now()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        return f"{age}"
    except Exception as e:
        return "Unknown"

def get_patient_diagnosis(patient_data):
    if not patient_data:
        return ""
    
    diagnosis = ""
    if 'extension' in patient_data:
        for ext in patient_data.get('extension', []):
            if 'url' in ext and 'diagnosis' in ext['url']:
                diagnosis = ext.get('valueString', '')
                print(f"Extracted diagnosis from FHIR data: {diagnosis}")
                return sanitize_text(diagnosis)
    
    print(f"No diagnosis found in FHIR data. Defaulting to: {diagnosis}")
    return diagnosis

def get_patient_labs(patient_data):
    if not patient_data:
        return {}
    
    if 'extension' in patient_data:
        for ext in patient_data.get('extension', []):
            if 'url' in ext and 'recentLabs' in ext['url']:
                labs = {}
                for lab_ext in ext.get('extension', []):
                    if 'valueCoding' in lab_ext:
                        key = sanitize_text(lab_ext['valueCoding']['display'])
                        value = sanitize_text(lab_ext['valueCoding']['code'])
                        labs[key] = value
                if labs:
                    return labs
    
    return {}

# Function to fetch patient data from Express server
def fetch_patient_data():
    try:
        response = requests.get('http://localhost:8080/api/patient')
        if response.status_code == 200:
            raw_data = response.json()
            print(f"Raw FHIR patient data: {raw_data}")
            return raw_data
        else:
            st.warning(f"⚠️ Failed to retrieve patient data from server: {response.status_code}")
            return None
    except Exception as e:
        st.warning(f"⚠️ Error connecting to server: {str(e)}")
        return None

# Function to refresh patient data
def refresh_patient_data():
    with st.spinner("Refreshing patient data..."):
        fhir_patient = fetch_patient_data()
        if fhir_patient:
            st.session_state.current_patient = create_patient_object(fhir_patient)
            st.session_state.fhir_patient = fhir_patient
            st.success("✅ Patient data refreshed successfully!")
            st.rerun()
        else:
            st.error("❌ Failed to refresh patient data from server")

# Set page configuration
st.set_page_config(
    page_title="EHR Guidelines Assistant",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state variables if they don't exist
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'home'
if 'selected_guideline' not in st.session_state:
    st.session_state.selected_guideline = None
if 'current_patient' not in st.session_state:
    # Try to fetch patient from Express server first
    fhir_patient = fetch_patient_data()
    if fhir_patient:
        st.session_state.current_patient = create_patient_object(fhir_patient)
        st.session_state.fhir_patient = fhir_patient
    else:
        # Fallback to sample data if server fetch fails
        print("Falling back to sample patient data due to server fetch failure.")
        st.session_state.current_patient = get_sample_patient('diabetes')
        st.session_state.fhir_patient = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'search_results' not in st.session_state:
    st.session_state.search_results = []

# Apply custom CSS
st.markdown("""
<style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .stApp {
        background-color: #f8fafc;
    }
    .patient-banner {
        background-color: #eff6ff;
        border: 1px solid #dbeafe;
        border-radius: 0.5rem;
        padding: 0.75rem;
        margin-bottom: 1rem;
    }
    .document-viewer {
        background-color: white;
        border: 1px solid #e2e8f0;
        border-radius: 0.5rem;
        padding: 1rem;
        height: calc(100vh - 10rem);
        overflow-y: auto;
    }
    .chat-message {
        padding: 0.75rem;
        border-radius: 0.5rem;
        margin-bottom: 0.75rem;
        max-width: 80%;
    }
    .user-message {
        background-color: #3b82f6;
        color: white;
        margin-left: auto;
    }
    .assistant-message {
        background-color: #f1f5f9;
        border: 1px solid #e2e8f0;
    }
    .system-message {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        color: #64748b;
    }
    .note-container {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 0.5rem;
        padding: 1rem;
        font-family: monospace;
        white-space: pre-wrap;
    }
    .guideline-reference {
        background-color: #eff6ff;
        border-left: 4px solid #60a5fa;
        padding: 0.75rem;
        margin-top: 0.75rem;
        border-radius: 0 0.25rem 0.25rem 0;
    }
    .footer {
        position: fixed;
        bottom: 0;
        right: 0;
        padding: 0.5rem;
        font-size: 0.8rem;
        color: #94a3b8;
    }
    .refresh-button {
        color: #3b82f6;
        background-color: #eff6ff;
        border: 1px solid #dbeafe;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        cursor: pointer;
        font-size: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)

# Add patient refresh button in a container at the top
with st.container():
    col1, col2 = st.columns([6, 1])
    with col2:
        if st.button("🔄 Refresh Patient", help="Refresh patient data from FHIR server"):
            refresh_patient_data()

# Render patient context banner
render_patient_context(st.session_state.current_patient)

# Render sidebar navigation
render_sidebar()

# Render main content based on current page
if st.session_state.current_page == 'home':
    if st.session_state.selected_guideline:
        render_document_viewer(st.session_state.selected_guideline, st.session_state.current_patient)
    else:
        st.markdown("""
        <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 70vh;">
            <div style="font-size: 4rem; color: #cbd5e1; margin-bottom: 1rem;">📚</div>
            <h2 style="color: #334155; margin-bottom: 0.5rem;">Welcome to MedGuide</h2>
            <p style="color: #64748b; text-align: center; max-width: 400px;">
                Select a guideline document from the sidebar or search for specific clinical recommendations.
            </p>
        </div>
        """, unsafe_allow_html=True)
elif st.session_state.current_page == 'prompts':
    render_clinician_prompts()
elif st.session_state.current_page == 'note':
    render_note_generator()

# If FHIR data is available, add an expandable section to view it
if st.session_state.get('fhir_patient'):
    with st.expander("View Raw FHIR Patient Data"):
        st.json(st.session_state.fhir_patient)

# Footer
st.markdown("""
<div class="footer">
    Powered by Claude 3 Sonnet
</div>
""", unsafe_allow_html=True)
