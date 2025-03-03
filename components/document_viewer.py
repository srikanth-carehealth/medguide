# =====================================
# components/document_viewer.py
# =====================================
import streamlit as st
import io
import os
from utils.claude_api import ClaudeAPI
from utils.pdf_utils import display_pdf, display_pdf_page
from data.sample_data import get_guideline_content

def render_document_viewer(guideline, patient):
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown(f"## {guideline['title']}")
        st.markdown(f"<p style='color: #64748b;'>{guideline['source']} • Last updated: {guideline['lastUpdated']}</p>", unsafe_allow_html=True)
        
        # Mock document content (in a real app, this would be a PDF viewer)
        content = get_guideline_content(guideline['id'])
        
        # Page navigation
        page_col1, page_col2, page_col3 = st.columns([1, 1, 5])
        with page_col1:
            if st.button("◀ Previous"):
                # Navigate to previous page
                pass
        with page_col2:
            if st.button("Next ▶"):
                # Navigate to next page
                pass
        with page_col3:
            st.markdown(f"<p style='text-align: right;'>Page 42 of 128</p>", unsafe_allow_html=True)
        
        # Document content
        st.markdown("""
        <div class="document-viewer">
            <div style="max-width: 600px; margin: 0 auto;">
                <div style="margin-bottom: 1.5rem;">
                    <h3 style="font-size: 1.25rem; font-weight: bold; text-align: center; margin-bottom: 0.5rem;">Glycemic Targets and Management Guidelines</h3>
                    <h4 style="font-size: 1.125rem; font-weight: 500; text-align: center; color: #64748b; margin-bottom: 1rem;">American Diabetes Association, 2024</h4>
                </div>
                
                <div style="font-size: 0.875rem; line-height: 1.5;">
                    <p style="text-align: justify; margin-bottom: 1rem;">Regular monitoring of glycemia in patients with diabetes is crucial to assess treatment efficacy and reduce risk of hypoglycemia and hyperglycemia. The advent of continuous glucose monitoring (CGM) technology has revolutionized this aspect of diabetes care.</p>
                    
                    <h4 style="font-weight: bold; margin-top: 1rem; margin-bottom: 0.5rem;">Recommendations</h4>
                    
                    <div style="padding: 0.75rem; background-color: #fef9c3; border-left: 4px solid #facc15; margin-bottom: 1rem;">
                        <p><strong>8.1</strong> Most patients with diabetes should be assessed using glycated hemoglobin (HbA1c) testing at least twice per year. <em>(Grade A)</em></p>
                    </div>
                    
                    <div style="padding: 0.75rem; background-color: #dbeafe; border-left: 4px solid #60a5fa; margin-bottom: 1rem;">
                        <p><strong>8.2</strong> When glycemic targets are not being met, quarterly assessments using HbA1c testing are recommended. <em>(Grade B)</em></p>
                    </div>
                    
                    <p style="text-align: justify; margin-bottom: 1rem;">All adult patients with diabetes should have an individualized glycemic target based on their duration of diabetes, age/life expectancy, comorbid conditions, known cardiovascular disease or advanced microvascular complications, hypoglycemia unawareness, and individual patient considerations.</p>
                    
                    <div style="padding: 0.75rem; background-color: #fef9c3; border-left: 4px solid #facc15; margin-bottom: 1rem;">
                        <p><strong>8.5</strong> For patients with Type 2 diabetes with HbA1c levels <strong>&gt; 8.0%</strong>, clinicians should consider intensifying pharmacologic therapy, adding additional agents, or referral to a specialist. <em>(Grade A)</em></p>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### AI Assistant")
        
        # Patient-specific recommendations
        st.markdown("#### Patient-specific Recommendations")
        
        # Get recommendations from Claude API
        claude_api = ClaudeAPI(st.session_state.get('claude_api_key', 'demo_key'))
        recommendations = claude_api.query_guidelines(
            query="relevant recommendations for this patient",
            patient_context=patient,
            document_ids=[guideline['id']]
        ).get('recommendations', [])
        
        for rec in recommendations:
            st.markdown(f"""
            <div style="padding: 0.75rem; background-color: #dbeafe; border-radius: 0.5rem; margin-bottom: 0.75rem; font-size: 0.875rem;">
                <p style="margin-bottom: 0.5rem;">{rec.get('explanation', '')}</p>
                <p style="font-weight: 500;">"{rec.get('text', '')}"</p>
                <p style="font-size: 0.75rem; color: #3b82f6; margin-top: 0.5rem;">Page {rec.get('page', '')}, {rec.get('source', '')}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Ask about document
        st.markdown("#### Ask about this document")
        question = st.text_input("Ask a question about this guideline", key="guideline_question")
        # Inside your "Ask" button click handler:
        if st.button("Ask", key="ask_guideline_button"):
            if question:
                # Add debug info
                st.write(f"Debug: Question received: '{question}'")
                
                # Query Claude about the document
                with st.spinner("Getting answer..."):
                    claude_api = ClaudeAPI(st.session_state.get('claude_api_key', 'demo_key'))
                    
                # Get the guideline content
                content = get_guideline_content(guideline['id'])
                st.write(f"Debug: Content length: {len(content)} characters")
                
                # Query Claude using the document content and the question
                st.write("Debug: Sending query to Claude API...")
                response = claude_api.query_guidelines(
                    query=question,
                    patient_context=patient,
                    document_text=content
                )
                
                # Inspect the raw response
                st.write("Debug: Raw API response:")
                st.write(response)
                
                # Display the response
                recommendations = response.get('recommendations', [])
                st.write(f"Debug: Found {len(recommendations)} recommendations")
                
                if recommendations:
                    for rec in recommendations:
                        st.markdown(f"""
                        <div style="padding: 0.75rem; background-color: #f0f9ff; border-radius: 0.5rem; margin-top: 0.75rem; font-size: 0.875rem;">
                            <p>{rec.get('explanation', '')}</p>
                            <p style="font-style: italic;">"{rec.get('text', '')}"</p>
                            <p style="font-size: 0.75rem; color: #3b82f6; margin-top: 0.5rem;">Page {rec.get('page', '')}, {rec.get('source', '')}</p>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("I couldn't find a specific answer to your question in this document. Please try rephrasing or ask a different question.")
        
        # Related guidelines
        st.markdown("#### Related Guidelines")
        
        st.markdown("""
        <div style="padding: 0.5rem; border: 1px solid #e2e8f0; border-radius: 0.375rem; font-size: 0.875rem; margin-bottom: 0.5rem; cursor: pointer; hover:bg-gray-50;">
            <p style="font-weight: 500; color: #3b82f6;">Hypertension Management in Diabetes</p>
            <p style="font-size: 0.75rem; color: #64748b;">JNC 8 Guidelines, p.18-22</p>
        </div>
        
        <div style="padding: 0.5rem; border: 1px solid #e2e8f0; border-radius: 0.375rem; font-size: 0.875rem; cursor: pointer; hover:bg-gray-50;">
            <p style="font-weight: 500; color: #3b82f6;">Medication Adjustments for HbA1c > 8%</p>
            <p style="font-size: 0.75rem; color: #64748b;">ADA Guidelines 2024, p.45-48</p>
        </div>
        """, unsafe_allow_html=True)