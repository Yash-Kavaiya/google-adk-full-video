#!/usr/bin/env python3
"""
build_deck.py -- compile a Triad Beamer deck and report problems usefully.

Why this exists: `latexmk` prints hundreds of lines and buries the one line
that matters. This runs the compile, then extracts only the actionable
diagnostics (errors, then layout warnings), and renders page previews so the
result can actually be looked at rather than assumed correct.

Usage:
    python3 build_deck.py main.tex
    python3 build_deck.py main.tex --preview          # render PNGs of pages
    python3 build_deck.py main.tex --preview --pages 1,4,7
    python3 build_deck.py main.tex --engine xelatex   # if using system fonts

Exit code is 0 on a successful build, 1 otherwise.
"""

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

# Errors begin with "! " in TeX logs. These are fatal.
ERROR_RE = re.compile(r"^! (.+)$", re.M)
# The line number of the failure is reported as "l.<n>".
LINE_RE = re.compile(r"^l\.(\d+)(.*)$", re.M)
# Overfull boxes mean content is spilling past the slide edge.
OVERFULL_RE = re.compile(r"^(Overfull \\[hv]box .+?)$", re.M)
# Missing references resolve on the second pass; only report if still unresolved.
UNDEFINED_RE = re.compile(r"Reference `([^']+)' on page (\d+) undefined", re.M)


def run(cmd, cwd):
    return subprocess.run(
        cmd, cwd=cwd, capture_output=True, text=True, errors="replace"
    )


def find_theme(texfile: Path) -> bool:
    """The theme must sit beside the .tex file or be installed in TEXMF."""
    if (texfile.parent / "beamerthemeTriad.sty").exists():
        return True
    probe = shutil.which("kpsewhich")
    if probe:
        r = run([probe, "beamerthemeTriad.sty"], texfile.parent)
        if r.stdout.strip():
            return True
    return False


def compile_deck(texfile: Path, engine: str) -> tuple[bool, str]:
    """
    Run latexmk if available (it handles the multi-pass logic on its own),
    otherwise fall back to running the engine twice by hand. Two passes are
    required: the frame counter and the progress bar both read totals that
    only exist in the .aux file after pass one.
    """
    cwd = texfile.parent
    if shutil.which("latexmk"):
        cmd = [
            "latexmk",
            f"-{engine}",
            "-interaction=nonstopmode",
            "-file-line-error",
            texfile.name,
        ]
        run(cmd, cwd)
    else:
        for _ in range(2):
            run([engine, "-interaction=nonstopmode",
                 "-file-line-error", texfile.name], cwd)

    logfile = cwd / (texfile.stem + ".log")
    log = logfile.read_text(errors="replace") if logfile.exists() else ""
    pdf = cwd / (texfile.stem + ".pdf")
    return pdf.exists(), log


def report(log: str) -> list[str]:
    """Pull only the diagnostics worth a human's attention."""
    out = []

    errors = ERROR_RE.findall(log)
    if errors:
        out.append("ERRORS")
        lines = LINE_RE.findall(log)
        for i, err in enumerate(errors[:12]):
            loc = f"  (near line {lines[i][0]})" if i < len(lines) else ""
            out.append(f"  ! {err.strip()}{loc}")

    over = OVERFULL_RE.findall(log)
    if over:
        out.append("")
        out.append(f"LAYOUT WARNINGS ({len(over)} overfull boxes)")
        out.append("  Content is spilling past the slide edge. Usually means "
                   "too much material on one frame -- split it.")
        for o in over[:8]:
            out.append(f"  - {o.strip()}")

    undef = UNDEFINED_RE.findall(log)
    if undef:
        out.append("")
        out.append("UNRESOLVED REFERENCES")
        for ref, page in undef[:8]:
            out.append(f"  - `{ref}' on page {page}")

    return out


def preview(pdf: Path, pages: str | None, dpi: int = 110) -> list[Path]:
    """Render pages to PNG so the layout can be inspected, not assumed."""
    if not shutil.which("pdftoppm"):
        print("  (pdftoppm not available -- skipping preview)")
        return []
    outdir = pdf.parent / "preview"
    outdir.mkdir(exist_ok=True)
    made = []
    if pages:
        for p in [x.strip() for x in pages.split(",") if x.strip()]:
            run(["pdftoppm", "-png", "-r", str(dpi), "-f", p, "-l", p,
                 pdf.name, f"preview/page"], pdf.parent)
    else:
        run(["pdftoppm", "-png", "-r", str(dpi), pdf.name, "preview/page"],
            pdf.parent)
    made = sorted(outdir.glob("page*.png"))
    return made


def main():
    ap = argparse.ArgumentParser(description="Compile a Triad Beamer deck.")
    ap.add_argument("texfile")
    ap.add_argument("--engine", default="pdflatex",
                    choices=["pdflatex", "xelatex", "lualatex"])
    ap.add_argument("--preview", action="store_true",
                    help="render page PNGs for visual inspection")
    ap.add_argument("--pages", default=None,
                    help="comma-separated pages to preview, e.g. 1,4,7")
    args = ap.parse_args()

    tex = Path(args.texfile).resolve()
    if not tex.exists():
        print(f"No such file: {tex}")
        return 1

    if not find_theme(tex):
        print("beamerthemeTriad.sty not found next to the .tex file or in "
              "TEXMF.\nCopy it into the deck directory before building.")
        return 1

    print(f"Building {tex.name} with {args.engine} ...")
    ok, log = compile_deck(tex, args.engine)

    diagnostics = report(log)

    if not ok:
        print("\nBUILD FAILED -- no PDF produced.\n")
        print("\n".join(diagnostics) or "  (no '!' errors found; check the .log)")
        return 1

    pdf = tex.with_suffix(".pdf")
    pages = "?"
    if shutil.which("pdfinfo"):
        r = run(["pdfinfo", pdf.name], tex.parent)
        m = re.search(r"Pages:\s+(\d+)", r.stdout)
        if m:
            pages = m.group(1)

    print(f"\nBuilt {pdf.name} -- {pages} pages.")
    if diagnostics:
        print()
        print("\n".join(diagnostics))
    else:
        print("No errors, no overfull boxes.")

    if args.preview:
        imgs = preview(pdf, args.pages)
        if imgs:
            print(f"\nRendered {len(imgs)} preview image(s) in "
                  f"{pdf.parent / 'preview'}/")
            print("Look at them before declaring the deck finished.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
