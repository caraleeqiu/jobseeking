"""把简历 Markdown 渲染成排版正确的 PDF。"""
import sys, re, markdown
from weasyprint import HTML

def fix_bullets(md):
    lines = md.split('\n'); fixed = []
    for line in lines:
        s = line.lstrip()
        is_li = s.startswith('- ') or (len(s) > 1 and s[0].isdigit() and s[1] in '.)')
        if is_li and fixed and fixed[-1].strip() != '':
            prev = fixed[-1].lstrip()
            prev_is_li = prev.startswith('- ') or (len(prev) > 1 and prev[0].isdigit() and prev[1] in '.)')
            if not prev_is_li: fixed.append('')
        fixed.append(line)
    return '\n'.join(fixed)

CSS = """
@page { size: A4; margin: 1.4cm 1.5cm; }
body { font-family: 'WenQuanYi Zen Hei', sans-serif; font-size: 10.5px; line-height: 1.5; color: #1a1a1a; }
h1 { font-size: 22px; margin: 0 0 2px 0; }
h2 { font-size: 13px; margin: 14px 0 6px 0; padding-bottom: 3px; border-bottom: 1.5px solid #333; }
h3 { font-size: 11.5px; margin: 8px 0 2px 0; }
p { margin: 3px 0; }
ul, ol { margin: 3px 0 6px 0; padding-left: 18px; }
li { margin: 2px 0; }
em { color: #555; font-style: italic; }
strong { color: #000; }
hr { border: none; border-top: 1px solid #ccc; margin: 6px 0; }
.job { font-size: 12px; font-weight: bold; color: #000; margin: 13px 0 0 0; padding: 3px 7px; background: #f0f0f0; border-left: 3px solid #333; }
.sub { font-size: 9.5px; color: #777; font-style: italic; margin: 1px 0 4px 0; }
.phase { font-size: 10.5px; font-weight: bold; color: #1a1a1a; margin: 7px 0 2px 0; padding-left: 6px; border-left: 3px solid #999; }
"""

def style_blocks(html):
    html = re.sub(r'<p><strong>([^<]+)</strong>\s*<em>([^<]+)</em></p>', r'<div class="job">\1</div><div class="sub">\2</div>', html)
    html = re.sub(r'<p><strong>([^<]+)</strong></p>', r'<div class="phase">\1</div>', html)
    return html

def main():
    inp, outp = sys.argv[1], sys.argv[2]
    with open(inp, encoding='utf-8') as f: md = f.read()
    md = fix_bullets(md)
    html = markdown.markdown(md, extensions=['extra', 'sane_lists'])
    html = style_blocks(html)
    html = f"<html><head><meta charset='utf-8'><style>{CSS}</style></head><body>{html}</body></html>"
    HTML(string=html).write_pdf(outp)
    print('li count:', html.count('<li>')); print('written:', outp)

if __name__ == '__main__': main()
