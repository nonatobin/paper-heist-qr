#!/usr/bin/env python3
import csv, re, html, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
DATA = DOCS / "data" / "redirects.csv"
OUT_R = DOCS / "r"

def safe_slug(s: str) -> str:
    s = (s or "").strip().lower()
    s = re.sub(r"[^a-z0-9\-]+", "-", s)
    s = re.sub(r"-{2,}", "-", s).strip("-")
    if not s:
        raise ValueError("Empty slug")
    return s

def write_redirect(slug: str, title: str, dest: str) -> None:
    folder = OUT_R / slug
    folder.mkdir(parents=True, exist_ok=True)
    now = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    body = f"""<!doctype html><html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="refresh" content="0; url={html.escape(dest, quote=True)}">
<title>{html.escape(title)} → Redirect</title>
</head><body>
<h1>Redirecting…</h1>
<p><strong>{html.escape(title)}</strong></p>
<p>If not redirected, click: <a href="{html.escape(dest, quote=True)}">{html.escape(dest)}</a></p>
<p style="color:#666;font-size:0.9rem;">Last built: {now}</p>
<script>window.location.replace({dest!r});</script>
</body></html>"""
    (folder / "index.html").write_text(body, encoding="utf-8")

def write_index(items):
    now = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    lis = "\n".join([f'<li><a href="r/{it["slug"]}/">{html.escape(it["title"])}</a></li>' for it in items])
    (DOCS / "index.html").write_text(
        f'<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>QR Redirect Hub</title></head>'
        f'<body><h1>QR Redirect Hub</h1><ul>{lis}</ul><p style="color:#666;font-size:0.9rem;">Last built: {now}</p></body></html>',
        encoding="utf-8"
    )

def main():
    items = []
    with DATA.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            slug = safe_slug(row.get("slug",""))
            title = (row.get("title","") or "").strip()
            dest = (row.get("destination_url","") or "").strip()
            if title and dest:
                items.append({"slug": slug, "title": title, "destination_url": dest})
    if not items:
        raise SystemExit("No valid rows in redirects.csv")
    OUT_R.mkdir(parents=True, exist_ok=True)
    for it in items:
        write_redirect(it["slug"], it["title"], it["destination_url"])
    write_index(items)
    print(f"Built {len(items)} redirects in {DOCS}")

if __name__ == "__main__":
    main()
