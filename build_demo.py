import re
from pathlib import Path

root = Path(__file__).resolve().parents[1]
dist = root / "frontend/dist"
html = (dist / "index.html").read_text()
html = re.sub(
    r'<script[^>]+src="([^"]+)"[^>]*></script>',
    lambda m: (
        '<script type="module">' + (dist / m[1].lstrip("/")).read_text() + "</script>"
    ),
    html,
)
html = re.sub(
    r'<link[^>]+href="([^"]+\.css)"[^>]*>',
    lambda m: "<style>" + (dist / m[1].lstrip("/")).read_text() + "</style>",
    html,
)
# Local file auto-selects demo; HTTP delivery must select demo explicitly.
html = html.replace(
    "<head>",
    '<head><script>if(location.protocol!=="file:"&&!location.search.includes("demo"))location.search="demo=1";</script>',
)
(root / "demo/index.html").write_text(html)
