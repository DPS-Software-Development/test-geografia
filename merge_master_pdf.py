"""Merge per-page PDFs from extracted chapter ZIPs into one master PDF, in book order."""
import json
import sys
from pathlib import Path
from pypdf import PdfReader, PdfWriter

ROOT = Path(__file__).parent
SRC = ROOT / "regioni-pdf-source"
EXTRACTED = SRC / "extracted"
ORDER_FILE = SRC / "chapter-order.json"
MASTER = SRC / "master.pdf"


def main():
    if not EXTRACTED.exists():
        print(f"Missing: {EXTRACTED}", file=sys.stderr)
        sys.exit(1)
    if not ORDER_FILE.exists():
        print(f"Missing: {ORDER_FILE}", file=sys.stderr)
        sys.exit(1)

    order = json.loads(ORDER_FILE.read_text(encoding="utf-8"))

    # Build map: chapter_id -> path to PDF
    pdf_map = {}
    for pdf in EXTRACTED.rglob("*.pdf"):
        try:
            cid = int(pdf.stem)
            pdf_map[cid] = pdf
        except ValueError:
            pass
    print(f"Found {len(pdf_map)} per-page PDFs in {EXTRACTED}")

    writer = PdfWriter()
    added = 0
    skipped = 0
    for entry in order:
        cid = entry["id"]
        if cid in pdf_map:
            try:
                reader = PdfReader(str(pdf_map[cid]))
                for p in reader.pages:
                    writer.add_page(p)
                added += 1
            except Exception as e:
                print(f"  ! errore lettura {cid}: {e}")
                skipped += 1
        else:
            skipped += 1

    print(f"Aggiunti: {added}  /  Saltati (no PDF): {skipped}")
    with open(MASTER, "wb") as f:
        writer.write(f)
    print(f"Master PDF: {MASTER} ({MASTER.stat().st_size//1024} KB, {len(writer.pages)} pagine)")


if __name__ == "__main__":
    main()
