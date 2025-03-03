# =====================================
# utils/pdf_utils.py
# =====================================
import PyPDF2
import io
import os
import base64
from typing import Dict, List, Any, Optional, Tuple
import streamlit as st

def extract_text_from_pdf(pdf_file: io.BytesIO) -> Tuple[str, Dict[int, str]]:
    """
    Extract text from a PDF file
    Returns both full text and text by page
    """
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        full_text = ""
        text_by_page = {}
        
        for i, page in enumerate(pdf_reader.pages):
            page_text = page.extract_text()
            full_text += page_text + "\n\n"
            text_by_page[i+1] = page_text
            
        return full_text, text_by_page
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return "", {}

def get_pdf_page_count(pdf_file: io.BytesIO) -> int:
    """Get the number of pages in a PDF file"""
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        return len(pdf_reader.pages)
    except Exception as e:
        print(f"Error getting PDF page count: {e}")
        return 0

def extract_pdf_metadata(pdf_file: io.BytesIO) -> Dict[str, Any]:
    """Extract metadata from a PDF file"""
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        metadata = pdf_reader.metadata
        if metadata:
            return {
                "title": metadata.get("/Title", ""),
                "author": metadata.get("/Author", ""),
                "subject": metadata.get("/Subject", ""),
                "creator": metadata.get("/Creator", ""),
                "producer": metadata.get("/Producer", ""),
                "creation_date": metadata.get("/CreationDate", ""),
                "modification_date": metadata.get("/ModDate", "")
            }
        return {}
    except Exception as e:
        print(f"Error extracting PDF metadata: {e}")
        return {}

def pdf_to_base64(pdf_file: io.BytesIO) -> str:
    """Convert PDF file to base64 string"""
    pdf_file.seek(0)
    return base64.b64encode(pdf_file.read()).decode('utf-8')

def display_pdf(pdf_file: io.BytesIO, width: int = 700, height: int = 800) -> None:
    """Display a PDF file in Streamlit"""
    base64_pdf = pdf_to_base64(pdf_file)
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="{width}" height="{height}" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

def display_pdf_page(pdf_file: io.BytesIO, page_num: int = 1, width: int = 700, height: int = 800) -> None:
    """Display a specific page of a PDF file in Streamlit"""
    try:
        # Create a new PDF with just the specified page
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        pdf_writer = PyPDF2.PdfWriter()
        
        if 1 <= page_num <= len(pdf_reader.pages):
            pdf_writer.add_page(pdf_reader.pages[page_num - 1])
            
            output = io.BytesIO()
            pdf_writer.write(output)
            output.seek(0)
            
            # Display the single page
            base64_pdf = base64.b64encode(output.read()).decode('utf-8')
            pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="{width}" height="{height}" type="application/pdf"></iframe>'
            st.markdown(pdf_display, unsafe_allow_html=True)
        else:
            st.error(f"Page number {page_num} is out of range. The PDF has {len(pdf_reader.pages)} pages.")
    except Exception as e:
        st.error(f"Error displaying PDF page: {e}")