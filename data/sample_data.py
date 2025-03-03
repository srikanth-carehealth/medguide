# =====================================
# data/sample_data.py
# =====================================
import json
from typing import Dict, List, Any, Optional

def get_sample_guidelines() -> List[Dict[str, Any]]:
    """Return sample guideline data"""
    return [
        {
            "id": "1",
            "title": "Diabetes Management - ADA 2024",
            "source": "American Diabetes Association",
            "lastUpdated": "Jan 2024"
        },
        {
            "id": "2",
            "title": "Hypertension Guidelines - JNC 8",
            "source": "Journal of the American Medical Association",
            "lastUpdated": "Dec 2023"
        },
        {
            "id": "3",
            "title": "Lipid Management in Cardiovascular Disease",
            "source": "American Heart Association",
            "lastUpdated": "Mar 2024"
        },
        {
            "id": "4",
            "title": "HER2+ Breast Cancer - NCCN Guidelines",
            "source": "National Comprehensive Cancer Network",
            "lastUpdated": "Feb 2024"
        }
    ]

def get_sample_uploaded_docs() -> List[Dict[str, Any]]:
    """Return sample uploaded documents"""
    return [
        {
            "id": "uploaded_1",
            "title": "Hospital Diabetes Protocol",
            "source": "Internal Document",
            "uploadedBy": "Dr. Sarah Chen",
            "uploadDate": "Feb 15, 2024",
            "lastUpdated": "Feb 15, 2024"
        },
        {
            "id": "uploaded_2",
            "title": "Cardiology Department BP Management",
            "source": "Internal Document",
            "uploadedBy": "Dr. Michael Johnson",
            "uploadDate": "Jan 22, 2024",
            "lastUpdated": "Jan 22, 2024"
        }
    ]

def get_sample_patient(condition_type: str = "diabetes") -> Dict[str, Any]:
    """Return sample patient data based on condition type"""
    if condition_type == "her2":
        return {
            "id": "p002",
            "name": "Sarah Johnson",
            "age": 47,
            "gender": "female",
            "diagnosis": "Invasive Ductal Carcinoma, HER2+",
            "stage": "cT2N1M0 stage IIB",
            "receptorStatus": {
                "ER": "15%",
                "PR": "5%",
                "HER2": "3+ by IHC (confirmed by FISH with HER2/CEP17 ratio 5.2)"
            },
            "recentLabs": {
                "CBC": "WNL",
                "CMP": "WNL",
                "LVEF": "62%"
            }
        }
    else:  # diabetes or default
        return {
            "id": "p001",
            "name": "James Wilson",
            "age": 54,
            "gender": "male",
            "diagnosis": "Type 2 Diabetes, Hypertension",
            "recentLabs": {
                "HbA1c": "8.2%",
                "BP": "142/88",
                "LDL": "138mg/dL"
            }
        }

def get_guideline_content(guideline_id: str) -> str:
    """Return sample content for a specific guideline"""
    
    # Diabetes content
    if guideline_id == "1":
        return """
# Glycemic Targets and Management Guidelines

Regular monitoring of glycemia in patients with diabetes is crucial to assess treatment efficacy and reduce risk of hypoglycemia and hyperglycemia. The advent of continuous glucose monitoring (CGM) technology has revolutionized this aspect of diabetes care.

## Recommendations

8.1 Most patients with diabetes should be assessed using glycated hemoglobin (HbA1c) testing at least twice per year. (Grade A)

8.2 When glycemic targets are not being met, quarterly assessments using HbA1c testing are recommended. (Grade B)

All adult patients with diabetes should have an individualized glycemic target based on their duration of diabetes, age/life expectancy, comorbid conditions, known cardiovascular disease or advanced microvascular complications, hypoglycemia unawareness, and individual patient considerations.

8.5 For patients with Type 2 diabetes with HbA1c levels > 8.0%, clinicians should consider intensifying pharmacologic therapy, adding additional agents, or referral to a specialist. (Grade A)
        """
    
    # Hypertension content
    elif guideline_id == "2":
        return """
# Hypertension Guidelines - JNC 8

## Recommendations

1. In the general population ≥60 years of age, initiate pharmacologic treatment to lower BP at systolic blood pressure (SBP) ≥150 mm Hg or diastolic blood pressure (DBP) ≥90 mm Hg and treat to a goal SBP <150 mm Hg and goal DBP <90 mm Hg. (Grade A)

2. In the general population <60 years of age, initiate pharmacologic treatment to lower BP at DBP ≥90 mm Hg and treat to a goal DBP <90 mm Hg. (Grade A)

3. In the general population <60 years of age, initiate pharmacologic treatment to lower BP at SBP ≥140 mm Hg and treat to a goal SBP <140 mm Hg. (Grade E)

4. In the population aged ≥18 years with chronic kidney disease (CKD), initiate pharmacologic treatment to lower BP at SBP ≥140 mm Hg or DBP ≥90 mm Hg and treat to goal SBP <140 mm Hg and goal DBP <90 mm Hg. (Grade E)

5. In the population aged ≥18 years with diabetes, initiate pharmacologic treatment to lower BP at SBP ≥140 mm Hg or DBP ≥90 mm Hg and treat to a goal SBP <140 mm Hg and goal DBP <90 mm Hg. (Grade E)
        """
    
    # HER2+ Breast Cancer content
    elif guideline_id == "4":
        return """
# NCCN Guidelines for HER2-Positive Breast Cancer

## Neoadjuvant/Adjuvant Therapy Recommendations

Preferred regimens for HER2-positive disease include:

1. Doxorubicin/cyclophosphamide (AC) followed by paclitaxel + trastuzumab ± pertuzumab
   - AC: Doxorubicin 60 mg/m² IV + Cyclophosphamide 600 mg/m² IV q2-3wks × 4 cycles
   - Followed by: Paclitaxel 80 mg/m² IV weekly × 12 weeks
   - With: Trastuzumab 4 mg/kg IV loading dose, then 2 mg/kg IV weekly
   - And: Pertuzumab 840 mg IV loading dose, then 420 mg IV q3wks (optional)

2. Docetaxel/carboplatin/trastuzumab + pertuzumab (TCH+P)
   - Docetaxel 75 mg/m² IV + Carboplatin AUC 6 IV day 1 q3wks × 6 cycles
   - With: Trastuzumab 8 mg/kg IV loading dose, then 6 mg/kg IV q3wks
   - And: Pertuzumab 840 mg IV loading dose, then 420 mg IV q3wks

The addition of pertuzumab to trastuzumab-based regimens has been shown to increase the rate of pCR in neoadjuvant studies.

Cardiac monitoring:
- LVEF assessment at baseline and q3mo during HER2-targeted therapy
- Hold HER2-targeted therapy for >16% absolute decrease in LVEF from baseline, or LVEF <50%
        """
    
    # Default content
    else:
        return """
# Medical Guideline Content

This is a placeholder for guideline content. In a real application, this would contain the actual text from the selected guideline document.

## Recommendations

1. Recommendation one would appear here.
2. Recommendation two would appear here.
3. Recommendation three would appear here.

## Evidence Quality

The quality of evidence supporting these recommendations is [level].
        """