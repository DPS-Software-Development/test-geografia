"""
Split a master PDF (downloaded from Hub Scuola) into 20 per-region PDFs.

Reads .claude/page_map.json which contains URL page numbers for each region.
The URL page → PDF page offset can be tuned via --offset (default 0; if PDF
starts with cover/index pages, offset of -2 typically matches book page numbers).

Usage:
    python split_pdf_by_region.py master.pdf
    python split_pdf_by_region.py master.pdf --offset -2
    python split_pdf_by_region.py master.pdf --offset -2 --out regioni-pdf/
"""
import argparse
import json
import sys
from pathlib import Path

try:
    from pypdf import PdfReader, PdfWriter
except ImportError:
    print("Need pypdf:  pip install pypdf", file=sys.stderr)
    sys.exit(1)


def split(master_path: Path, page_map_path: Path, out_dir: Path, offset: int):
    if not master_path.exists():
        print(f"Master PDF not found: {master_path}", file=sys.stderr)
        sys.exit(1)
    page_map = json.loads(page_map_path.read_text(encoding="utf-8"))
    reader = PdfReader(str(master_path))
    total_pages = len(reader.pages)
    print(f"Master PDF: {master_path.name} ({total_pages} pagine)")
    out_dir.mkdir(parents=True, exist_ok=True)

    for region in page_map["regions"]:
        idx = region["idx"]
        rid = region["id"]
        url_pages = region["url_pages"]
        # URL page → PDF page (1-indexed) with offset
        pdf_pages = [u + offset for u in url_pages]
        # Filter valid + dedup + sort
        pdf_pages = sorted({p for p in pdf_pages if 1 <= p <= total_pages})
        if not pdf_pages:
            print(f"  ! {rid}: nessuna pagina valida (offset={offset})")
            continue

        writer = PdfWriter()
        for p in pdf_pages:
            writer.add_page(reader.pages[p - 1])  # pypdf is 0-indexed

        out_file = out_dir / f"{idx:02d}_{rid}.pdf"
        with open(out_file, "wb") as f:
            writer.write(f)
        print(f"  [OK]{idx:02d}_{rid}.pdf  ({len(pdf_pages)} pagg.: {pdf_pages})")

    # Italy global pages too
    if "italy_global_pages" in page_map:
        ig = page_map["italy_global_pages"]
        if "url_pages" in ig:
            pdf_pages = sorted({u + offset for u in ig["url_pages"] if 1 <= u + offset <= total_pages})
            if pdf_pages:
                writer = PdfWriter()
                for p in pdf_pages:
                    writer.add_page(reader.pages[p - 1])
                out_file = out_dir / "00_italia-generale.pdf"
                with open(out_file, "wb") as f:
                    writer.write(f)
                print(f"  [OK]00_italia-generale.pdf  ({len(pdf_pages)} pagg.)")

    print(f"\nFatto. Output in: {out_dir}/")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("master", type=Path, help="The downloaded master PDF")
    p.add_argument("--offset", type=int, default=0,
                   help="Offset to apply to URL pages → PDF pages (try -2 if PDF starts with cover)")
    p.add_argument("--map", type=Path, default=Path(".claude/page_map.json"),
                   help="Path to page_map.json (default: .claude/page_map.json)")
    p.add_argument("--out", type=Path, default=Path("regioni-pdf"),
                   help="Output directory (default: regioni-pdf/)")
    args = p.parse_args()
    split(args.master, args.map, args.out, args.offset)


if __name__ == "__main__":
    main()
