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

def set_run_font(run, font_name='Arial', size=11, bold=False, color=None):
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

def set_cell_shading(cell, color_hex):
    shading = OxmlElement('w:shd')
    shading.set(qn('w:fill'), color_hex)
    cell._tc.get_or_add_tcPr().append(shading)

def add_bottom_border(paragraph, color_hex='1E3A5F', size=6):
    pPr = paragraph._p.get_or_add_pPr()
    pBdr = OxmlElement('w:pBdr')
    bottom = OxmlElement('w:bottom')
    bottom.set(qn('w:val'), 'single')
    bottom.set(qn('w:sz'), str(size))
    bottom.set(qn('w:color'), color_hex)
    pBdr.append(bottom)
    pPr.append(pBdr)

@router.post("/download/docx")
async def download_docx(request: DownloadRequest):
    try:
        document = Document()
        
        navy_color = RGBColor(0x1E, 0x3A, 0x5F)
        dark_gray = RGBColor(0x37, 0x41, 0x51)
        white_color = RGBColor(0xFF, 0xFF, 0xFF)
        
        sections = document.sections
        for section in sections:
            section.top_margin = Inches(0.5)
            section.bottom_margin = Inches(0.75)
            section.left_margin = Inches(0.75)
            section.right_margin = Inches(0.75)
        
        header_table = document.add_table(rows=1, cols=1)
        header_table.autofit = False
        header_table.allow_autofit = False
        header_cell = header_table.cell(0, 0)
        header_cell.width = Inches(7)
        set_cell_shading(header_cell, '1E3A5F')
        
        header_para = header_cell.paragraphs[0]
        header_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        header_run = header_para.add_run("GetHiredAlly - Job Analysis Report")
        set_run_font(header_run, size=14, bold=True, color=white_color)
        
        from docx.shared import Twips
        tc = header_cell._tc
        tcPr = tc.get_or_add_tcPr()
        tcMar = OxmlElement('w:tcMar')
        for margin_name in ['top', 'bottom', 'left', 'right']:
            margin = OxmlElement(f'w:{margin_name}')
            margin.set(qn('w:w'), '200')
            margin.set(qn('w:type'), 'dxa')
            tcMar.append(margin)
        tcPr.append(tcMar)
        
        document.add_paragraph()
        
        info_table = document.add_table(rows=1, cols=1)
        info_table.autofit = False
        info_cell = info_table.cell(0, 0)
        info_cell.width = Inches(7)
        set_cell_shading(info_cell, 'F3F4F6')
        
        tc_info = info_cell._tc
        tcPr_info = tc_info.get_or_add_tcPr()
        tcBorders = OxmlElement('w:tcBorders')
        for border_name in ['top', 'bottom', 'left', 'right']:
            border = OxmlElement(f'w:{border_name}')
            border.set(qn('w:val'), 'single')
            border.set(qn('w:sz'), '4')
            border.set(qn('w:color'), 'E5E7EB')
            tcBorders.append(border)
        tcPr_info.append(tcBorders)
        
        tcMar_info = OxmlElement('w:tcMar')
        for margin_name in ['top', 'bottom', 'left', 'right']:
            margin = OxmlElement(f'w:{margin_name}')
            margin.set(qn('w:w'), '150')
            margin.set(qn('w:type'), 'dxa')
            tcMar_info.append(margin)
        tcPr_info.append(tcMar_info)
        
        info_para = info_cell.paragraphs[0]
        title_text = request.job_title if request.job_title else "Job Analysis Report"
        job_run = info_para.add_run(f"Job Title: {title_text}")
        set_run_font(job_run, size=10, bold=True)
        
        if request.company_name:
            info_para.add_run("\n")
            company_run = info_para.add_run(f"Company: {request.company_name}")
            set_run_font(company_run, size=10)
        
        info_para.add_run("\n")
        date_run = info_para.add_run(f"Generated: {datetime.now().strftime('%B %d, %Y')}")
        set_run_font(date_run, size=10, color=dark_gray)
        
        document.add_paragraph()
        
        title_para = document.add_paragraph()
        title_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        title_run = title_para.add_run(title_text)
        set_run_font(title_run, size=26, bold=True, color=navy_color)
        set_paragraph_spacing(title_para, space_after=12)
        
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
                    set_paragraph_spacing(spacer, space_before=2, space_after=2)
                skip_next_empty = False
                continue
            
            skip_next_empty = False
            
            if line.startswith('###'):
                clean_line = line.lstrip('#').strip()
                p = document.add_paragraph()
                run = p.add_run(clean_line)
                set_run_font(run, size=12, bold=True, color=dark_gray)
                set_paragraph_spacing(p, space_before=10, space_after=6)
            elif line.startswith('##'):
                clean_line = line.lstrip('#').strip()
                p = document.add_paragraph()
                add_bottom_border(p, '1E3A5F', 4)
                run = p.add_run(clean_line)
                set_run_font(run, size=14, bold=True, color=navy_color)
                set_paragraph_spacing(p, space_before=16, space_after=8)
            elif line.startswith('#'):
                clean_line = line.lstrip('#').strip()
                p = document.add_paragraph()
                add_bottom_border(p, '1E3A5F', 6)
                run = p.add_run(clean_line)
                set_run_font(run, size=16, bold=True, color=navy_color)
                set_paragraph_spacing(p, space_before=16, space_after=10)
            elif line.startswith('- ') or line.startswith('• ') or line.startswith('* '):
                clean_line = line[2:].replace('**', '').replace('*', '')
                p = document.add_paragraph(style='List Bullet')
                run = p.add_run(clean_line)
                set_run_font(run, size=11)
                set_paragraph_spacing(p, space_before=1, space_after=1)
            elif line.startswith('**') and line.endswith('**'):
                clean_line = line.strip('*').strip()
                p = document.add_paragraph()
                run = p.add_run(clean_line)
                set_run_font(run, size=11, bold=True)
                set_paragraph_spacing(p, space_before=4, space_after=4)
            else:
                clean_line = line.replace('**', '').replace('*', '')
                if clean_line:
                    p = document.add_paragraph()
                    run = p.add_run(clean_line)
                    set_run_font(run, size=11)
                    set_paragraph_spacing(p, space_before=2, space_after=4)
        
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
