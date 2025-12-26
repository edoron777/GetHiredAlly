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
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

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

def set_run_font(run, font_name='Calibri', size=11, bold=False, color=None):
    run.font.name = font_name
    run.font.size = Pt(size)
    run.font.bold = bold
    if color:
        run.font.color.rgb = color
    r = run._element
    r.rPr.rFonts.set(qn('w:eastAsia'), font_name)

def set_paragraph_spacing(paragraph, space_before=0, space_after=0, line_spacing=1.15):
    pPr = paragraph._p.get_or_add_pPr()
    spacing = OxmlElement('w:spacing')
    spacing.set(qn('w:before'), str(int(space_before * 20)))
    spacing.set(qn('w:after'), str(int(space_after * 20)))
    spacing.set(qn('w:line'), str(int(line_spacing * 240)))
    spacing.set(qn('w:lineRule'), 'auto')
    pPr.append(spacing)

@router.post("/download/docx")
async def download_docx(request: DownloadRequest):
    try:
        document = Document()
        
        navy_color = RGBColor(0x1E, 0x3A, 0x5F)
        dark_gray = RGBColor(0x37, 0x41, 0x51)
        
        title_text = request.job_title if request.job_title else "Job Analysis Report"
        title_para = document.add_paragraph()
        title_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        title_run = title_para.add_run(title_text)
        set_run_font(title_run, size=24, bold=True, color=navy_color)
        set_paragraph_spacing(title_para, space_after=6)
        
        if request.company_name:
            subtitle_para = document.add_paragraph()
            subtitle_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
            subtitle_run = subtitle_para.add_run(request.company_name)
            set_run_font(subtitle_run, size=14, color=dark_gray)
            set_paragraph_spacing(subtitle_para, space_after=12)
        else:
            spacer = document.add_paragraph()
            set_paragraph_spacing(spacer, space_after=12)
        
        lines = request.report_content.split('\n')
        skip_next_empty = False
        
        for line in lines:
            line = line.strip()
            
            if line == '---' or line == '***' or line == '___':
                skip_next_empty = True
                continue
            
            if not line:
                if not skip_next_empty:
                    spacer = document.add_paragraph()
                    set_paragraph_spacing(spacer, space_before=3, space_after=3)
                skip_next_empty = False
                continue
            
            skip_next_empty = False
            
            if line.startswith('###'):
                clean_line = line.lstrip('#').strip()
                p = document.add_paragraph()
                run = p.add_run(clean_line)
                set_run_font(run, size=13, bold=True, color=dark_gray)
                set_paragraph_spacing(p, space_before=12, space_after=6)
            elif line.startswith('##'):
                clean_line = line.lstrip('#').strip()
                p = document.add_paragraph()
                run = p.add_run(clean_line)
                set_run_font(run, size=16, bold=True, color=navy_color)
                set_paragraph_spacing(p, space_before=18, space_after=12)
            elif line.startswith('#'):
                clean_line = line.lstrip('#').strip()
                p = document.add_paragraph()
                run = p.add_run(clean_line)
                set_run_font(run, size=18, bold=True, color=navy_color)
                set_paragraph_spacing(p, space_before=18, space_after=12)
            elif line.startswith('- ') or line.startswith('• ') or line.startswith('* '):
                clean_line = line[2:].replace('**', '').replace('*', '')
                p = document.add_paragraph(style='List Bullet')
                run = p.add_run(clean_line)
                set_run_font(run, size=11)
                set_paragraph_spacing(p, space_before=2, space_after=2)
            elif line.startswith('**') and line.endswith('**'):
                clean_line = line.strip('*').strip()
                p = document.add_paragraph()
                run = p.add_run(clean_line)
                set_run_font(run, size=11, bold=True)
                set_paragraph_spacing(p, space_before=6, space_after=6)
            else:
                clean_line = line.replace('**', '').replace('*', '')
                if clean_line:
                    p = document.add_paragraph()
                    run = p.add_run(clean_line)
                    set_run_font(run, size=11)
                    set_paragraph_spacing(p, space_before=3, space_after=6)
        
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
