# =====================================
# data/__init__.py
# =====================================

# Import sample data functions
from .sample_data import (
    get_sample_guidelines,
    get_sample_uploaded_docs,
    get_sample_patient,
    get_guideline_content
)

# Define __all__ to control what's imported with "from data import *"
__all__ = [
    'get_sample_guidelines',
    'get_sample_uploaded_docs',
    'get_sample_patient',
    'get_guideline_content'
]