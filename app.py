import streamlit as st
import os
from PIL import Image
import base64
from datetime import datetime
import sys


from components.sidebar import render_sidebar
from components.document_viewer import render_document_viewer
from components.clinician_prompts import render_clinician_prompts
from components.note_generator import render_note_generator
from components.patient_context import render_patient_context
from data.sample_data import get_sample_patient

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
    st.session_state.current_patient = get_sample_patient('diabetes')
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
</style>
""", unsafe_allow_html=True)

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
    render_note_generator('diabetes')
elif st.session_state.current_page == 'her2_note':
    render_note_generator('her2')

# Footer
st.markdown("""
<div class="footer">
    Powered by Claude 3 Sonnet
</div>
""", unsafe_allow_html=True)