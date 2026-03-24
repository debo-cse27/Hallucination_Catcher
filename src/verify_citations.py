import requests
import time
import re
from rapidfuzz import fuzz

def clean_title(title):
    if not title:
        return ""
    title = title.replace("Faculty Opinions recommendation of", "")
    title = re.sub(r'[^a-zA-Z0-9\s]', '', title)
    return title.lower().strip()

def verify_citation(citation, user_email):
    # Dynamically inject the user's email into the headers
    headers = {'User-Agent': f'CitationVerificationTool/1.0 (mailto:{user_email})'}
    
    raw_extracted_title = citation.get('title', '')
    extracted_doi = citation.get('doi')
    clean_extracted_title = clean_title(raw_extracted_title)
    
    time.sleep(0.1) 
    
    if extracted_doi:
        url = f"https://api.crossref.org/works/{extracted_doi}"
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                raw_real_title = data['message'].get('title', [''])[0] 
                clean_real_title = clean_title(raw_real_title)
                
                similarity = fuzz.ratio(clean_extracted_title, clean_real_title)
                if clean_extracted_title in clean_real_title or clean_real_title in clean_extracted_title:
                     similarity = 100
                
                if similarity > 80:
                    return {"status": "Verified", "real_title": raw_real_title, "score": similarity}
                else:
                    return {"status": "Mismatched Metadata", "real_title": raw_real_title, "score": similarity}
            elif response.status_code == 404:
                return {"status": "Ghost Citation", "real_title": "DOI not found in registry", "score": 0}
        except requests.exceptions.RequestException as e:
            return {"status": "API Error", "real_title": str(e), "score": 0}

    elif raw_extracted_title and raw_extracted_title != "No Title Found":
        url = "https://api.crossref.org/works"
        params = {'query.bibliographic': raw_extracted_title, 'rows': 3} 
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            if response.status_code == 200:
                items = response.json()['message'].get('items', [])
                best_score = 0
                best_title = "No close match found"
                
                for item in items:
                    raw_real_title = item.get('title', [''])[0]
                    clean_real_title = clean_title(raw_real_title)
                    similarity = fuzz.ratio(clean_extracted_title, clean_real_title)
                    if clean_extracted_title in clean_real_title or clean_real_title in clean_extracted_title:
                         similarity = 100
                    if similarity > best_score:
                        best_score = similarity
                        best_title = raw_real_title
                
                if best_score > 80:
                    return {"status": "Verified", "real_title": best_title, "score": best_score}
                else:
                    return {"status": "Ghost Citation", "real_title": f"Closest registry match: {best_title}", "score": best_score}
                    
        except requests.exceptions.RequestException as e:
            return {"status": "API Error", "real_title": str(e), "score": 0}
            
    return {"status": "Incomplete Data", "real_title": "Insufficient metadata to verify", "score": 0}