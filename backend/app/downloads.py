import io
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_LEFT
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

router = APIRouter(prefix="/api", tags=["downloads"])

class DownloadRequest(BaseModel):
    content: str
    filename: str = "analysis-report"

@router.post("/download/pdf")
async def download_pdf(request: DownloadRequest):
    try:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=inch,
            leftMargin=inch,
            topMargin=inch,
            bottomMargin=inch
        )
        
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=20,
            textColor='#1E3A5F'
        )
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            spaceBefore=16,
            spaceAfter=8,
            textColor='#1E3A5F'
        )
        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['Normal'],
            fontSize=11,
            leading=16,
            alignment=TA_LEFT
        )
        
        story = []
        story.append(Paragraph("Interview Prep Report", title_style))
        story.append(Spacer(1, 12))
        
        lines = request.content.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                story.append(Spacer(1, 8))
            elif line.startswith('##'):
                clean_line = line.lstrip('#').strip()
                story.append(Paragraph(clean_line, heading_style))
            elif line.startswith('#'):
                clean_line = line.lstrip('#').strip()
                story.append(Paragraph(clean_line, heading_style))
            elif line.startswith('**') and line.endswith('**'):
                clean_line = line.strip('*').strip()
                story.append(Paragraph(f"<b>{clean_line}</b>", body_style))
            else:
                clean_line = line.replace('**', '').replace('*', '')
                if clean_line:
                    story.append(Paragraph(clean_line, body_style))
        
        doc.build(story)
        buffer.seek(0)
        
        return StreamingResponse(
            buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={request.filename}.pdf"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")

@router.post("/download/docx")
async def download_docx(request: DownloadRequest):
    try:
        document = Document()
        
        title = document.add_heading('Interview Prep Report', 0)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        lines = request.content.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                document.add_paragraph()
            elif line.startswith('##'):
                clean_line = line.lstrip('#').strip()
                document.add_heading(clean_line, level=2)
            elif line.startswith('#'):
                clean_line = line.lstrip('#').strip()
                document.add_heading(clean_line, level=1)
            elif line.startswith('- ') or line.startswith('• '):
                clean_line = line[2:].replace('**', '').replace('*', '')
                p = document.add_paragraph(clean_line, style='List Bullet')
            elif line.startswith('**') and line.endswith('**'):
                clean_line = line.strip('*').strip()
                p = document.add_paragraph()
                run = p.add_run(clean_line)
                run.bold = True
            else:
                clean_line = line.replace('**', '').replace('*', '')
                if clean_line:
                    document.add_paragraph(clean_line)
        
        buffer = io.BytesIO()
        document.save(buffer)
        buffer.seek(0)
        
        return StreamingResponse(
            buffer,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f"attachment; filename={request.filename}.docx"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Word document generation failed: {str(e)}")
