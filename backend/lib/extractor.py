import pymupdf  # PyMuPDF

def extract_text_from_pdf(file_path):
    doc = pymupdf.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text