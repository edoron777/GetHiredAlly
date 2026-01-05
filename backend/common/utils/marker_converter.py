"""Convert CV structure markers to HTML for better display."""

import re
from html import escape


def _process_bold_markers(text: str) -> str:
    """Convert [BOLD] markers to <strong> tags, closing at end of text if unclosed."""
    if '[BOLD]' not in text:
        return text
    
    if '[/BOLD]' in text:
        return text.replace('[BOLD]', '<strong>').replace('[/BOLD]', '</strong>')
    
    result = text.replace('[BOLD]', '<strong>')
    
    open_count = result.count('<strong>')
    close_count = result.count('</strong>')
    
    if open_count > close_count:
        result += '</strong>' * (open_count - close_count)
    
    return result


def convert_markers_to_html(text: str) -> str:
    """Convert structure markers to HTML elements for Document View display.
    
    Converts:
    - [H1] text -> <h2 class="cv-section">text</h2>
    - [H2] text -> <h3 class="cv-subsection">text</h3>
    - [BOLD] text -> <strong>text</strong>
    - [BULLET] text -> <li>text</li> (wrapped in <ul>)
    
    Args:
        text: CV content with structure markers
        
    Returns:
        HTML-formatted string for display
    """
    if not text:
        return ""
    
    lines = text.split('\n')
    result_lines = []
    in_bullet_list = False
    
    for line in lines:
        is_bullet = '[BULLET]' in line
        
        if is_bullet and not in_bullet_list:
            result_lines.append('<ul class="cv-bullets">')
            in_bullet_list = True
        elif not is_bullet and in_bullet_list:
            result_lines.append('</ul>')
            in_bullet_list = False
        
        if '[H1]' in line:
            content = re.sub(r'\[H1\]\s*', '', line).strip()
            safe_content = escape(content)
            safe_content = _process_bold_markers(safe_content)
            result_lines.append(f'<h2 class="cv-section">{safe_content}</h2>')
        
        elif '[H2]' in line:
            content = re.sub(r'\[H2\]\s*', '', line).strip()
            safe_content = escape(content)
            safe_content = _process_bold_markers(safe_content)
            result_lines.append(f'<h3 class="cv-subsection">{safe_content}</h3>')
        
        elif '[BULLET]' in line:
            content = re.sub(r'\[BULLET\]\s*', '', line).strip()
            safe_content = escape(content)
            safe_content = _process_bold_markers(safe_content)
            result_lines.append(f'<li>{safe_content}</li>')
        
        elif line.strip():
            safe_content = escape(line)
            safe_content = _process_bold_markers(safe_content)
            result_lines.append(f'<p>{safe_content}</p>')
        
        else:
            result_lines.append('<br/>')
    
    if in_bullet_list:
        result_lines.append('</ul>')
    
    return '\n'.join(result_lines)
