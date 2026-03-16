import fitz

def parse_contract(file_content: bytes) -> list[str]:
    extracted_text = ""
    with fitz.open(stream=file_content, filetype="pdf") as doc:
        for page in doc:
            extracted_text += page.get_text() + "\n"
    
    # Split the contract into logical clauses (roughly by paragraph for this implementation)
    # We filter out very short lines like page numbers
    clauses = [p.strip() for p in extracted_text.split('\n\n') if len(p.strip()) > 20]
    
    # If the formatting didn't have double newlines, fallback to single newlines
    if len(clauses) < 2 and len(extracted_text) > 100:
        clauses = [p.strip() for p in extracted_text.split('\n') if len(p.strip()) > 20]
        
    return clauses
