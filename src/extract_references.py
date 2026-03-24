import requests
from bs4 import BeautifulSoup

def process_pdf_with_grobid(pdf_path):
    url = "http://localhost:8070/api/processReferences"
    try:
        with open(pdf_path, 'rb') as f:
            files = {'input': (pdf_path, f, 'application/pdf')}
            response = requests.post(url, files=files)
            
        if response.status_code == 200:
            return response.text 
        else:
            return None
    except Exception:
        return None

def parse_grobid_xml(xml_data):
    soup = BeautifulSoup(xml_data, 'lxml-xml')
    citations = []
    
    for bibl in soup.find_all('biblStruct'):
        citation_data = {}
        
        title_tag = bibl.find('title', level='a')
        if not title_tag:
            title_tag = bibl.find('title', level='m')
        citation_data['title'] = title_tag.text.strip() if title_tag else "No Title Found"
        
        doi_tag = bibl.find('idno', type='DOI')
        citation_data['doi'] = doi_tag.text.strip() if doi_tag else None
        
        date_tag = bibl.find('date')
        citation_data['year'] = date_tag.get('when') if date_tag else "Unknown Year"
        
        citations.append(citation_data)
        
    return citations