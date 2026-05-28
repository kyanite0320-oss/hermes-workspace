#!/usr/bin/env python3
"""
Convert markdown research report to a beautiful dark-theme HTML page.
Self-contained, responsive, gaming-inspired design.
"""

import re

def parse_markdown(content):
    """Simple markdown parser that returns structured blocks."""
    lines = content.split('\n')
    blocks = []
    i = 0
    in_code_block = False
    code_buffer = []
    code_lang = ''
    
    while i < len(lines):
        line = lines[i]
        
        # Code block handling
        if line.startswith('```'):
            if in_code_block:
                code_buffer.append(line)
                blocks.append({'type': 'code', 'content': '\n'.join(code_buffer), 'lang': code_lang})
                code_buffer = []
                in_code_block = False
            else:
                in_code_block = True
                code_lang = line[3:].strip()
                code_buffer = [line]
            i += 1
            continue
        
        if in_code_block:
            code_buffer.append(line)
            i += 1
            continue
        
        # Horizontal rule
        if line.strip() == '---':
            blocks.append({'type': 'hr'})
            i += 1
            continue
        
        # Empty line
        if line.strip() == '':
            i += 1
            continue
        
        # Headers
        h_match = re.match(r'^(#{1,6})\s+(.+)$', line)
        if h_match:
            level = len(h_match.group(1))
            text = h_match.group(2).strip()
            # Remove anchor links like [text](#anchor)
            text = re.sub(r'\s*\[.*?\]\(.*?\)', '', text).strip()
            blocks.append({'type': f'h{level}', 'content': text})
            i += 1
            continue
        
        # Table
        if '|' in line and line.strip().startswith('|'):
            table_lines = []
            while i < len(lines) and '|' in lines[i] and lines[i].strip().startswith('|'):
                table_lines.append(lines[i])
                i += 1
            blocks.append({'type': 'table', 'content': '\n'.join(table_lines)})
            continue
        
        # Bold line (single line with **)
        if re.match(r'^\*\*.*\*\*$', line.strip()):
            blocks.append({'type': 'bold_line', 'content': line.strip().strip('*')})
            i += 1
            continue
        
        # List items
        if re.match(r'^(\d+\.|-|\*)\s+', line):
            list_items = []
            while i < len(lines):
                line_stripped = lines[i].strip()
                if line_stripped == '' or line_stripped == '---':
                    break
                if re.match(r'^(\d+\.|-|\*)\s+', line_stripped):
                    list_items.append(line_stripped)
                    i += 1
                else:
                    break
            blocks.append({'type': 'list', 'content': '\n'.join(list_items)})
            continue
        
        # Regular paragraph
        para_lines = []
        while i < len(lines):
            if lines[i].strip() == '' or lines[i].strip() == '---' or lines[i].strip().startswith('```'):
                break
            para_lines.append(lines[i])
            i += 1
        if para_lines:
            blocks.append({'type': 'paragraph', 'content': '\n'.join(para_lines)})
            continue
        
        i += 1
    
    return blocks


def parse_table(markdown_table):
    """Parse a markdown table into rows and columns."""
    lines = markdown_table.strip().split('\n')
    rows = []
    for line in lines:
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        rows.append(cells)
    
    # Remove separator row (index 1)
    header = rows[0] if len(rows) > 0 else []
    data = rows[2:] if len(rows) > 2 else []
    
    # Detect alignment from separator row
    alignments = []
    if len(rows) > 1:
        sep_cells = rows[1]
        for cell in sep_cells:
            if cell.startswith(':') and cell.endswith(':'):
                alignments.append('center')
            elif cell.endswith(':'):
                alignments.append('right')
            elif cell.startswith(':'):
                alignments.append('left')
            else:
                alignments.append('left')
    
    return header, data, alignments


def render_inline_markdown(text):
    """Convert inline markdown to HTML."""
    # Bold
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    # Italic
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    # Inline code
    text = re.sub(r'`(.+?)`', r'<code>\1</code>', text)
    return text


