import pdfplumber
import pytesseract
from PIL import Image
import io

def extract_text_from_pdf(file: bytes) -> str:
    """Extract text from uploaded PDF bytes."""
    try:
        text = ""
        with pdfplumber.open(io.BytesIO(file)) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ''
        return text.strip()
    except Exception as e:
        return f"[ERROR extracting PDF text] {e}"

def extract_text_from_image(file: bytes) -> str:
    """Extract text using OCR from uploaded image bytes."""
    try:
        image = Image.open(io.BytesIO(file))
        text = pytesseract.image_to_string(image)
        return text.strip()
    except Exception as e:
        return f"[ERROR extracting image text] {e}"
def extract_text(file: bytes, filename: str) -> str:
    if filename.lower().endswith(".pdf"):
        return extract_text_from_pdf(file)
    elif filename.lower().endswith((".jpg", ".jpeg", ".png")):
        return extract_text_from_image(file)
    else:
        return "[ERROR: Unsupported file format]"
