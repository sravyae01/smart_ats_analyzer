# Create a test file to learn: test_pdf_parser.py
import PyPDF2
import docx

def extract_from_pdf(file_path):
    """Extract text from PDF file"""
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ''
        for page in reader.pages:
            text += page.extract_text()
    return text

def extract_from_docx(file_path):
    """Extract text from DOCX file"""
    doc = docx.Document(file_path)
    text = ''
    for paragraph in doc.paragraphs:
        text += paragraph.text + '\n'
    return text

# Test with a resume file
# result = extract_from_pdf('path/to/resume.pdf')
# print(result)