def strip_inline_markdown(text):
    """Remove markdown formatting for HTML attribute use."""
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'\*(.+?)\*', r'\1', text)
    text = re.sub(r'`(.+?)`', r'\1', text)
    return text


def get_section_color(h1_text, h2_text):
    """Return color scheme based on section."""
    color_schemes = [
        # (match_keywords, bg, border, accent, heading_color)
        (['市场概览', '扫榜'], '#1a1a2e', '#4a4a8a', '#6c63ff', '#8b83ff'),
        (['直接竞品', '竞品参考', '同品类'], '#1e2a1e', '#3a6a3a', '#4caf50', '#66bb6a'),
        (['高热度玩法'], '#2a1a1a', '#8a3a3a', '#ff6b6b', '#ff8a8a'),
        (['无尽冬日'], '#1a1a2e', '#4a4a6a', '#ffd700', '#ffe44d'),
        (['搜打撤', '超自然行动组', '深度拆解2'], '#1e1a2a', '#6a3a8a', '#bb86fc', '#ce93d8'),
        (['融合策略矩阵'], '#1a2a2a', '#3a6a6a', '#00bcd4', '#4dd0e1'),
        (['落地路线图'], '#2a1e1a', '#6a4a2a', '#ff9800', '#ffb74d'),
        (['附录', '信源'], '#1a1a1e', '#505050', '#9e9e9e', '#bdbdbd'),
    ]
    
    text = (h1_text or '') + ' ' + (h2_text or '')
    for keywords, bg, border, accent, heading in color_schemes:
        if any(k in text for k in keywords):
            return bg, border, accent, heading
    
    return '#1e1e28', '#3a3a5a', '#6c63ff', '#8b83ff'


