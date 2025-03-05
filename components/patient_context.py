# =====================================
# components/patient_context.py
# =====================================
import streamlit as st
import streamlit.components.v1 as components  # Import for st.components.v1.html
import re
import requests
import json
import html
from datetime import datetime

# Function to fetch patient data from Express server
def fetch_patient_data():
    try:
        response = requests.get('http://localhost:3001/api/patient')
        if response.status_code == 200:
            raw_data = response.json()
            print(f"Raw FHIR patient data: {raw_data}")  # Log the raw data
            return raw_data
        else:
            st.error(f"Failed to retrieve patient data: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error connecting to server: {str(e)}")
        return None

# Function to extract patient name from FHIR patient resource
def get_patient_name(patient_data):
    if not patient_data or 'name' not in patient_data:
        return "Unknown Patient"
    
    name = patient_data['name'][0] if isinstance(patient_data['name'], list) else patient_data['name']
    
    if 'text' in name and name['text']:
        return sanitize_html(name['text'])
    
    given = ' '.join(name.get('given', [])) if 'given' in name else ''
    family = name.get('family', '')
    
    if given and family:
        return sanitize_html(f"{given} {family}")
    elif family:
        return sanitize_html(family)
    elif given:
        return sanitize_html(given)
    else:
        return "Unknown Patient"

# Function to extract patient age from FHIR patient resource
def get_patient_age(patient_data):
    if not patient_data or 'birthDate' not in patient_data:
        return "Unknown"
    
    try:
        birth_date = datetime.strptime(patient_data['birthDate'], '%Y-%m-%d')
        today = datetime.now()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        return sanitize_html(f"{age}")
    except Exception as e:
        st.warning(f"Could not calculate age: {str(e)}")
        return "Unknown"

# Function to extract diagnosis from FHIR patient resource
def get_patient_diagnosis(patient_data):
    if not patient_data:
        return "No diagnosis information"
    
    if 'extension' in patient_data:
        for ext in patient_data['extension']:
            if 'url' in ext and 'diagnosis' in ext['url']:
                return sanitize_html(ext.get('valueString', 'Unspecified diagnosis'))
    
    return "Diagnosis information not available"

# Function to extract recent labs from FHIR patient resource
def get_patient_labs(patient_data):
    labs = {}
    
    if not patient_data:
        return labs
    
    if 'extension' in patient_data:
        for ext in patient_data['extension']:
            if 'url' in ext and 'recentLabs' in ext['url']:
                if 'extension' in ext:
                    for lab_ext in ext['extension']:
                        if 'valueCoding' in lab_ext:
                            labs[lab_ext['valueCoding']['display']] = lab_ext['valueCoding']['code']
    
    if not labs:
        labs = {"Glucose": "95 mg/dL", "Hgb": "14.2 g/dL"}
    
    return labs

def sanitize_html(text):
    """Remove any HTML tags and escape HTML content"""
    if text is None:
        return ""
    
    # Convert to string if not already
    text_str = str(text)
    
    # Remove all HTML tags aggressively, including malformed ones
    stripped_text = re.sub(r'</?[^>]+/?>', '', text_str, flags=re.IGNORECASE)
    
    # Remove any remaining HTML entities (like &lt;, &gt;, etc.)
    stripped_text = re.sub(r'&[a-zA-Z0-9#]+;', '', stripped_text)
    
    # Trim any extra whitespace
    stripped_text = stripped_text.strip()
    
    # Escape any remaining special characters to prevent XSS
    return html.escape(stripped_text)

def render_patient_context(patient):
    if not patient:
        st.warning("No patient data available")
        return
    
    # Extract patient data and sanitize thoroughly
    patient_name = sanitize_html(patient.get('name', 'Unknown'))
    patient_age = sanitize_html(str(patient.get('age', '')))
    patient_diagnosis = sanitize_html(patient.get('diagnosis', ''))
    
    # Log the sanitized values for debugging
    print(f"Sanitized patient_name: {patient_name}")
    print(f"Sanitized patient_age: {patient_age}")
    print(f"Sanitized patient_diagnosis: {patient_diagnosis}")
    
    # Prepare diagnosis HTML
    diagnosis_html = ""
    if patient_diagnosis:
        diagnosis_html = f'<p style="font-size: 0.75rem; margin: 0; color: #3b82f6;">{patient_diagnosis}</p>'
    
    # Prepare labs HTML
    labs_html = ""
    labs_string = get_patient_labs_string(patient)
    if labs_string:
        labs_html = f'''
        <span style="font-size: 0.75rem; color: #3b82f6;">
            <span style="font-weight: 500;">Recent:</span> {labs_string}
        </span>
        '''
    
    # Create the complete HTML for the patient banner with simplified structure
    patient_html = f'''
    <div class="patient-banner">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <h3 style="font-size: 0.875rem; font-weight: 500; margin: 0; color: #1e40af;">{patient_name}, {patient_age}</h3>
            {labs_html}
        </div>
        {diagnosis_html}
    </div>
    '''
    
    # Log the final HTML for debugging
    print(f"Final patient_html: {patient_html}")
    
    # Use st.components.v1.html to render the HTML instead of st.markdown
    components.html(patient_html, height=100)
    
 
def get_patient_labs_string(patient):
    labs = patient.get('recentLabs', {})
    if not labs:
        return ""
        
    labs_strings = []
    for key, value in labs.items():
        # Sanitize lab values thoroughly
        sanitized_key = sanitize_html(key)
        sanitized_value = sanitize_html(str(value))
        labs_strings.append(f"{sanitized_key}: {sanitized_value}")
    
    # Sanitize the final string
    return sanitize_html(", ".join(labs_strings))