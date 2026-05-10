"""Convert grouped screenshots into one A4 PDF per Italian region."""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "--quiet", "pillow"]
    )
    from PIL import Image  # noqa: E402

# A4 at 150 DPI -> good print quality without huge files.
DPI = 150
A4_PX = (int(8.27 * DPI), int(11.69 * DPI))  # 1240 x 1754
NAME_RE = re.compile(r"^(\d+)_([^_]+(?:-[^_]+)*)_p(\d+)\.(png|jpe?g)$", re.IGNORECASE)


def regroup(folder: Path, pattern: re.Pattern = NAME_RE) -> dict:
    """Group image files in *folder* by region, sorted by page number.

    Returns a dict ordered by region index: {(idx, region_id): [Path, ...]}.
    """
    groups: dict[tuple[int, str], list[tuple[int, Path]]] = defaultdict(list)
    for f in folder.iterdir():
        if not f.is_file():
            continue
        m = pattern.match(f.name)
        if not m:
            continue
        idx, region, page, _ext = m.groups()
        groups[(int(idx), region)].append((int(page), f))
    ordered = {}
    for key in sorted(groups):
        ordered[key] = [p for _, p in sorted(groups[key])]
    return ordered


def fit_to_a4(img: Image.Image) -> Image.Image:
    """Scale *img* to fit A4 keeping aspect ratio; pad with white margins."""
    img = img.convert("RGB")
    iw, ih = img.size
    pw, ph = A4_PX
    ratio = min(pw / iw, ph / ih)
    new = img.resize((max(1, int(iw * ratio)), max(1, int(ih * ratio))), Image.LANCZOS)
    canvas = Image.new("RGB", A4_PX, "white")
    canvas.paste(new, ((pw - new.width) // 2, (ph - new.height) // 2))
    return canvas


def build_pdf(images: list[Path], out_path: Path) -> None:
    pages = [fit_to_a4(Image.open(p)) for p in images]
    pages[0].save(
        out_path,
        save_all=True,
        append_images=pages[1:],
        format="PDF",
        resolution=DPI,
    )


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--src", default="regioni-screens", type=Path)
    ap.add_argument("--dst", default="regioni-pdf", type=Path)
    args = ap.parse_args()

    if not args.src.is_dir():
        print(f"[!] Cartella sorgente non trovata: {args.src}", file=sys.stderr)
        return 1
    groups = regroup(args.src)
    if not groups:
        print(f"[!] Nessuna immagine valida in {args.src}", file=sys.stderr)
        return 1

    args.dst.mkdir(parents=True, exist_ok=True)
    for (idx, region), files in groups.items():
        out = args.dst / f"{idx:02d}_{region}.pdf"
        build_pdf(files, out)
        print(f"  -> {out.name}  ({len(files)} pagine)")
    print(f"[OK] Regioni processate: {len(groups)} | PDF creati: {len(groups)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