def generate_html(blocks):
    """Generate complete HTML from parsed blocks."""
    
    # Extract title
    title = ''
    for b in blocks:
        if b['type'] == 'h1':
            title = strip_inline_markdown(b['content'])
            break
    
    # Track section structure for colors
    current_h1 = None
    current_h2 = None
    
    section_index = 0
    
    html_buffer = []
    html_buffer.append(f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', 'Noto Sans SC', sans-serif;
    background: #0d0d12;
    color: #e0e0e0;
    line-height: 1.7;
    padding: 20px;
}}
.container {{
    max-width: 920px;
    margin: 0 auto;
    padding: 20px;
}}
/* Header / Hero */
.hero {{
    background: linear-gradient(135deg, #16162a 0%, #1a1a35 50%, #12121e 100%);
    border: 1px solid #2a2a4a;
    border-radius: 16px;
    padding: 48px 36px;
    margin-bottom: 36px;
    text-align: center;
    position: relative;
    overflow: hidden;
}}
.hero::before {{
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle at 30% 50%, rgba(108,99,255,0.05) 0%, transparent 50%);
    pointer-events: none;
}}
.hero h1 {{
    font-size: 28px;
    font-weight: 700;
    color: #f0f0ff;
    margin-bottom: 16px;
    position: relative;
    letter-spacing: 0.5px;
}}
.hero .meta {{
    font-size: 14px;
    color: #8888aa;
    margin-bottom: 8px;
    position: relative;
}}
.hero .purpose {{
    font-size: 13px;
    color: #9999bb;
    line-height: 1.6;
    position: relative;
    max-width: 700px;
    margin: 0 auto;
}}
.hero .badge {{
    display: inline-block;
    background: rgba(108,99,255,0.15);
    color: #8b83ff;
    border: 1px solid rgba(108,99,255,0.3);
    padding: 2px 12px;
    border-radius: 20px;
    font-size: 11px;
    margin-top: 12px;
    position: relative;
}}
/* Section cards */
.section {{
    border-radius: 14px;
    padding: 28px 32px;
    margin-bottom: 28px;
    border: 1px solid;
    position: relative;
}}
.section h2 {{
    font-size: 22px;
    font-weight: 700;
    margin-bottom: 20px;
    padding-bottom: 10px;
    border-bottom: 2px solid rgba(255,255,255,0.08);
    display: flex;
    align-items: center;
    gap: 8px;
}}
.section h3 {{
    font-size: 18px;
    font-weight: 600;
    margin: 24px 0 14px 0;
    padding-left: 12px;
    border-left: 3px solid;
}}
.section h4 {{
    font-size: 16px;
    font-weight: 600;
    margin: 18px 0 10px 0;
    color: #cccce0;
}}
.section p {{
    margin: 10px 0;
    font-size: 14.5px;
    line-height: 1.8;
    color: #c8c8d8;
}}
.section p strong {{
    color: #f0f0ff;
}}
.section hr {{
    border: none;
    border-top: 1px solid rgba(255,255,255,0.06);
    margin: 24px 0;
}}
/* Tables */
.table-wrapper {{
    overflow-x: auto;
    margin: 16px 0;
    border-radius: 10px;
    border: 1px solid rgba(255,255,255,0.06);
}}
table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 13.5px;
    min-width: 500px;
}}
thead {{
    background: rgba(255,255,255,0.06);
}}
th {{
    padding: 12px 14px;
    text-align: left;
    font-weight: 600;
    color: #d0d0e8;
    font-size: 13px;
    letter-spacing: 0.3px;
    white-space: nowrap;
}}
td {{
    padding: 10px 14px;
    border-top: 1px solid rgba(255,255,255,0.04);
    color: #c0c0d0;
    vertical-align: top;
}}
tr:nth-child(even) td {{
    background: rgba(255,255,255,0.02);
}}
tr:hover td {{
    background: rgba(255,255,255,0.04);
}}
td code, th code {{
    background: rgba(255,255,255,0.08);
    padding: 1px 6px;
    border-radius: 4px;
    font-size: 12px;
    font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
}}
/* Code blocks */
.code-block {{
    background: #0a0a0f;
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 10px;
    padding: 18px 20px;
    margin: 16px 0;
    overflow-x: auto;
    position: relative;
}}
.code-block .code-lang {{
    position: absolute;
    top: 8px;
    right: 12px;
    font-size: 11px;
    color: #666;
    text-transform: uppercase;
    letter-spacing: 1px;
}}
.code-block code {{
    font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
    font-size: 13px;
    line-height: 1.7;
    color: #c0c0d0;
    white-space: pre;
}}
/* Lists */
.section ul, .section ol {{
    margin: 10px 0;
    padding-left: 22px;
}}
.section li {{
    margin: 6px 0;
    font-size: 14.5px;
    line-height: 1.7;
    color: #c8c8d8;
}}
.section li strong {{
    color: #e8e8f8;
}}
/* Inline code */
.section code {{
    background: rgba(255,255,255,0.06);
    padding: 1px 6px;
    border-radius: 4px;
    font-size: 13px;
    font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
    color: #d0d0e8;
}}
/* Lists inside tables */
.section td ul, .section td ol {{
    margin: 0;
    padding-left: 16px;
}}
.section td li {{
    font-size: 13px;
    margin: 2px 0;
}}
/* Emoji stars */
.stars {{
    color: #ffd700;
    letter-spacing: 1px;
}}
/* TOC */
.toc-card {{
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 12px;
    padding: 24px 28px;
    margin-bottom: 28px;
}}
.toc-card h2 {{
    font-size: 18px;
    font-weight: 700;
    color: #d0d0e8;
    margin-bottom: 14px;
    border: none;
    padding: 0;
}}
.toc-card ol {{
    padding-left: 20px;
}}
.toc-card li {{
    margin: 6px 0;
    font-size: 14px;
    color: #9999bb;
    list-style-position: outside;
}}
.toc-card li a {{
    color: #8888bb;
    text-decoration: none;
    transition: color 0.2s;
}}
.toc-card li a:hover {{
    color: #bb88ff;
}}
/* Bold lines */
.bold-line {{
    font-weight: 700;
    font-size: 15px;
    color: #e0e0f0;
    margin: 14px 0 8px 0;
    padding: 6px 0;
}}
/* Responsive */
@media (max-width: 640px) {{
    body {{ padding: 12px; }}
    .container {{ padding: 0; }}
    .hero {{ padding: 28px 18px; }}
    .hero h1 {{ font-size: 22px; }}
    .section {{ padding: 20px 16px; }}
    .section h2 {{ font-size: 19px; }}
    .section h3 {{ font-size: 16px; }}
    table {{ font-size: 12.5px; min-width: 400px; }}
    th, td {{ padding: 8px 10px; }}
    .code-block {{ padding: 14px; }}
    .code-block code {{ font-size: 12px; }}
}}
</style>
</head>
<body>
<div class="container">
''')
    
    # Extract metadata
    date_text = ''
    purpose_text = ''
    source_text = ''
    
    for i, b in enumerate(blocks):
        if b['type'] == 'paragraph' and i < 5:
            content = b['content']
            if '日期' in content:
                date_text = content.replace('**日期：**', '').strip()
            if '目的' in content:
                purpose_text = content.replace('**目的：**', '').strip()
            if '数据来源' in content:
                source_text = content.replace('**数据来源：**', '').strip()
    
    # Hero section
    html_buffer.append(f'''<div class="hero">
