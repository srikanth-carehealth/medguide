# =====================================
# utils/claude_api.py
# =====================================
import requests
import json
import os
from typing import Dict, List, Any, Optional, Union
import time

class ClaudeAPI:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("CLAUDE_API_KEY", "demo_key")
        self.base_url = "https://api.anthropic.com/v1"
        self.headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01"
        }
        self.model = "claude-3-sonnet-20240229"  # Add this line
        self.max_tokens = 2048  # Add this line
        self.temperature = 0.7  # Add this line
    
    def _build_headers(self) -> Dict[str, str]:
            """Build the request headers for Anthropic API."""
            return {
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            }
    
    def query_guidelines(
        self, 
        query: str, 
        patient_context: Dict[str, Any], 
        condition: str = "general",
        document_ids: List[str] = None,
        document_text: str = None
    ) -> Dict[str, Any]:
        """
        Query Claude about medical guidelines with patient context.
        
        Args:
            query: The specific question or request
            patient_context: Patient data dictionary
            condition: The medical condition context (e.g., "diabetes", "breast cancer")
            document_ids: Optional list of guideline document IDs 
            document_text: Optional full text of the document
            
        Returns:
            Dictionary with recommendations and explanations
        """
        # If we're in demo mode, return mock data
        if self.api_key == 'demo_key':
            return self._get_mock_response(query, patient_context, condition)
        
        # Format patient context for prompt
        patient_info = self._format_patient_context(patient_context)
        
        # Build system prompt with condition context
        system_prompt = f"""You are a medical AI assistant helping a healthcare provider understand guidelines and make treatment decisions.
        
Your task is to analyze medical guidelines and provide accurate, clinically relevant information that is personalized to the specific patient.

The primary condition being discussed is: {condition}

When answering questions:
1. Only use information explicitly stated in the guidelines.
2. Cite specific sections, recommendations, and page numbers when possible.
3. Be objective and factual about medical information.
4. Consider the patient's unique clinical characteristics in your recommendations.
5. When making recommendations, explain your reasoning clearly.
6. Be respectful of the provider's expertise while being helpful.
7. If information isn't in the guidelines, admit this rather than speculate.

PATIENT CONTEXT:
{patient_info}

Guidelines should be interpreted in light of this specific patient's clinical context and the primary condition: {condition}."""
        
        # Build main prompt
        if document_text:
            main_prompt = f"""I have a question about {condition} based on the following medical guideline:

{document_text[:50000]}  # Limit document text to avoid token limits

My question is: {query}

Please analyze this guideline in the context of my patient and answer my question, focusing on {condition}."""
        elif document_ids:
            # In a real app, you would fetch document content based on IDs
            main_prompt = f"""I'm reviewing guidelines with IDs: {', '.join(document_ids)} related to {condition}

My question is: {query}

Please provide relevant recommendations from these guidelines for my patient with {condition}."""
        else:
            main_prompt = f"""With regard to {condition}, {query}"""
        
        # Call Anthropic API
        try:
            response = requests.post(
                f"{self.base_url}/messages",
                headers=self._build_headers(),
                json={
                    "model": self.model,
                    "max_tokens": self.max_tokens,
                    "temperature": self.temperature,
                    "system": system_prompt,
                    "messages": [
                        {"role": "user", "content": main_prompt}
                    ]
                }
            )
            
            response.raise_for_status()
            result = response.json()
            
            # Parse Claude's response into a structured format
            return self._parse_claude_response(result["content"][0]["text"], query)
            
        except Exception as e:
            print(f"Error calling Claude API: {e}")
            # Return a fallback response in case of API error
            return {
                "recommendations": [
                    {
                        "text": "Unable to retrieve recommendations at this time.",
                        "explanation": f"There was an error communicating with Claude: {str(e)}",
                        "source": "Error",
                        "page": "N/A"
                    }
                ]
            }
    
    def _format_patient_context(self, patient: Dict[str, Any]) -> str:
        """Format patient data in a readable way for the prompt."""
        patient_str = f"""
Name: {patient.get('name', 'Unknown')}
Age: {patient.get('age', 'Unknown')}
Gender: {patient.get('gender', 'Unknown')}
"""
        
        # Add diagnosis if available
        if patient.get('diagnosis'):
            patient_str += f"Diagnosis: {patient.get('diagnosis')}\n"
        
        # Add vital signs if available
        vitals = patient.get('vitals', {})
        if vitals:
            patient_str += f"""
Vital Signs:
- Blood Pressure: {vitals.get('bloodPressure', 'Not recorded')}
- Heart Rate: {vitals.get('heartRate', 'Not recorded')} bpm
- Height: {vitals.get('height', 'Not recorded')}
- Weight: {vitals.get('weight', 'Not recorded')} kg
- BMI: {vitals.get('bmi', 'Not recorded')} kg/m²
"""

        # Add lab values if available
        labs = patient.get('recentLabs', {}) or patient.get('labs', {})
        if labs:
            patient_str += "\nLab Values:\n"
            for lab, value in labs.items():
                patient_str += f"- {lab}: {value}\n"
        
        # Add conditions if available
        conditions = patient.get('conditions', [])
        if conditions:
            patient_str += "\nMedical Conditions:\n"
            for condition in conditions:
                patient_str += f"- {condition}\n"
        
        # Add medications if available
        medications = patient.get('medications', [])
        if medications:
            patient_str += "\nCurrent Medications:\n"
            for med in medications:
                patient_str += f"- {med}\n"
                
        return patient_str
    
    def _parse_claude_response(self, response_text: str, query: str) -> Dict[str, List[Dict[str, str]]]:
        """
        Parse Claude's response into a structured format with recommendations.
        
        This implementation uses a heuristic approach to extract recommendations
        from Claude's free-text response.
        """
        # For complex parsing, you might want to use a better prompt structure
        # or have Claude return a more structured response format like JSON
        
        recommendations = []
        
        # Split the response into paragraphs
        paragraphs = response_text.split('\n\n')
        
        # Identify recommendations in the text
        for i, paragraph in enumerate(paragraphs):
            if len(paragraph.strip()) < 10:  # Skip short paragraphs
                continue
                
            # Look for quoted text as recommendations
            if '"' in paragraph:
                # Try to extract quotes
                parts = paragraph.split('"')
                if len(parts) >= 3:  # At least one complete quote
                    for j in range(1, len(parts), 2):
                        if parts[j].strip():
                            # Found a recommendation inside quotes
                            explanation = parts[j-1].strip() if j-1 >= 0 else ""
                            
                            # Look for source/page in the text
                            source_match = None
                            page_match = None
                            
                            # Simple regex-free search for page and source indicators
                            lower_text = paragraph.lower()
                            if "page" in lower_text:
                                # Extract page number - simplified approach
                                for word in lower_text.split():
                                    if word.startswith("page"):
                                        page_match = word.split("page")[1].strip(".,: ")
                                        break
                            
                            # Look for common guideline sources
                            if "ada" in lower_text:
                                source_match = "ADA Standards of Medical Care in Diabetes"
                            elif "jnc" in lower_text:
                                source_match = "JNC Guidelines"
                            elif "nccn" in lower_text:
                                source_match = "NCCN Guidelines for Breast Cancer"
                            elif "asco" in lower_text:
                                source_match = "ASCO Guidelines"
                            elif "breast" in lower_text and "cancer" in lower_text:
                                source_match = "Breast Cancer Treatment Guidelines"
                            else:
                                source_match = "Clinical Guidelines"
                            
                            # Create recommendation object
                            recommendations.append({
                                "text": parts[j].strip(),
                                "explanation": explanation if explanation else paragraph,
                                "source": source_match if source_match else "Medical Guidelines",
                                "page": page_match if page_match else "N/A"
                            })
            
            # If no quotes found but paragraph looks like a recommendation
            elif any(keyword in paragraph.lower() for keyword in ["recommend", "should", "advised", "indicated"]):
                recommendations.append({
                    "text": paragraph,
                    "explanation": "Based on your patient's clinical profile",
                    "source": "Clinical Guidelines",
                    "page": "N/A"
                })
        
        # If no recommendations found, treat the entire response as one
        if not recommendations:
            recommendations.append({
                "text": response_text.strip(),
                "explanation": f"Response to query: {query}",
                "source": "Medical Guidelines",
                "page": "N/A"
            })
        
        return {"recommendations": recommendations}
    
    def generate_clinical_note(
        self, 
        patient_data: Dict[str, Any], 
        condition: str
    ) -> Dict[str, Any]:
        """
        Generate a clinical note for the specified patient and condition
        """
        # For demo purposes, return mock data if using demo key
        if self.api_key == "demo_key":
            return self._get_mock_note_response(condition, patient_data)
                
        # Prepare prompt
        prompt = f"""
        Generate a succinct assessment and plan for a clinical note based on the following:

        Patient Context:
        {json.dumps(patient_data, indent=2)}

        Condition: {condition}

        Requirements:
        1. Create a structured assessment summarizing patient's current status
        2. Provide a plan organized by problem
        3. Include specific guideline references with page numbers
        4. Keep it concise and formatted for direct inclusion in EHR
        
        Format the note with clear sections for ASSESSMENT and PLAN.
        The note should be ready to copy and paste into an EHR system.
        """
        
        # Make API call to Claude
        try:
            response = requests.post(
                f"{self.base_url}/messages",
                headers=self.headers,
                json={
                    "model": "claude-3-sonnet-20240229",
                    "max_tokens": 2048,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                },
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            
            # Extract content
            content = result["content"][0]["text"]
            
            return {
                "title": f"Assessment & Plan for {condition.upper()}",
                "content": content.strip()
            }
                
        except requests.RequestException as e:
            print(f"API request error: {e}")
            return {
                "title": "Error Generating Note",
                "content": "Unable to generate a clinical note at this time."
            }


    def _get_mock_note_response(self, condition: str, patient_data: Dict[str, Any]) -> Dict[str, Any]:
            """Generate mock clinical note for demonstration purposes"""
            time.sleep(1.5)  # Simulate API delay
            
            # Check for known condition types
            if "diabetes" in condition.lower():
                content = f"""ASSESSMENT:
        {patient_data.get('age', 54)}yo {patient_data.get('gender', 'male')} with poorly-controlled Type 2 Diabetes (A1c {patient_data.get('recentLabs', {}).get('HbA1c', '8.2%')}) and Hypertension (BP {patient_data.get('recentLabs', {}).get('BP', '142/88')}), with elevated LDL ({patient_data.get('recentLabs', {}).get('LDL', '138mg/dL')}).

        PLAN:
        1. Diabetes Management:
        - Intensify glycemic control (HbA1c > 8.0% requires therapy adjustment per ADA 2024 Guidelines, p.42)
        - Consider adding second-line agent or adjusting current medication dose
        - Reinforce dietary modifications and physical activity
        - Schedule follow-up A1c check in 3 months

        2. Hypertension Management:
        - Target BP < 140/90 mmHg per JNC 8 Guidelines for diabetic patients
        - Continue current antihypertensive; reassess in 4 weeks
        - Encourage sodium restriction and DASH diet

        3. Lipid Management:
        - Initiate moderate-intensity statin therapy (LDL > 130mg/dL with diabetes indicates statin benefit per AHA/ACC Guidelines)
        - Baseline liver function tests prior to starting

        4. Monitoring:
        - Renal function panel and urine microalbumin
        - Comprehensive foot exam
        - Schedule eye examination if not done within past year"""
                
            elif "her2" in condition.lower() or "breast cancer" in condition.lower():
                content = f"""ASSESSMENT:
        {patient_data.get('age', 47)}yo {patient_data.get('gender', 'female')} with newly diagnosed left breast invasive ductal carcinoma, {patient_data.get('stage', 'cT2N1M0 stage IIB')}, ER {patient_data.get('receptorStatus', {}).get('ER', '15%')}, PR {patient_data.get('receptorStatus', {}).get('PR', '5%')}, HER2 {patient_data.get('receptorStatus', {}).get('HER2', '3+ by IHC (confirmed by FISH with HER2/CEP17 ratio 5.2)')}.

        PLAN:
        1. Neoadjuvant Systemic Therapy:
        - Dose-dense AC-T regimen with dual HER2-targeted therapy per NCCN Guidelines v.1.2024 (BINV-L)
        - Regimen details:
            * Dose-dense AC: Doxorubicin 60 mg/m² IV + Cyclophosphamide 600 mg/m² IV q2wks × 4 cycles
            * Followed by: Paclitaxel 80 mg/m² IV weekly × 12 weeks
            * With: Trastuzumab 4 mg/kg IV loading dose, then 2 mg/kg IV weekly
            * And: Pertuzumab 840 mg IV loading dose, then 420 mg IV q3wks

        2. Supportive Care:
        - Pegfilgrastim 6 mg SC on day 2 of each AC cycle
        - Antiemetic protocol with AC: Olanzapine 10 mg PO day 1-3, Aprepitant 125 mg PO day 1 then 80 mg days 2-3, Dexamethasone 12 mg IV day 1, Ondansetron 16 mg PO day 1
        - Cardiac monitoring: LVEF assessment at baseline, after AC completion, and q3mo during HER2-targeted therapy (baseline LVEF 62%)
        - Infusion reaction prophylaxis per institutional protocol

        3. Monitoring:
        - CBC with diff, CMP prior to each AC cycle and weekly during paclitaxel
        - Clinical tumor assessment prior to each cycle
        - Cardiac monitoring with MUGA scan or echocardiogram at baseline and q3mo
        - Post-treatment imaging with MRI breast to assess response prior to surgery

        4. Follow-up:
        - Weekly visits during AC with medical oncology
        - Surgical consultation after cycle 2 of AC to plan for post-neoadjuvant surgery
        - Genetic counseling referral (appointment pending)
        - Consider enrollment in clinical trial NSABP B-60 (pending eligibility screening)"""
                
            elif "hypertension" in condition.lower() or "blood pressure" in condition.lower():
                content = f"""ASSESSMENT:
        {patient_data.get('age', 60)}yo {patient_data.get('gender', 'male')} with Hypertension (BP {patient_data.get('recentLabs', {}).get('BP', '152/94')}). Patient has been on lisinopril 10mg daily with suboptimal control.

        PLAN:
        1. Hypertension Management:
        - Increase lisinopril to 20mg daily
        - Target BP < 130/80 mmHg per 2017 ACC/AHA Guidelines
        - Sodium restriction (<2.3g daily) and DASH diet
        - Regular aerobic exercise 150 minutes per week

        2. Lifestyle Modifications:
        - Weight loss goal of 5-10% of body weight
        - Limit alcohol consumption to ≤2 drinks per day for men, ≤1 drink per day for women
        - Smoking cessation counseling and resources

        3. Monitoring:
        - Home BP monitoring twice daily for 2 weeks
        - Follow-up appointment in 4 weeks for BP check
        - Basic metabolic panel to assess renal function and electrolytes

        4. Patient Education:
        - Provide educational materials on low-sodium diet
        - Review medication adherence strategies
        - Discuss symptoms that require immediate attention"""
                
            elif "lipid" in condition.lower() or "cholesterol" in condition.lower():
                content = f"""ASSESSMENT:
        {patient_data.get('age', 58)}yo {patient_data.get('gender', 'female')} with Hyperlipidemia (LDL {patient_data.get('recentLabs', {}).get('LDL', '162mg/dL')}, HDL {patient_data.get('recentLabs', {}).get('HDL', '42mg/dL')}, TG {patient_data.get('recentLabs', {}).get('TG', '190mg/dL')}). 10-year ASCVD risk calculated at 12.4%.

        PLAN:
        1. Lipid Management:
        - Initiate moderate-intensity statin therapy: Atorvastatin 20mg daily
        - Target LDL reduction of ≥30% per 2018 AHA/ACC Guidelines
        - Consider addition of ezetimibe if inadequate response to statin

        2. Lifestyle Modifications:
        - Mediterranean diet pattern with increased plant sterols/stanols
        - Regular aerobic exercise 150 minutes per week
        - Weight loss goal of 5-10% of body weight if BMI >25

        3. Monitoring:
        - Lipid panel in 4-12 weeks after starting statin therapy
        - Liver function tests at baseline and as clinically indicated
        - Assess for muscle symptoms at follow-up visits

        4. Patient Education:
        - Discuss potential statin side effects and management
        - Provide dietary resources for cholesterol management
        - Review importance of medication adherence"""
            
            else:
                # Generic template for any other condition
                content = f"""ASSESSMENT:
        {patient_data.get('age', 50)}yo {patient_data.get('gender', 'patient')} with {condition}. 

        PLAN:
        1. Condition Management:
        - Comprehensive evaluation of {condition}
        - Consideration of evidence-based treatment options
        - Patient education regarding condition management

        2. Monitoring:
        - Regular follow-up to assess treatment response
        - Laboratory monitoring as appropriate for condition
        - Assessment of potential complications

        3. Additional Considerations:
        - Lifestyle modifications appropriate for condition
        - Review of medication regimen for interactions
        - Referral to specialists if indicated

        4. Follow-up:
        - Schedule follow-up appointment in 4-6 weeks
        - Provide patient with relevant educational materials
        - Consider support resources for patient"""
                
            return {
                "title": f"Assessment & Plan for {condition.title()}",
                "content": content
            }
    
    def _get_mock_response(self, query: str, patient_context: Dict[str, Any], condition: str = "general") -> Dict[str, List[Dict[str, str]]]:
        """Return mock data for demo purposes based on the condition specified."""
        # Create dynamic mock responses based on query and condition
        time.sleep(0.5)  # Simulate API delay
        
        # Convert condition to lowercase for easier matching
        condition = condition.lower() if condition else "general"
        
        # BREAST CANCER specific responses
        if "breast cancer" in condition:
            # Breast cancer treatment
            if "treatment" in query.lower() or "options" in query.lower():
                return {
                    "recommendations": [
                        {
                            "explanation": "Based on the patient's breast cancer diagnosis, here are the standard treatment options:",
                            "text": "Treatment options for breast cancer include surgery (lumpectomy or mastectomy), radiation therapy, chemotherapy, hormone therapy, and targeted therapy. The specific treatment plan depends on the cancer stage, tumor characteristics, and patient factors.",
                            "source": "NCCN Guidelines for Breast Cancer",
                            "page": "42"
                        }
                    ]
                }
            # Breast cancer screening
            elif "screening" in query.lower():
                return {
                    "recommendations": [
                        {
                            "explanation": "Current breast cancer screening guidelines recommend:",
                            "text": "Women at average risk of breast cancer should be offered screening mammography starting at age 40. The decision to start screening mammography before age 50 should be individualized and take patient context into account.",
                            "source": "American Cancer Society Guidelines",
                            "page": "18"
                        }
                    ]
                }
            # Breast cancer follow-up
            elif "follow-up" in query.lower() or "monitoring" in query.lower():
                return {
                    "recommendations": [
                        {
                            "explanation": "For patients with a history of breast cancer, follow-up protocols include:",
                            "text": "Follow-up after primary breast cancer treatment should include history/physical examination every 4-6 months for 5 years, then annually; mammography annually; and breast awareness education.",
                            "source": "ASCO Guidelines",
                            "page": "27"
                        }
                    ]
                }
            # Genetic testing for breast cancer
            elif "genetic" in query.lower() or "testing" in query.lower():
                return {
                    "recommendations": [
                        {
                            "explanation": "Regarding genetic testing for breast cancer patients:",
                            "text": "Genetic testing should be offered to patients with a personal history of breast cancer and one or more of the following: diagnosed at age ≤45, triple-negative breast cancer at age ≤60, or a significant family history of breast, ovarian, pancreatic, or prostate cancer.",
                            "source": "NCCN Genetic/Familial High-Risk Assessment Guidelines",
                            "page": "35"
                        }
                    ]
                }
            # Default breast cancer response
            else:
                return {
                    "recommendations": [
                        {
                            "explanation": "General approach to breast cancer management:",
                            "text": "Breast cancer treatment should be individualized based on tumor characteristics, disease stage, and patient preferences. A multidisciplinary approach involving surgical oncology, medical oncology, radiation oncology, pathology, and radiology is recommended.",
                            "source": "NCCN Clinical Practice Guidelines in Oncology: Breast Cancer",
                            "page": "12"
                        }
                    ]
                }
                
        # DIABETES specific responses
        elif "diabetes" in condition:
            if "medication" in query.lower() or "regimen" in query.lower():
                return {
                    "recommendations": [
                        {
                            "explanation": "The patient's current BP is 142/88, which is above the recommended target for patients with diabetes.",
                            "text": "Target BP should be <140/90 mmHg for most patients with diabetes and hypertension.",
                            "source": "JNC 8 Guidelines",
                            "page": "18"
                        },
                        {
                            "explanation": "The patient's HbA1c is 8.2%, which is above the recommended target.",
                            "text": "For patients with Type 2 diabetes with HbA1c levels > 8.0%, clinicians should consider intensifying pharmacologic therapy, adding additional agents, or referral to a specialist.",
                            "source": "ADA Standards of Medical Care in Diabetes - 2024",
                            "page": "42"
                        }
                    ]
                }
            elif "hba1c" in query.lower() or "glucose" in query.lower():
                return {
                    "recommendations": [
                        {
                            "explanation": "This patient has an HbA1c of 8.2%, indicating suboptimal glycemic control.",
                            "text": "For patients with Type 2 diabetes with HbA1c levels > 8.0%, clinicians should consider intensifying pharmacologic therapy, adding additional agents, or referral to a specialist.",
                            "source": "ADA Standards of Medical Care in Diabetes - 2024",
                            "page": "42"
                        },
                        {
                            "explanation": "Given the elevated HbA1c, more frequent monitoring is recommended.",
                            "text": "When glycemic targets are not being met, quarterly assessments using HbA1c testing are recommended.",
                            "source": "ADA Standards of Medical Care in Diabetes - 2024",
                            "page": "44"
                        }
                    ]
                }
            else:
                return {
                    "recommendations": [
                        {
                            "explanation": "Based on the patient's clinical profile with Type 2 diabetes and hypertension.",
                            "text": "Regular comprehensive diabetes care visits are recommended, including medication review, screen for complications, and reinforcement of self-management behaviors.",
                            "source": "ADA Standards of Medical Care in Diabetes - 2024",
                            "page": "35"
                        }
                    ]
                }
                
        # HYPERTENSION specific responses
        elif "hypertension" in condition or "blood pressure" in query.lower():
            return {
                "recommendations": [
                    {
                        "explanation": "The patient's current BP is 142/88, which is above the recommended target.",
                        "text": "Target BP should be <140/90 mmHg for most patients with diabetes and hypertension.",
                        "source": "JNC 8 Guidelines",
                        "page": "18"
                    }
                ]
            }
            
        # Generic fallback for other conditions
        else:
            if "assessment" in query.lower() and "plan" in query.lower() and "note" in query.lower():
                return {
                    "recommendations": [
                        {
                            "explanation": "Here's a template for the assessment and plan note.",
                            "text": f"For patients with {condition}, include specific treatment targets and monitoring recommendations in the plan.",
                            "source": "Best Practice Guidelines",
                            "page": "5"
                        }
                    ]
                }
            else:
                # Generic fallback response
                return {
                    "recommendations": [
                        {
                            "explanation": f"Based on the patient's clinical profile with {condition}.",
                            "text": f"Regular comprehensive care visits are recommended for patients with {condition}, including medication review, monitoring for complications, and reinforcement of self-management behaviors.",
                            "source": "Clinical Practice Guidelines",
                            "page": "35"
                        }
                    ]
                }