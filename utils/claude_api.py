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
    
    def query_guidelines(
        self, 
        query: str, 
        patient_context: Dict[str, Any], 
        document_text: Optional[str] = None,
        document_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Query the Claude API for guideline recommendations based on patient context
        """
        # For demo purposes, return mock data if using demo key
        if self.api_key == "demo_key":
            return self._get_mock_guideline_response(query, patient_context)
        
        # Prepare prompt with document content if available
        prompt = f"""
        Patient Context:
        {json.dumps(patient_context, indent=2)}
        
        Query: {query}
        """
        
        if document_text:
            prompt += f"\n\nDocument Text:\n{document_text}\n"
            
        prompt += """
        Please identify specific guideline recommendations relevant to this patient.
        Return the response in JSON format with page numbers and exact text excerpts.
        Format your response as a JSON object with the following structure:
        {
            "recommendations": [
                {
                    "text": "The relevant recommendation text",
                    "explanation": "Why this is relevant for this patient",
                    "page": 42,
                    "source": "ADA Guidelines 2024",
                    "confidence": 0.95
                }
            ]
        }
        """
        
        # Make API call to Claude
        try:
            response = requests.post(
                f"{self.base_url}/messages",
                headers=self.headers,
                json={
                    "model": "claude-3-5-sonnet-20241022",
                    "max_tokens": 4096,
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
            
            # Extract and parse JSON from the response
            try:
                content = result["content"][0]["text"]
                # Find JSON content within the response
                json_start = content.find('{')
                json_end = content.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    json_str = content[json_start:json_end]
                    return json.loads(json_str)
                else:
                    # Fallback if structured JSON not found
                    return {"recommendations": [{"text": content, "page": None, "source": None, "confidence": 0.7}]}
            except (KeyError, json.JSONDecodeError):
                return {"recommendations": [{"text": "Unable to parse response", "page": None, "source": None, "confidence": 0}]}
                
        except requests.RequestException as e:
            print(f"API request error: {e}")
            return {"recommendations": []}
    
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
                    "model": "claude-3-5-sonnet-20241022",
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
    
    def process_pdf(self, pdf_content: bytes) -> Dict[str, Any]:
        """
        Process PDF content using Claude's vision capabilities
        """
        # For demo purposes with demo key
        if self.api_key == "demo_key":
            return {
                "title": "Processed PDF",
                "text": "This is a mock processed PDF content for demonstration purposes.",
                "pages": {
                    "1": "Page 1 content would appear here...",
                    "2": "Page 2 content would appear here..."
                },
                "toc": [
                    {"title": "Introduction", "page": 1},
                    {"title": "Recommendations", "page": 2}
                ]
            }
        
        # In a real implementation, this would encode the PDF as base64
        # and send it to Claude's API for analysis
        
        # Placeholder for PDF processing with Claude
        return {
            "title": "Processed PDF",
            "text": "PDF processing would happen here with Claude's vision capabilities",
            "pages": {},
            "toc": []
        }
    
    def _get_mock_guideline_response(self, query: str, patient_context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate mock guideline response for demonstration purposes"""
        time.sleep(1)  # Simulate API delay
        
        if "diabetes" in patient_context.get("diagnosis", "").lower():
            return {
                "recommendations": [
                    {
                        "text": "For patients with Type 2 diabetes with HbA1c levels > 8.0%, clinicians should consider intensifying pharmacologic therapy, adding additional agents, or referral to a specialist.",
                        "explanation": f"The patient's HbA1c is {patient_context.get('recentLabs', {}).get('HbA1c', '8.2%')}, which is above the threshold where guidelines recommend treatment intensification.",
                        "page": 42,
                        "source": "ADA Standards of Medical Care in Diabetes—2024",
                        "confidence": 0.95
                    },
                    {
                        "text": "Target BP should be <140/90 mmHg for most patients with diabetes and hypertension.",
                        "explanation": f"The patient's current BP is {patient_context.get('recentLabs', {}).get('BP', '142/88')}, which is above the recommended target for patients with diabetes.",
                        "page": 18,
                        "source": "JNC 8 Guidelines",
                        "confidence": 0.90
                    }
                ]
            }
        elif "her2" in query.lower() or "breast cancer" in query.lower():
            return {
                "recommendations": [
                    {
                        "text": "Preferred neoadjuvant regimens for HER2-positive disease include: Doxorubicin/cyclophosphamide (AC) followed by paclitaxel + trastuzumab ± pertuzumab.",
                        "explanation": "The patient has HER2-positive breast cancer that would benefit from neoadjuvant therapy with dual HER2 blockade.",
                        "page": 24,
                        "source": "NCCN Guidelines Version 1.2024, Breast Cancer (BINV-L)",
                        "confidence": 0.95
                    }
                ]
            }
        else:
            return {
                "recommendations": [
                    {
                        "text": "Recommendation based on your search would appear here.",
                        "explanation": "This is a placeholder explanation for demo purposes.",
                        "page": 1,
                        "source": "Medical Guidelines",
                        "confidence": 0.7
                    }
                ]
            }
    
    def _get_mock_note_response(self, condition: str, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate mock clinical note for demonstration purposes"""
        time.sleep(1.5)  # Simulate API delay
        
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
            
            return {
                "title": "Assessment & Plan for Diabetes Management",
                "content": content
            }
        
        elif "her2" in condition.lower() or "breast" in condition.lower():
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
            
            return {
                "title": "Assessment & Plan for HER2+ Breast Cancer",
                "content": content
            }
        else:
            return {
                "title": "Assessment & Plan",
                "content": "No specific template available for this condition."
            }