import re
from pathlib import Path
import pdfplumber
from docx import Document

SKILL_WORDS = [
    "python", "java", "c++", "sql", "html", "css", "javascript",
    "fastapi", "django", "machine learning", "pandas", "excel"
]

def extract_text(filename: str, content: bytes) -> str:
    suffix = Path(filename).suffix.lower()
    if suffix == ".pdf":
        import io
        with pdfplumber.open(io.BytesIO(content)) as pdf:
            return "\n".join(page.extract_text() or "" for page in pdf.pages)
    if suffix == ".docx":
        import io
        doc = Document(io.BytesIO(content))
        return "\n".join(p.text for p in doc.paragraphs)
    raise ValueError("Only PDF and DOCX files are supported")

def parse_resume(text: str) -> dict:
    email_match = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
    phone_match = re.search(r"(?:\+?91[-\s]?)?[6-9]\d{9}", text)
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    name = lines[0][:150] if lines else None
    lower_text = text.lower()
    skills = [skill for skill in SKILL_WORDS if skill in lower_text]
    return {
        "name": name,
        "email": email_match.group(0) if email_match else None,
        "phone": phone_match.group(0) if phone_match else None,
        "skills": skills,
        "experience": None
    }
