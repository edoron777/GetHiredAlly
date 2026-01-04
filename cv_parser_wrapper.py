import re
import os
import spacy
import docx2txt
from pdfminer.high_level import extract_text as extract_pdf_text

nlp = spacy.load('en_core_web_sm')

def parse_cv(file_path):
    # Extract text
    if file_path.endswith('.pdf'):
        text = extract_pdf_text(file_path)
    else:
        text = docx2txt.process(file_path)
    
    doc = nlp(text)
    
    # Extract contact info
    email = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
    phone = re.findall(r'[\+]?[(]?[0-9]{1,3}[)]?[-\s\.]?[(]?[0-9]{1,4}[)]?[-\s\.]?[0-9]{1,4}[-\s\.]?[0-9]{1,9}', text)
    
    # Extract entities
    persons = [ent.text for ent in doc.ents if ent.label_ == 'PERSON']
    orgs = [ent.text for ent in doc.ents if ent.label_ == 'ORG']
    
    return {
        'name': persons[0] if persons else None,
        'email': email[0] if email else None,
        'phone': phone[0] if phone else None,
        'companies': orgs[:10],
        'raw_text_length': len(text)
    }

if __name__ == '__main__':
    import sys
    import json
    result = parse_cv(sys.argv[1])
    print(json.dumps(result, indent=2))
