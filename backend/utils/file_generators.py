from io import BytesIO
from fpdf import FPDF
from docx import Document
from docx.shared import Pt, Inches


def generate_pdf(content: str) -> bytes:
    """Generate PDF from text content."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', size=11)
    pdf.set_auto_page_break(auto=True, margin=15)

    lines = content.split('\n')

    for line in lines:
        if line.isupper() and len(line) < 50 and line.strip():
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 8, line, ln=True)
            pdf.set_font('Arial', size=11)
        else:
            try:
                pdf.multi_cell(0, 6, line)
            except:
                safe_line = line.encode('latin-1', 'ignore').decode('latin-1')
                pdf.multi_cell(0, 6, safe_line)

    return pdf.output(dest='S').encode('latin-1')


def generate_docx(content: str) -> bytes:
    """Generate DOCX from text content."""
    doc = Document()

    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)

    lines = content.split('\n')

    for line in lines:
        if not line.strip():
            doc.add_paragraph()
        elif line.isupper() and len(line) < 50:
            p = doc.add_paragraph(line)
            if p.runs:
                p.runs[0].bold = True
                p.runs[0].font.size = Pt(14)
        else:
            p = doc.add_paragraph(line)
            if p.runs:
                p.runs[0].font.size = Pt(11)

    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)

    return buffer.getvalue()