<h1>{render_inline_markdown(title)}</h1>
''')
    if date_text:
        html_buffer.append(f'<div class="meta">📅 {render_inline_markdown(date_text)}</div>\n')
    if purpose_text:
        html_buffer.append(f'<div class="purpose">🎯 {render_inline_markdown(purpose_text)}</div>\n')
    if source_text:
        html_buffer.append(f'<span class="badge">📊 {render_inline_markdown(source_text)}</span>\n')
    html_buffer.append('</div>\n')
    
    # Track current section colors for h3/h4
    current_bg = '#1e1e28'
    current_border = '#3a3a5a'
    current_accent = '#6c63ff'
    current_heading_c = '#8b83ff'
    
    # Process blocks
    for b in blocks:
        t = b['type']
        
        if t == 'h1':
            current_h1 = b['content']
            current_h2 = None
            section_index += 1
            # h1 already handled as hero, skip if title
            if section_index == 1:
                continue
            bg, border, accent, heading_c = get_section_color(current_h1, current_h2)
            current_bg, current_border, current_accent, current_heading_c = bg, border, accent, heading_c
            html_buffer.append(f'''<div class="section" style="background: {bg}; border-color: {border};">
<h2 style="color: {heading_c};">{render_inline_markdown(b['content'])}</h2>
''')
        
        elif t == 'h2':
            if current_h1 and current_h1 != '国内手游市场调研报告 — 玩法/系统/竞品分析':
                # Check if this is a major section or subsection
                bg, border, accent, heading_c = get_section_color(current_h1, b['content'])
                current_h2 = b['content']
                current_bg, current_border, current_accent, current_heading_c = bg, border, accent, heading_c
                html_buffer.append(f'<h3 style="color: {heading_c}; border-left-color: {accent};">{render_inline_markdown(b["content"])}</h3>\n')
            else:
                current_h2 = b['content']
                bg, border, accent, heading_c = get_section_color(current_h1, b['content'])
                current_bg, current_border, current_accent, current_heading_c = bg, border, accent, heading_c
                html_buffer.append(f'''<div class="section" style="background: {bg}; border-color: {border};">
