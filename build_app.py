"""Build the final single-file index.html by inlining italy_clean.svg into the template."""
from pathlib import Path

with open('italy_clean.svg', 'r', encoding='utf-8') as f:
    svg = f.read()

with open('app_template.html', 'r', encoding='utf-8') as f:
    template = f.read()

result = template.replace('<!-- INLINE_SVG -->', svg)

Path('index.html').write_text(result, encoding='utf-8')
print(f"index.html size: {len(result)} bytes ({len(result)/1024:.1f} KB)")
