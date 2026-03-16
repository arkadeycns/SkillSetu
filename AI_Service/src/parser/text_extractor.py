import pdfplumber
import docx


def extract_text_from_pdf(file_stream):

    text = ""

    with pdfplumber.open(file_stream) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""

    return text


def extract_text_from_docx(file_stream):

    document = docx.Document(file_stream)

    text = "\n".join([p.text for p in document.paragraphs])

    return text