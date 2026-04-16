from __future__ import annotations

from io import BytesIO

from docx import Document
from pypdf import PdfReader


class DocumentParser:
    @staticmethod
    def parse(filename: str, raw: bytes) -> str:
        lower = filename.lower()
        if lower.endswith(".pdf"):
            return DocumentParser._parse_pdf(raw)
        if lower.endswith(".docx"):
            return DocumentParser._parse_docx(raw)
        raise ValueError("Unsupported file type. Please upload PDF or DOCX.")

    @staticmethod
    def _parse_pdf(raw: bytes) -> str:
        reader = PdfReader(BytesIO(raw))
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(pages).strip()

    @staticmethod
    def _parse_docx(raw: bytes) -> str:
        doc = Document(BytesIO(raw))
        return "\n".join(p.text for p in doc.paragraphs).strip()
