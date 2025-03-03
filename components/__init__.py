# =====================================
# components/__init__.py
# =====================================

# Import all component modules
from .clinician_prompts import render_clinician_prompts
from .document_viewer import render_document_viewer
from .note_generator import render_note_generator
from .patient_context import render_patient_context, get_patient_labs_string
from .sidebar import render_sidebar

# Define __all__ to control what's imported with "from components import *"
__all__ = [
    'render_clinician_prompts',
    'render_document_viewer',
    'render_note_generator',
    'render_patient_context',
    'get_patient_labs_string',
    'render_sidebar'
]