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
        
        # Initialize message history if not exists
        if 'messages' not in st.session_state:
            st.session_state.messages = []
            
            # Add initial system message about patient context
            patient_info = f"Patient: {patient.get('name', 'Unknown')}, {patient.get('age', 'Unknown')} years old"
            if 'vitals' in patient and 'bloodPressure' in patient['vitals']:
                patient_info += f", BP {patient['vitals']['bloodPressure']}"
            if 'labs' in patient and 'HbA1c' in patient['labs']:
                patient_info += f", HbA1c {patient['labs']['HbA1c']}%"
                
            st.session_state.messages.append({
                "role": "system", 
                "content": f"I'm analyzing {guideline['title']} for {patient_info}."
            })
        
        # Patient-specific recommendations - only add to history if not already there
        if not any(msg.get("content", "").startswith("Based on this guideline") for msg in st.session_state.messages if msg.get("role") == "assistant"):
            # Get recommendations from Claude API
            claude_api = ClaudeAPI(st.session_state.get('claude_api_key', 'demo_key'))
            recommendations = claude_api.query_guidelines(
                query="best medication regimen and relevant recommendations for this patient",
                patient_context=patient,
                document_ids=[guideline['id']]
            ).get('recommendations', [])
            
            # Format recommendations as a single message
            if recommendations:
                rec_text = "Based on this guideline and the patient's data, here are my recommendations:\n\n"
                
                # Deduplicate recommendations by text content
                unique_recs = {}
                for rec in recommendations:
                    unique_recs[rec.get('text', '')] = rec
                
                for rec in unique_recs.values():
                    rec_text += f"• {rec.get('explanation', '')}\n"
                    rec_text += f"  \"{rec.get('text', '')}\"\n"
                    rec_text += f"  Source: {rec.get('source', '')}, Page {rec.get('page', '')}\n\n"
                
                # Add to session state
                st.session_state.messages.append({"role": "assistant", "content": rec_text})
        
        # Display message history
        for message in st.session_state.messages:
            if message["role"] != "system":  # Don't display system messages
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
        
        # Query interface
        prompt = st.chat_input("Ask about this guideline for your patient...")
        
        if prompt:
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Display user message
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Get Claude response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    # Create message placeholder
                    message_placeholder = st.empty()
                    
                    # Query Claude
                    claude_api = ClaudeAPI(st.session_state.get('claude_api_key', 'demo_key'))
                    response = claude_api.query_guidelines(
                        query=prompt,
                        patient_context=patient,
                        document_text=content
                    )
                    
                    # Format the response
                    recommendations = response.get('recommendations', [])
                    full_response = ""
                    
                    if recommendations:
                        for rec in recommendations:
                            if rec.get('explanation'):
                                full_response += f"{rec.get('explanation')}\n\n"
                            
                            if rec.get('text'):
                                full_response += f"\"{rec.get('text')}\"\n\n"
                                
                            if rec.get('source') or rec.get('page'):
                                source_info = f"Source: {rec.get('source', '')}"
                                if rec.get('page') and rec.get('page') != 'N/A':
                                    source_info += f", Page {rec.get('page')}"
                                full_response += f"*{source_info}*\n\n"
                    else:
                        full_response = "I couldn't find specific information about that in the guidelines. Is there anything else you'd like to know?"
                    
                    # Display response
                    message_placeholder.markdown(full_response)
                    
                    # Add response to message history
                    st.session_state.messages.append({"role": "assistant", "content": full_response})
        
        # Related guidelines (kept from original)
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