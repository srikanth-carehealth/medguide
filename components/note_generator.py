# =====================================
# components/note_generator.py
# =====================================
import streamlit as st
import streamlit.components.v1 as components  # Import for st.components.v1.html
import json
import time
from utils.claude_api import ClaudeAPI

def render_note_generator():
    # Initialize Claude API
    claude_api = ClaudeAPI(st.session_state.get('claude_api_key', 'demo_key'))
    
    # Current patient context and condition
    patient = st.session_state.current_patient
    condition_type = st.session_state.get('selected_condition', 'diabetes')
    
    # Set theme based on condition type
    if "her2" in condition_type or "breast cancer" in condition_type:
        theme_color = "#db2777"  # pink-600
        theme_light = "#fce7f3"  # pink-100
        theme_title = "HER2+ Breast Cancer Treatment Plan"
        theme_subtitle = "Neoadjuvant regimen with guideline references"
    elif "diabetes" in condition_type:
        theme_color = "#2563eb"  # blue-600
        theme_light = "#dbeafe"  # blue-100
        theme_title = "Diabetes Management Plan"
        theme_subtitle = "Glycemic control and complication prevention"
    elif "hypertension" in condition_type or "blood pressure" in condition_type:
        theme_color = "#059669"  # emerald-600
        theme_light = "#d1fae5"  # emerald-100
        theme_title = "Hypertension Management Plan"
        theme_subtitle = "Blood pressure management and cardiovascular risk reduction"
    elif "lipid" in condition_type or "cholesterol" in condition_type:
        theme_color = "#7c3aed"  # violet-600
        theme_light = "#ede9fe"  # violet-100
        theme_title = "Lipid Management Plan"
        theme_subtitle = "Cholesterol management and cardiovascular risk reduction"
    else:
        # Default/generic theme for any other condition
        theme_color = "#6366f1"  # indigo-600
        theme_light = "#e0e7ff"  # indigo-100
        theme_title = f"{patient.get('diagnosis', condition_type.title())} Management Plan"
        theme_subtitle = "Evidence-based recommendations for patient care"
    
    # Page header
    st.markdown(f"""
    <div style="background-color: {theme_color}; padding: 1rem; border-radius: 0.5rem 0.5rem 0 0; color: white;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div style="display: flex; align-items: center;">
                <span style="margin-right: 0.5rem; font-size: 1.25rem;">📄</span>
                <h2 style="font-weight: 600; font-size: 1.25rem; margin: 0;">{theme_title}</h2>
            </div>
            <span style="font-size: 0.75rem; background-color: rgba(255,255,255,0.2); padding: 0.25rem 0.5rem; border-radius: 0.25rem;">Guideline-Informed</span>
        </div>
        <p style="margin-top: 0.25rem; font-size: 0.875rem; color: rgba(255,255,255,0.8);">
            {theme_subtitle}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Patient context banner
    patient_context_html = f"""
    <div style="background-color: {theme_light}; padding: 0.75rem; border-bottom: 1px solid rgba(0,0,0,0.1);">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <span style="font-size: 0.875rem; font-weight: 500; color: {theme_color};">{patient['name']}, {patient['age']}</span>
                <span style="font-size: 0.75rem; color: {theme_color}; margin-left: 0.5rem;">{patient['diagnosis']}</span>
            </div>
            <div style="font-size: 0.75rem; color: {theme_color};">
                {get_patient_labs_string(patient)}
            </div>
        </div>
    </div>
    """
    components.html(patient_context_html, height=50)  # Adjust height as needed
    
    # Main content
    st.markdown("""
    <div style="background-color: white; padding: 1rem; border: 1px solid #e2e8f0; border-radius: 0 0 0.5rem 0.5rem;">
    """, unsafe_allow_html=True)
    
    # Note title and actions
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"""
        <div style="display: flex; align-items: center;">
            <span style="margin-right: 0.5rem; color: {theme_color};">📄</span>
            <h3 style="font-weight: 500; color: #334155; margin: 0;">Generated Assessment & Plan</h3>
        </div>
        """, unsafe_allow_html=True)
    
    # Generate note if it doesn't exist in session state or condition has changed
    if 'current_note' not in st.session_state or st.session_state.get('current_note_type') != condition_type:
        with st.spinner("Generating clinical note..."):
            response = claude_api.generate_clinical_note(patient, condition_type)
            st.session_state.current_note = response.get("content", "Error generating note")
            st.session_state.current_note_type = condition_type
    
    # Display note content
    note_container = st.container()
    with note_container:
        # Editing and copying options
        edit_col, copy_col = st.columns([1, 1])
        
        with edit_col:
            if 'note_editing' not in st.session_state:
                st.session_state.note_editing = False
            
            if st.button("✏️ Edit Note" if not st.session_state.note_editing else "Cancel Edit", use_container_width=True):
                st.session_state.note_editing = not st.session_state.note_editing
        
        with copy_col:
            if st.button("📋 Copy to Clipboard", use_container_width=True):
                st.write(f'<div id="copy-trigger" data-content="{st.session_state.current_note.replace(chr(10), "\\n").replace(chr(13), "\\r")}" style="display:none"></div>', unsafe_allow_html=True)
                st.markdown("""
                <script>
                    // Wait for the copy-trigger element to appear
                    const checkExist = setInterval(function() {
                        const copyTrigger = document.getElementById('copy-trigger');
                        if (copyTrigger) {
                            clearInterval(checkExist);
                            const content = copyTrigger.getAttribute('data-content');
                            navigator.clipboard.writeText(content);
                            
                            // Show success message
                            const copyButton = document.querySelector("button:contains('Copy to Clipboard')");
                            if (copyButton) {
                                copyButton.innerText = "✓ Copied!";
                                setTimeout(() => copyButton.innerText = "📋 Copy to Clipboard", 2000);
                            }
                        }
                    }, 100);
                </script>
                """, unsafe_allow_html=True)
        
        # Note content
        if st.session_state.note_editing:
            edited_note = st.text_area("Edit Note", st.session_state.current_note, height=400)
            save_col, _ = st.columns([1, 3])
            with save_col:
                if st.button("💾 Save Changes", use_container_width=True):
                    st.session_state.current_note = edited_note
                    st.session_state.note_editing = False
                    st.rerun()
        else:
            # Format the note with proper line breaks
            formatted_note = st.session_state.current_note.replace("\n", "<br>")
            note_html = f"""
            <div class="note-container" style="line-height: 1.6; font-size: 0.875rem;">
                <div style="margin-bottom: 1rem;">{formatted_note}</div>
            </div>
            """
            components.html(note_html, height=400)  # Increased height to accommodate more content
        
        # Clinical considerations for HER2+ breast cancer
        if condition_type == "her2":
            st.markdown("""
            <div style="margin-top: 1rem; padding: 0.75rem; background-color: #fef9c3; border-left: 4px solid #facc15; border-radius: 0 0.25rem 0.25rem 0; display: flex;">
                <span style="color: #ca8a04; margin-right: 0.5rem; font-size: 1.25rem;">⚠️</span>
                <div style="font-size: 0.875rem;">
                    <p style="font-weight: 500; color: #854d0e; margin-bottom: 0.25rem;">Important Clinical Considerations</p>
                    <ul style="color: #854d0e; margin: 0.25rem 0 0 1.25rem; padding: 0;">
                        <li>Cardiac monitoring is critical - baseline and q3month LVEF assessment</li>
                        <li>Consider dose reduction for paclitaxel in patients with pre-existing neuropathy</li>
                        <li>Primary G-CSF prophylaxis required due to dose-density of regimen</li>
                        <li>Pertuzumab contraindicated if LVEF &lt;50% or pregnancy</li>
                    </ul>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Guideline references
    st.markdown("""
    <h4 style="font-size: 0.875rem; font-weight: 500; color: #475569; margin-top: 1rem; margin-bottom: 0.5rem;">Guideline References</h4>
    """, unsafe_allow_html=True)
    
    if condition_type == "her2":
        st.markdown("""
        <div class="guideline-reference">
            <p style="font-weight: 500; font-size: 0.75rem;">NCCN Guidelines Version 1.2024, Breast Cancer (BINV-L)</p>
            <p style="color: #475569; font-size: 0.75rem; margin-top: 0.25rem;">
                "Preferred neoadjuvant regimens for HER2-positive disease include: Doxorubicin/cyclophosphamide (AC) followed by paclitaxel + trastuzumab ± pertuzumab. The addition of pertuzumab to trastuzumab-based regimens has been shown to increase the rate of pCR in neoadjuvant studies."
            </p>
        </div>
        
        <div class="guideline-reference" style="background-color: #eff6ff; border-left: 4px solid #60a5fa;">
            <p style="font-weight: 500; font-size: 0.75rem;">ASCO Clinical Practice Guideline Update (2018)</p>
            <p style="color: #475569; font-size: 0.75rem; margin-top: 0.25rem;">
                "For patients with advanced HER2-positive breast cancer treated with first-line trastuzumab, pertuzumab, and taxane for 4 to 6 months to maximal response or until limiting toxicity, and whose disease is not progressing at the completion of taxane-based therapy: Clinicians should continue HER2-targeted therapy until time of disease progression or limiting toxicity."
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Evidence section for HER2+
        st.markdown("""
        <h4 style="font-size: 0.875rem; font-weight: 500; color: #475569; margin-top: 1rem; margin-bottom: 0.5rem;">Key Supporting Evidence</h4>
        
        <div style="padding: 0.5rem; border: 1px solid #e2e8f0; border-radius: 0.375rem; margin-bottom: 0.5rem; font-size: 0.75rem;">
            <p style="font-weight: 500;">NEOSPHERE Trial (Lancet Oncol. 2012)</p>
            <p style="color: #475569; margin-top: 0.25rem;">
                Dual HER2 blockade with trastuzumab + pertuzumab improved pCR rate to 45.8% vs 29.0% with trastuzumab alone when combined with docetaxel in the neoadjuvant setting.
            </p>
        </div>
        
        <div style="padding: 0.5rem; border: 1px solid #e2e8f0; border-radius: 0.375rem; font-size: 0.75rem;">
            <p style="font-weight: 500;">BERENICE Trial (Ann Oncol. 2018)</p>
            <p style="color: #475569; margin-top: 0.25rem;">
                Demonstrated the cardiac safety of dose-dense AC followed by weekly paclitaxel with dual HER2 blockade in the neoadjuvant setting. Pathologic complete response was achieved in 61.8% of patients.
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="guideline-reference" style="background-color: #fef9c3; border-left: 4px solid #facc15;">
            <p style="font-weight: 500; font-size: 0.75rem;">ADA Standards of Medical Care in Diabetes—2024, p.42</p>
            <p style="color: #475569; font-size: 0.75rem; margin-top: 0.25rem;">
                "For patients with Type 2 diabetes with HbA1c levels > 8.0%, clinicians should consider intensifying pharmacologic therapy, adding additional agents, or referral to a specialist. (Grade A)"
            </p>
        </div>
        
        <div class="guideline-reference" style="background-color: #eff6ff; border-left: 4px solid #60a5fa;">
            <p style="font-weight: 500; font-size: 0.75rem;">JNC 8 Guidelines for Hypertension, p.18</p>
            <p style="color: #475569; font-size: 0.75rem; margin-top: 0.25rem;">
                "In the general nonblack population, including those with diabetes, initial antihypertensive treatment should include a thiazide-type diuretic, calcium channel blocker (CCB), angiotensin-converting enzyme inhibitor (ACEI), or angiotensin receptor blocker (ARB)."
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Footer
    st.markdown(f"""
    <div style="padding: 0.75rem; border-top: 1px solid #e2e8f0; background-color: #f8fafc; display: flex; justify-content: space-between; align-items: center; margin-top: 1rem;">
        <div style="display: flex; align-items: center; gap: 0.5rem;">
            <button style="border: none; background: none; color: #64748b; cursor: pointer;">
                <span>👍</span>
            </button>
            <button style="border: none; background: none; color: #64748b; cursor: pointer;">
                <span>🔖</span>
            </button>
            <button style="border: none; background: none; color: #64748b; cursor: pointer;">
                <span>💾</span>
            </button>
        </div>
        <div style="font-size: 0.75rem; color: #64748b;">
            Generated using Claude 3 Sonnet
        </div>
        <button style="border: none; background: none; color: {theme_color}; font-size: 0.75rem; display: flex; align-items: center; cursor: pointer;">
            <span style="margin-right: 0.25rem;">View Full Guidelines</span>
            <span>→</span>
        </button>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

def get_patient_labs_string(patient):
    labs = patient.get('recentLabs', {})
    labs_strings = []
    for key, value in labs.items():
        labs_strings.append(f"{key}: {value}")
    return ", ".join(labs_strings)