import io
from datetime import datetime
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

router = APIRouter(prefix="/api/xray", tags=["downloads"])

class DownloadRequest(BaseModel):
    report_content: str
    job_title: str = ""
    company_name: str = ""

def add_header_footer(canvas, doc):
    canvas.saveState()
    canvas.setFont('Helvetica-Bold', 9)
    canvas.setFillColor(HexColor('#1E3A5F'))
    canvas.drawString(inch, letter[1] - 0.5 * inch, "GetHiredAlly - Job Analysis Report")
    canvas.setFont('Helvetica', 9)
    canvas.setFillColor(HexColor('#666666'))
    page_num = f"Page {doc.page}"
    date_str = datetime.now().strftime("%B %d, %Y")
    canvas.drawString(inch, 0.5 * inch, date_str)
    canvas.drawRightString(letter[0] - inch, 0.5 * inch, page_num)
    canvas.restoreState()

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
            fontSize=24,
            spaceAfter=8,
            textColor=HexColor('#1E3A5F'),
            fontName='Helvetica-Bold',
            alignment=TA_CENTER
        )
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Normal'],
            fontSize=14,
            spaceAfter=24,
            textColor=HexColor('#666666'),
            alignment=TA_CENTER
        )
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            spaceBefore=16,
            spaceAfter=8,
            textColor=HexColor('#1E3A5F'),
            fontName='Helvetica-Bold'
        )
        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['Normal'],
            fontSize=11,
            leading=16,
            alignment=TA_LEFT
        )
        bullet_style = ParagraphStyle(
            'CustomBullet',
            parent=styles['Normal'],
            fontSize=11,
            leading=16,
            leftIndent=20,
            bulletIndent=10
        )
        
        story = []
        
        title_text = request.job_title if request.job_title else "Job Analysis Report"
        story.append(Paragraph(title_text, title_style))
        
        if request.company_name:
            story.append(Paragraph(request.company_name, subtitle_style))
        else:
            story.append(Spacer(1, 24))
        
        lines = request.report_content.split('\n')
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
            elif line.startswith('- ') or line.startswith('• '):
                clean_line = line[2:].replace('**', '').replace('*', '')
                story.append(Paragraph(f"• {clean_line}", bullet_style))
            elif line.startswith('**') and line.endswith('**'):
                clean_line = line.strip('*').strip()
                story.append(Paragraph(f"<b>{clean_line}</b>", body_style))
            else:
                clean_line = line.replace('**', '').replace('*', '')
                if clean_line:
                    story.append(Paragraph(clean_line, body_style))
        
        doc.build(story, onFirstPage=add_header_footer, onLaterPages=add_header_footer)
        buffer.seek(0)
        
        safe_company = request.company_name.replace(' ', '_').replace('/', '_') if request.company_name else 'Analysis'
        filename = f"XRay_Analysis_{safe_company}.pdf"
        
        return StreamingResponse(
            buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")

@router.post("/download/docx")
async def download_docx(request: DownloadRequest):
    try:
        document = Document()
        
        title_text = request.job_title if request.job_title else "Job Analysis Report"
        title = document.add_heading(title_text, 0)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        if request.company_name:
            subtitle = document.add_paragraph(request.company_name)
            subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for run in subtitle.runs:
                run.font.size = Pt(14)
        
        document.add_paragraph()
        
        lines = request.report_content.split('\n')
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
                document.add_paragraph(clean_line, style='List Bullet')
            elif line.startswith('**') and line.endswith('**'):
                clean_line = line.strip('*').strip()
                p = document.add_paragraph()
                run = p.add_run(clean_line)
                run.bold = True
            else:
                clean_line = line.replace('**', '').replace('*', '')
                if clean_line:
                    p = document.add_paragraph(clean_line)
                    for run in p.runs:
                        run.font.size = Pt(11)
        
        buffer = io.BytesIO()
        document.save(buffer)
        buffer.seek(0)
        
        safe_company = request.company_name.replace(' ', '_').replace('/', '_') if request.company_name else 'Analysis'
        filename = f"XRay_Analysis_{safe_company}.docx"
        
        return StreamingResponse(
            buffer,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Word document generation failed: {str(e)}")
