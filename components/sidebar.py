# =====================================
# components/sidebar.py
# =====================================
import streamlit as st
from data.sample_data import get_sample_guidelines, get_sample_uploaded_docs

def render_sidebar():
    with st.sidebar:
        st.markdown("<h1 style='text-align: center; color: #1e40af;'>MedGuide</h1>", unsafe_allow_html=True)
        
        # Navigation
        st.markdown("### Navigation")
        if st.button("📚 Guidelines Home", use_container_width=True):
            st.session_state.current_page = 'home'
            st.session_state.selected_guideline = None
            st.rerun()
            
        if st.button("💬 Ask Clinical Questions", use_container_width=True):
            st.session_state.current_page = 'prompts'
            st.rerun()
        
        # Note Generator with Custom Condition
        st.markdown("### Generate Note")
        
        # Custom condition input - make this a dropdown to avoid typos
        condition_options = ["Breast Cancer", "Diabetes", "Hypertension", "Cardiovascular Disease"]
        condition = st.selectbox("Select medical condition", condition_options, index=0)
        
        # Sample conditions suggestions
        st.caption("Or enter a custom condition")
        custom_condition = st.text_input("Custom condition (optional)")
        
        # Use custom condition if provided, otherwise use the selected one
        final_condition = custom_condition if custom_condition else condition
        
        # Generate note button
        if st.button("📝 Generate Note", use_container_width=True):
            if final_condition:
                # Store condition in session state (lowercase for consistent processing)
                st.session_state.selected_condition = final_condition.lower()
                
                # Ensure a patient exists in session state
                if 'current_patient' not in st.session_state or not st.session_state.current_patient:
                    st.error("No patient data available. Please refresh the patient data.")
                    return
                
                st.session_state.current_page = 'note'
                st.rerun()
            else:
                st.error("Please select or enter a medical condition")
        
        st.markdown("<hr>", unsafe_allow_html=True)
        
        # Guidelines tabs
        tab1, tab2, tab3 = st.tabs(["Curated", "Uploaded", "Search"])
        
        with tab1:
            st.markdown("#### Curated Guidelines")
            guidelines = get_sample_guidelines()
            
            for guideline in guidelines:
                guideline_container = st.container()
                with guideline_container:
                    if st.button(f"{guideline['title']}", key=f"guideline_{guideline['id']}", use_container_width=True):
                        st.session_state.selected_guideline = guideline
                        
                        # If it's a condition-specific guideline, also set the condition
                        if "diabetes" in guideline['title'].lower():
                            st.session_state.selected_condition = "diabetes"
                        elif "hypertension" in guideline['title'].lower():
                            st.session_state.selected_condition = "hypertension"
                        elif "breast cancer" in guideline['title'].lower():
                            st.session_state.selected_condition = "breast cancer"
                        elif "cardiovascular" in guideline['title'].lower() or "lipid" in guideline['title'].lower():
                            st.session_state.selected_condition = "cardiovascular disease"
                            
                        st.session_state.current_page = 'home'
                        st.rerun()
                    st.caption(f"{guideline['source']} • Updated {guideline['lastUpdated']}")
                st.markdown("<hr>", unsafe_allow_html=True)
        
        with tab2:
            st.markdown("#### Uploaded Documents")
            
            # Upload new document
            uploaded_file = st.file_uploader("Upload a guideline PDF", type="pdf")
            if uploaded_file:
                st.success("File uploaded successfully!")
                # In a real app, process and store the file
            
            # Existing uploaded docs
            uploaded_docs = get_sample_uploaded_docs()
            for doc in uploaded_docs:
                doc_container = st.container()
                with doc_container:
                    if st.button(f"{doc['title']}", key=f"doc_{doc['id']}", use_container_width=True):
                        st.session_state.selected_guideline = doc
                        
                        # Set condition if document title contains condition keywords
                        if "diabetes" in doc['title'].lower():
                            st.session_state.selected_condition = "diabetes"
                        elif "hypertension" in doc['title'].lower():
                            st.session_state.selected_condition = "hypertension"
                        elif "breast cancer" in doc['title'].lower() or "mammography" in doc['title'].lower():
                            st.session_state.selected_condition = "breast cancer"
                        elif "cardiovascular" in doc['title'].lower() or "lipid" in doc['title'].lower():
                            st.session_state.selected_condition = "cardiovascular disease"
                            
                        st.session_state.current_page = 'home'
                        st.rerun()
                    st.caption(f"Uploaded by {doc['uploadedBy']} • {doc['uploadDate']}")
                st.markdown("<hr>", unsafe_allow_html=True)
        
        with tab3:
            st.markdown("#### Search Medical Guidelines")
            
            search_query = st.text_input("Search guidelines", placeholder="Enter search terms...")
            if st.button("Search", use_container_width=True):
                if search_query:
                    st.session_state.search_results = [
                        {
                            "title": "Search Results for Medical Guidelines",
                            "snippet": f"Results for: {search_query}",
                            "url": "#",
                            "source": "Search Engine"
                        }
                    ]
                    
                    # Try to infer condition from search query
                    if "diabetes" in search_query.lower():
                        st.session_state.selected_condition = "diabetes"
                    elif "hypertension" in search_query.lower() or "blood pressure" in search_query.lower():
                        st.session_state.selected_condition = "hypertension"
                    elif "breast" in search_query.lower() and "cancer" in search_query.lower():
                        st.session_state.selected_condition = "breast cancer"
                    elif "heart" in search_query.lower() or "cardiovascular" in search_query.lower():
                        st.session_state.selected_condition = "cardiovascular disease"
            
            # Recent searches
            st.markdown("#### Recent Searches")
            recent_searches = [
                "breast cancer treatment options",
                "hypertension treatment in patients with diabetes",
                "statin recommendations for diabetic patients"
            ]
            
            for search in recent_searches:
                if st.button(f"🕒 {search}", key=f"search_{search}", use_container_width=True):
                    # Set condition based on search content
                    if "diabetes" in search.lower():
                        st.session_state.selected_condition = "diabetes"
                    elif "hypertension" in search.lower() or "blood pressure" in search.lower():
                        st.session_state.selected_condition = "hypertension"
                    elif "breast" in search.lower() and "cancer" in search.lower():
                        st.session_state.selected_condition = "breast cancer"
                    elif "heart" in search.lower() or "cardiovascular" in search.lower() or "statin" in search.lower():
                        st.session_state.selected_condition = "cardiovascular disease"
        
        # Settings and help
        st.markdown("<hr>", unsafe_allow_html=True)
        
        with st.expander("Settings"):
            st.markdown("### API Configuration")
            claude_api_key = st.text_input("Claude API Key", 
                                          value=st.session_state.get('claude_api_key', ''), 
                                          type="password",
                                          placeholder="Enter Claude API key")
            
            perplexity_api_key = st.text_input("Perplexity API Key", 
                                              value=st.session_state.get('perplexity_api_key', ''), 
                                              type="password",
                                              placeholder="Enter Perplexity API key")
            
            if st.button("Save API Keys"):
                st.session_state.claude_api_key = claude_api_key
                st.session_state.perplexity_api_key = perplexity_api_key
                st.success("API keys saved successfully!")
        
        with st.expander("Help"):
            st.markdown("""
            ### Using MedGuide
            
            - **Guidelines Home**: Browse and view medical guidelines
            - **Ask Clinical Questions**: Chat with AI about patient-specific recommendations
            - **Generate Note**: Create clinical notes for documentation
            
            For more help, please contact support@medguide.example.com
            """)