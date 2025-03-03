# =====================================
# utils/__init__.py
# =====================================

# Import the API classes
from .claude_api import ClaudeAPI
from .perplexity_api import PerplexityAPI

# Import PDF utility functions
from .pdf_utils import (
    extract_text_from_pdf,
    get_pdf_page_count,
    extract_pdf_metadata,
    pdf_to_base64,
    display_pdf,
    display_pdf_page
)

# Define __all__ to control what's imported with "from utils import *"
__all__ = [
    'ClaudeAPI',
    'PerplexityAPI',
    'extract_text_from_pdf',
    'get_pdf_page_count',
    'extract_pdf_metadata',
    'pdf_to_base64',
    'display_pdf',
    'display_pdf_page'
]