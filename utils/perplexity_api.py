# =====================================
# utils/perplexity_api.py
# =====================================
import requests
import json
import os
from typing import Dict, List, Any, Optional
import time

class PerplexityAPI:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("PERPLEXITY_API_KEY", "demo_key")
        self.base_url = "https://api.perplexity.ai"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
    
    def search_web(
        self, 
        query: str, 
        patient_context: Optional[Dict[str, Any]] = None,
        max_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search the web for relevant medical information using Perplexity
        """
        # For demo purposes, return mock data if using demo key
        if self.api_key == "demo_key":
            return self._get_mock_search_results(query, patient_context)
        
        # Prepare search query, incorporating patient context if available
        search_query = query
        if patient_context:
            diagnosis = patient_context.get("diagnosis", "")
            if diagnosis:
                search_query += f" for patient with {diagnosis}"
        
        # Medical domains to prioritize
        medical_domains = [
            "guidelines.gov", "nih.gov", "cdc.gov", "who.int", 
            "diabetes.org", "heart.org", "medscape.com", "mayoclinic.org",
            "aafp.org", "nejm.org", "jamanetwork.com", "thelancet.com"
        ]
        
        # Make API call to Perplexity
        try:
            response = requests.post(
                f"{self.base_url}/sonar/search",
                headers=self.headers,
                json={
                    "query": search_query,
                    "source_filter": {"domains": medical_domains},
                    "highlight": True,
                    "max_results": max_results
                },
                timeout=30
            )
            response.raise_for_status()
            results = response.json()
            
            # Process and return results
            processed_results = []
            for result in results:
                processed_results.append({
                    "title": result.get("title", ""),
                    "snippet": result.get("snippet", ""),
                    "url": result.get("url", ""),
                    "source": self._extract_domain(result.get("url", ""))
                })
            
            return processed_results
                
        except requests.RequestException as e:
            print(f"API request error: {e}")
            return []
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain name from URL"""
        try:
            from urllib.parse import urlparse
            domain = urlparse(url).netloc
            return domain
        except:
            return url
    
    def _get_mock_search_results(self, query: str, patient_context: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate mock search results for demonstration purposes"""
        time.sleep(1)  # Simulate API delay
        
        if "diabetes" in query.lower() or (patient_context and "diabetes" in patient_context.get("diagnosis", "").lower()):
            return [
                {
                    "title": "Standards of Medical Care in Diabetes—2024",
                    "snippet": "The American Diabetes Association's Standards of Medical Care in Diabetes provides clinicians with evidence-based recommendations for managing patients with diabetes and prediabetes.",
                    "url": "https://diabetesjournals.org/care/issue/47/Supplement_1",
                    "source": "diabetesjournals.org"
                },
                {
                    "title": "Treatment Intensification for Patients with Type 2 Diabetes",
                    "snippet": "For patients with HbA1c levels > 8.0%, clinicians should consider adding additional pharmacologic agents or intensifying therapy.",
                    "url": "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7861057/",
                    "source": "ncbi.nlm.nih.gov"
                },
                {
                    "title": "Guidelines for Hypertension Management in Diabetic Patients",
                    "snippet": "Current recommendations suggest a target blood pressure of <140/90 mmHg for most patients with diabetes, with consideration of lower targets for certain high-risk populations.",
                    "url": "https://www.ahajournals.org/doi/10.1161/HYP.0000000000000065",
                    "source": "ahajournals.org"
                }
            ]
        elif "her2" in query.lower() or "breast cancer" in query.lower():
            return [
                {
                    "title": "NCCN Clinical Practice Guidelines in Oncology: Breast Cancer",
                    "snippet": "Current NCCN guidelines recommend dose-dense AC followed by paclitaxel with HER2-targeted therapy for HER2-positive breast cancer in the neoadjuvant setting.",
                    "url": "https://www.nccn.org/guidelines/guidelines-detail?category=1&id=1419",
                    "source": "nccn.org"
                },
                {
                    "title": "Dual HER2 Blockade in Neoadjuvant Treatment of Breast Cancer",
                    "snippet": "The addition of pertuzumab to trastuzumab-based regimens has been shown to increase the rate of pathologic complete response in neoadjuvant studies.",
                    "url": "https://www.nejm.org/doi/full/10.1056/NEJMoa1306801",
                    "source": "nejm.org"
                }
            ]
        else:
            return [
                {
                    "title": "Medical Guideline Search Results",
                    "snippet": "Search results for medical guidelines would appear here based on your query.",
                    "url": "https://example.com/guidelines",
                    "source": "example.com"
                }
            ]