<h2 style="color: {heading_c};">{render_inline_markdown(b['content'])}</h2>
''')
        
        elif t == 'h3':
            # Use current section's accent color
            html_buffer.append(f'<h4 style="color: {current_accent};">{render_inline_markdown(b["content"])}</h4>\n')
        
        elif t == 'hr':
            html_buffer.append('<hr>\n')
        
        elif t == 'paragraph':
            content = b['content']
            # Check for meta lines (bold at start)
            if content.startswith('**') and '**' in content[2:]:
                html_buffer.append(f'<p>{render_inline_markdown(content)}</p>\n')
            else:
                html_buffer.append(f'<p>{render_inline_markdown(content)}</p>\n')
        
        elif t == 'bold_line':
            html_buffer.append(f'<div class="bold-line">{render_inline_markdown(b["content"])}</div>\n')
        
        elif t == 'list':
            content = b['content']
            lines = content.split('\n')
            # Determine if ordered or unordered
            if re.match(r'^\d+\.', lines[0]):
                html_buffer.append('<ol>\n')
                for line in lines:
                    m = re.match(r'^\d+\.\s+(.*)', line)
                    if m:
                        item_text = render_inline_markdown(m.group(1))
                        # Convert markdown links [text](#anchor) to HTML links
                        item_text = re.sub(r'\[(.+?)\]\((#.+?)\)', r'<a href="\2" style="color: #8888bb; text-decoration: none;">\1</a>', item_text)
                        html_buffer.append(f'<li>{item_text}</li>\n')
                    else:
                        # Continuation or sub-item starting with -
                        m2 = re.match(r'^-\s+(.*)', line)
                        if m2:
                            html_buffer.append(f'<ul><li>{render_inline_markdown(m2.group(1))}</li></ul>\n')
                        else:
                            # Check if it has nested - items
                            stripped = line.strip()
                            if stripped.startswith('-'):
                                m3 = re.match(r'^-\s+(.*)', stripped)
                                if m3:
                                    html_buffer.append(f'<ul><li>{render_inline_markdown(m3.group(1))}</li></ul>\n')
                html_buffer.append('</ol>\n')
            else:
                html_buffer.append('<ul>\n')
                for line in lines:
                    m = re.match(r'^[-*]\s+(.*)', line)
                    if m:
                        html_buffer.append(f'<li>{render_inline_markdown(m.group(1))}</li>\n')
                    else:
                        # Sub-indented content (like continuation)
                        stripped = line.strip()
                        if stripped:
                            html_buffer.append(f'<li style="list-style: none; padding-left: 20px;">{render_inline_markdown(stripped)}</li>\n')
                html_buffer.append('</ul>\n')
        
        elif t == 'table':
            header, data, alignments = parse_table(b['content'])
            if not header:
                continue
            
            html_buffer.append('<div class="table-wrapper"><table>\n<thead><tr>')
            for i, h in enumerate(header):
                align = alignments[i] if i < len(alignments) else 'left'
                html_buffer.append(f'<th style="text-align: {align};">{render_inline_markdown(h)}</th>')
            html_buffer.append('</tr></thead>\n<tbody>\n')
            
            for row in data:
                html_buffer.append('<tr>')
                for i, cell in enumerate(row):
                    align = alignments[i] if i < len(alignments) else 'left'
                    # Convert star emoji markers
                    cell_html = render_inline_markdown(cell)
                    # Replace star ratings like ⭐⭐⭐⭐⭐ with styled spans
                    cell_html = re.sub(r'(⭐{1,5})', lambda m: f'<span class="stars">{m.group(1)}</span>', cell_html)
                    html_buffer.append(f'<td style="text-align: {align};">{cell_html}</td>')
                html_buffer.append('</tr>\n')
            html_buffer.append('</tbody>\n</table></div>\n')
        
        elif t == 'code':
            content = b['content']
            lang = b.get('lang', '')
            # Remove the opening and closing ```
            lines = content.split('\n')
            if lines and lines[0].startswith('```'):
                lines = lines[1:]
            if lines and lines[-1].strip() == '```':
                lines = lines[:-1]
            code_text = '\n'.join(lines)
            html_buffer.append(f'<div class="code-block"><span class="code-lang">{lang}</span><code>{code_text}</code></div>\n')
    
    # Close any open section
    html_buffer.append('</div>\n')
    
    # Close container and body
    html_buffer.append('''</div>
</body>
</html>''')
    
    return ''.join(html_buffer)


def main():
    input_path = '/mnt/c/AI/hermes/调研/2026-05-28-首轮调研报告.md'
    output_path = '/mnt/c/AI/hermes/调研/2026-05-28-首轮调研报告.html'
    
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    blocks = parse_markdown(content)
    html = generate_html(blocks)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f'✅ HTML generated: {output_path}')
    print(f'   Size: {len(html)} bytes')

if __name__ == '__main__':
    main()
