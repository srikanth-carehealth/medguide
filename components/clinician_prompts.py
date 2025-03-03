# =====================================
# components/clinician_prompts.py
# =====================================
import streamlit as st
import json
import time
from utils.claude_api import ClaudeAPI

def render_clinician_prompts():
    # Initialize chat history if not exists
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = [
            {
                "role": "system",
                "content": "I can help you find relevant guidelines and recommendations for your patient. What would you like to know?"
            }
        ]
    
    # Initialize Claude API
    claude_api = ClaudeAPI(st.session_state.get('claude_api_key', 'demo_key'))
    
    # Current patient context
    patient = st.session_state.current_patient
    
    # Page header
    st.markdown(f"## MedGuide Assistant")
    
    # Display chat messages
    for message in st.session_state.chat_history:
        role = message.get("role", "user")
        content = message.get("content", "")
        is_note = message.get("is_note", False)
        note = message.get("note", None)
        source = message.get("source", None)
        
        if role == "user":
            st.markdown(f"""
            <div class="chat-message user-message">
                {content}
            </div>
            """, unsafe_allow_html=True)
        elif role == "system":
            st.markdown(f"""
            <div class="chat-message system-message">
                {content}
            </div>
            """, unsafe_allow_html=True)
        else:  # assistant
            if is_note and note:
                st.markdown(f"""
                <div class="chat-message assistant-message">
                    <p>{content}</p>
                    <div style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 0.5rem; padding: 1rem; margin-top: 0.75rem;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                            <div style="display: flex; align-items: center;">
                                <span style="margin-right: 0.25rem;">📄</span>
                                <span style="font-weight: 500; color: #334155;">{note.get("title", "Clinical Note")}</span>
                            </div>
                            <button id="copy-button" 
                                onclick="navigator.clipboard.writeText(`{note.get('content', '')}`.replace(/\\n/g, '\\n')); 
                                document.getElementById('copy-button').innerHTML = '✓ Copied!'; 
                                setTimeout(() => document.getElementById('copy-button').innerHTML = '📋 Copy', 2000);"
                                style="background-color: #eff6ff; color: #3b82f6; border: none; padding: 0.25rem 0.5rem; border-radius: 0.25rem; font-size: 0.75rem; cursor: pointer;">
                                📋 Copy
                            </button>
                        </div>
                        <pre style="background-color: white; border: 1px solid #e2e8f0; padding: 0.5rem; border-radius: 0.25rem; font-family: monospace; font-size: 0.75rem; white-space: pre-wrap; overflow-x: auto;">{note.get("content", "")}</pre>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                source_html = ""
                if source:
                    source_html = f"""
                    <div style="display: flex; align-items: center; margin-top: 0.5rem; padding: 0.25rem 0.5rem; background-color: #3b82f6; color: white; border-radius: 0.25rem; font-size: 0.75rem; width: fit-content;">
                        <span style="margin-right: 0.25rem;">📚</span>
                        <span>{source}</span>
                    </div>
                    """
                
                st.markdown(f"""
                <div class="chat-message assistant-message">
                    <p>{content}</p>
                    {source_html}
                </div>
                """, unsafe_allow_html=True)

    # Display suggested prompts in two columns
    if len(st.session_state.chat_history) < 2:  # Only show if chat just started
        st.markdown("### Suggested for this patient")
        
        suggested_prompts = [
            "What medication adjustments are recommended for HbA1c > 8%?",
            "What BP targets should I aim for with this diabetic patient?",
            "When should I consider adding a statin given the patient's LDL?",
            "Generate a succinct assessment and plan for my note",
            "What monitoring frequency is recommended for this patient?",
            "Are there any drug interactions I should be aware of?"
        ]
        
        col1, col2 = st.columns(2)
        with col1:
            for i in range(0, len(suggested_prompts), 2):
                if i < len(suggested_prompts):
                    if st.button(suggested_prompts[i], key=f"suggest_{i}", use_container_width=True):
                        handle_user_input(suggested_prompts[i], claude_api, patient)
        with col2:
            for i in range(1, len(suggested_prompts), 2):
                if i < len(suggested_prompts):
                    if st.button(suggested_prompts[i], key=f"suggest_{i}", use_container_width=True):
                        handle_user_input(suggested_prompts[i], claude_api, patient)
    
    # Input for new message
    user_input = st.text_input("Ask about guidelines or recommendations", key="user_input")
    col1, col2 = st.columns([5, 1])
    with col2:
        if st.button("Send", use_container_width=True) or (user_input and user_input != st.session_state.get('last_input', '')):
            if user_input:
                st.session_state['last_input'] = user_input
                handle_user_input(user_input, claude_api, patient)

def handle_user_input(user_input, claude_api, patient):
    # Add user message to chat history
    st.session_state.chat_history.append({
        "role": "user",
        "content": user_input
    })
    
    # Show thinking indicator
    with st.spinner("AI is thinking..."):
        # Check if the user is asking for a note
        if "assessment" in user_input.lower() and "plan" in user_input.lower() and "note" in user_input.lower():
            # Generate clinical note
            response = claude_api.generate_clinical_note(patient, "diabetes" if "diabetes" in patient["diagnosis"].lower() else "general")
            
            # Add assistant response with note
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": "I've prepared an assessment and plan based on this patient's information and relevant guidelines:",
                "is_note": True,
                "note": {
                    "title": response.get("title", "Clinical Note"),
                    "content": response.get("content", "")
                }
            })
        else:
            # Query guidelines
            response = claude_api.query_guidelines(user_input, patient)
            recommendations = response.get("recommendations", [])
            
            if recommendations:
                rec = recommendations[0]  # Get first recommendation
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": f"{rec.get('explanation', '')}\n\n\"{rec.get('text', '')}\"",
                    "source": f"{rec.get('source', '')}, page {rec.get('page', '')}"
                })
            else:
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": "I couldn't find specific guideline recommendations for your query. Please try asking a different question or provide more context."
                })
    
    # Rerun to update the UI
    st.rerun()