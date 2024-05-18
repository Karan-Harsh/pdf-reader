import PyPDF2
import logging
from fastapi import HTTPException

logger = logging.getLogger(__name__)


def extract_text_from_pdf(pdf_file):
    try:
        with open(pdf_file, "rb") as f:
            pdf_reader = PyPDF2.PdfReader(f)
            num_pages = len(pdf_reader.pages)
            text = ""
            for page_num in range(num_pages):
                page_object = pdf_reader.pages[page_num]
                text += page_object.extract_text()
        return text
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {e}")
        raise HTTPException(status_code=500, detail="Error extracting text from PDF")
