# =====================================
# components/clinician_prompts.py
# =====================================
import streamlit as st
import json
import time
import re
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
    
    # Get selected condition from session state or extract from patient diagnosis
    selected_condition = st.session_state.get('selected_condition', '')
    
    # If condition isn't explicitly set, try to get it from patient diagnosis
    if not selected_condition and patient.get('diagnosis'):
        selected_condition = patient.get('diagnosis').lower()
    
    # If still no condition is found, default to a safe value
    if not selected_condition:
        selected_condition = "general"
    
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
                # Display the assistant message with proper source formatting
                st.markdown(f"""
                <div class="chat-message assistant-message">
                    <p>{content}</p>
                """, unsafe_allow_html=True)
                
                # Add source information if available
                if source:
                    st.markdown(f"""
                    <div style="display: flex; align-items: center; margin-top: 0.5rem; padding: 0.25rem 0.5rem; background-color: #3b82f6; color: white; border-radius: 0.25rem; font-size: 0.75rem; width: fit-content;">
                        <span style="margin-right: 0.25rem;">📚</span>
                        <span>{source}</span>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Close the assistant message div
                st.markdown("</div>", unsafe_allow_html=True)

    # Display condition-specific prompt suggestions
    if len(st.session_state.chat_history) < 2:  # Only show if chat just started
        st.markdown(f"### Suggested for this patient")
        
        # Default prompts
        general_prompts = [
            "Generate a succinct assessment and plan for my note",
            "What monitoring frequency is recommended for this patient?",
            "Are there any drug interactions I should be aware of?"
        ]
        
        # Condition-specific prompts
        condition_prompts = get_condition_specific_prompts(selected_condition)
        
        # Combine general and condition-specific prompts
        suggested_prompts = condition_prompts + general_prompts
        suggested_prompts = suggested_prompts[:6]  # Limit to 6 prompts
        
        col1, col2 = st.columns(2)
        with col1:
            for i in range(0, len(suggested_prompts), 2):
                if i < len(suggested_prompts):
                    if st.button(suggested_prompts[i], key=f"suggest_{i}", use_container_width=True):
                        handle_user_input(suggested_prompts[i], claude_api, patient, selected_condition)
        with col2:
            for i in range(1, len(suggested_prompts), 2):
                if i < len(suggested_prompts):
                    if st.button(suggested_prompts[i], key=f"suggest_{i}", use_container_width=True):
                        handle_user_input(suggested_prompts[i], claude_api, patient, selected_condition)
    
    # Input for new message
    user_input = st.text_input("Ask about guidelines or recommendations", key="user_input")
    col1, col2 = st.columns([5, 1])
    with col2:
        if st.button("Send", use_container_width=True) or (user_input and user_input != st.session_state.get('last_input', '')):
            if user_input:
                st.session_state['last_input'] = user_input
                handle_user_input(user_input, claude_api, patient, selected_condition)

def get_condition_specific_prompts(condition):
    """Return condition-specific prompt suggestions based on the medical condition."""
    condition = condition.lower()
    
    # Dictionary of condition-specific prompts
    condition_prompts = {
        "diabetes": [
            "What medication adjustments are recommended for HbA1c > 8%?",
            "What BP targets should I aim for with this diabetic patient?",
            "When should I consider adding a statin given the patient's LDL?"
        ],
        "breast cancer": [
            "What are the current treatment options for breast cancer?",
            "What are the guidelines for breast cancer screening?",
            "What are the recommended follow-up protocols after breast cancer treatment?"
        ],
        "hypertension": [
            "What are the BP targets for patients with hypertension?",
            "What medications are first-line for hypertension treatment?",
            "When should I consider combination therapy for hypertension?"
        ],
        "cardiovascular disease": [
            "What are the lipid targets for patients with established CVD?",
            "When should antiplatelet therapy be considered?",
            "What lifestyle modifications are recommended for CVD patients?"
        ]
    }
    
    # Check if we have specific prompts for this condition
    for key in condition_prompts:
        if key in condition:
            return condition_prompts[key]
    
    # Default to general clinical prompts if no match
    return [
        "What are the current treatment guidelines for this condition?",
        "What are the recommended monitoring parameters?",
        "What are the most common side effects to monitor?"
    ]

def handle_user_input(user_input, claude_api, patient, condition="general"):
    # Add user message to chat history
    st.session_state.chat_history.append({
        "role": "user",
        "content": user_input
    })
    
    # Show thinking indicator
    with st.spinner("AI is thinking..."):
        # Get response from Claude API with the condition context
        response = claude_api.query_guidelines(user_input, patient, condition)
        recommendations = response.get("recommendations", [])
        
        if recommendations:
            rec = recommendations[0]  # Get first recommendation
            
            explanation = rec.get('explanation', '')
            text = rec.get('text', '')
            source_text = f"{rec.get('source', '')}, page {rec.get('page', '')}"
            
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": f"{explanation}\n\n\"{text}\"",
                "source": source_text
            })
        else:
            # Provide a more condition-specific fallback message
            fallback_message = f"I couldn't find specific guideline recommendations for your query about {condition}. Please try asking a different question or provide more context."
            
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": fallback_message
            })
    
    # Rerun to update the UI
    st.rerun()