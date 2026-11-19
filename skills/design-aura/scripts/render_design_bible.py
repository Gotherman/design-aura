#!/usr/bin/env python3
"""Gera o papel da Biblia de Design sem limite de paginas.

Le DESIGN-BIBLE.md e escreve DESIGN-BIBLE.html. Se houver Chromium,
tambem escreve DESIGN-BIBLE.pdf em A4 retrato, com quantas paginas
o conteudo precisar. Nada e cortado por altura fixa.
"""
import argparse
import html
import re
import shutil
import subprocess
import sys
from pathlib import Path


def inline(text: str) -> str:
    escaped = html.escape(text)
    escaped = re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", escaped)
    return escaped


def markdown_to_body(md: str) -> str:
    lines = md.replace("\r\n", "\n").split("\n")
    out: list[str] = []
    i = 0
    paragraph: list[str] = []

    def flush_paragraph() -> None:
        if paragraph:
            out.append(f"<p>{inline(' '.join(paragraph))}</p>")
            paragraph.clear()

    while i < len(lines):
        line = lines[i]
        if line.startswith("```"):
            flush_paragraph()
            buff = []
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                buff.append(html.escape(lines[i]))
                i += 1
            out.append("<pre><code>" + "\n".join(buff) + "</code></pre>")
            i += 1
            continue
        if line.startswith("|") and i + 1 < len(lines) and re.match(r"^\|?\s*-+", lines[i + 1]):
            flush_paragraph()
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                rows.append(cells)
                i += 1
            head, body = rows[0], rows[2:]
            table = ["<table><thead><tr>"]
            table.extend(f"<th>{inline(cell)}</th>" for cell in head)
            table.append("</tr></thead><tbody>")
            for row in body:
                table.append("<tr>" + "".join(f"<td>{inline(cell)}</td>" for cell in row) + "</tr>")
            table.append("</tbody></table>")
            out.append("".join(table))
            continue
        if line.startswith("#"):
            flush_paragraph()
            level = min(len(line) - len(line.lstrip("#")), 3)
            title = line.lstrip("#").strip()
            out.append(f"<h{level}>{inline(title)}</h{level}>")
            i += 1
            continue
        if re.match(r"^(\s*)[-*] ", line):
            flush_paragraph()
            out.append("<ul>")
            while i < len(lines) and re.match(r"^(\s*)[-*] ", lines[i]):
                item = re.sub(r"^(\s*)[-*] ", "", lines[i])
                out.append(f"<li>{inline(item)}</li>")
                i += 1
            out.append("</ul>")
            continue
        if line.strip() == "":
            flush_paragraph()
            i += 1
            continue
        if line.startswith(">"):
            flush_paragraph()
            out.append(f"<blockquote><p>{inline(line.lstrip('> ').strip())}</p></blockquote>")
            i += 1
            continue
        paragraph.append(line.strip())
        i += 1
    flush_paragraph()
    return "\n".join(out)


PAPER_CSS = """
@page { size: A4 portrait; margin: 16mm 14mm 18mm; }
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; }
body {
  color: #142033;
  background: #f4f1ea;
  font-family: "Iowan Old Style", Palatino, "Palatino Linotype", Georgia, serif;
  font-size: 11.5pt;
  line-height: 1.45;
}
main { max-width: 178mm; margin: 0 auto; }
h1 { font-size: 22pt; line-height: 1.15; letter-spacing: -0.02em; margin: 0 0 8mm; }
h2 { font-size: 15pt; line-height: 1.2; margin: 8mm 0 3mm; break-after: avoid; }
h3 { font-size: 12.5pt; margin: 5mm 0 2mm; break-after: avoid; }
p, li { orphans: 3; widows: 3; }
ul { margin: 0 0 4mm; padding-left: 5mm; }
li { margin: 0.6mm 0; }
code, pre { font-family: "JetBrains Mono", ui-monospace, monospace; font-size: 9pt; }
code { background: #e7e1d6; padding: 0 1.5mm; }
pre, table, blockquote { break-inside: avoid; }
pre { white-space: pre-wrap; background: #172033; color: #f3f6fa; padding: 4mm; }
table { width: 100%; border-collapse: collapse; margin: 0 0 5mm; }
th, td { border-bottom: 0.3mm solid #c8bfb2; text-align: left; vertical-align: top; padding: 1.6mm 2mm; }
th { font-size: 9pt; letter-spacing: 0.02em; }
blockquote { margin: 0 0 4mm; padding-left: 4mm; border-left: 0.8mm solid #c2410c; color: #3d4b5c; }
"""


def build_html(md: str, title: str) -> str:
    body = markdown_to_body(md)
    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<title>{html.escape(title)}</title>
<style>{PAPER_CSS}</style>
</head>
<body>
<main>
{body}
</main>
</body>
</html>
"""


def find_browser() -> str | None:
    for name in ("google-chrome", "chromium", "chromium-browser"):
        found = shutil.which(name)
        if found:
            return found
    return None


def write_pdf(browser: str, html_path: Path, pdf_path: Path) -> None:
    subprocess.run(
        [
            browser,
            "--headless=new",
            "--disable-gpu",
            "--no-sandbox",
            f"--print-to-pdf={pdf_path}",
            "--no-pdf-header-footer",
            html_path.resolve().as_uri(),
        ],
        check=True,
        capture_output=True,
        text=True,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Renderiza a Biblia de Design em papel HTML e PDF sem corte.")
    parser.add_argument("markdown", help="DESIGN-BIBLE.md")
    parser.add_argument("--out-dir", default=".", help="Pasta de saida")
    args = parser.parse_args()

    source = Path(args.markdown)
    if not source.exists():
        print(f"Arquivo nao encontrado: {source}", file=sys.stderr)
        sys.exit(1)
    text = source.read_text(encoding="utf-8")
    title = "Biblia de Design"
    for line in text.splitlines():
        if line.startswith("# "):
            title = line[2:].strip()
            break

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    html_path = out_dir / "DESIGN-BIBLE.html"
    pdf_path = out_dir / "DESIGN-BIBLE.pdf"
    html_path.write_text(build_html(text, title), encoding="utf-8")
    print(f"Papel HTML: {html_path}")

    browser = find_browser()
    if not browser:
        print("Chromium nao encontrado. O HTML esta pronto para imprimir em PDF, sem limite de paginas.", file=sys.stderr)
        sys.exit(0)
    try:
        write_pdf(browser, html_path, pdf_path)
    except subprocess.CalledProcessError as exc:
        print(f"Falha ao gerar PDF: {exc.stderr}", file=sys.stderr)
        sys.exit(1)
    print(f"PDF sem corte: {pdf_path}")


if __name__ == "__main__":
    main()
