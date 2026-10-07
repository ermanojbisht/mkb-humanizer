"""Batch front end for hz. Rewrites supported files into a separate directory."""
from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys


SUPPORTED = {".txt", ".md", ".markdown", ".docx"}


def _inside(path: Path, directory: Path) -> bool:
    try:
        path.resolve().relative_to(directory.resolve())
        return True
    except ValueError:
        return False


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="humanize-batch", description="Rewrite text, Markdown, and DOCX files recursively.")
    p.add_argument("input", help="input file or directory")
    p.add_argument("output", help="separate output file or directory")
    p.add_argument("--model", help="installed Ollama model name; otherwise hz auto-detects humanizer")
    p.add_argument("--ollama-url", help="Ollama address, such as http://127.0.0.1:11434")
    p.add_argument("--overwrite", action="store_true", help="replace existing output files")
    p.add_argument("--report-dir", help="write one JSON quality report per output file")
    p.add_argument("--retries", type=int, default=1, help="extra attempts for a flagged piece (default 1)")
    a = p.parse_args(argv)

    src, dst = Path(a.input).expanduser(), Path(a.output).expanduser()
    if not src.exists():
        p.error(f"input does not exist: {src}")
    report_root = Path(a.report_dir).expanduser() if a.report_dir else None
    if src.is_file():
        jobs = [(src, dst)]
    else:
        if dst.exists() and dst.is_file():
            p.error("directory input requires a directory output")
        excluded = [p for p in (dst, report_root) if p is not None and _inside(p, src)]
        jobs = [(f, dst / f.relative_to(src)) for f in sorted(src.rglob("*"))
                if f.is_file() and f.suffix.lower() in SUPPORTED
                and not any(_inside(f, directory) for directory in excluded)]
    if not jobs:
        print("humanize-batch: no .txt, .md, .markdown, or .docx files found", file=sys.stderr)
        return 0

    done = skipped = failed = 0
    for i, (infile, outfile) in enumerate(jobs, 1):
        if infile.resolve() == outfile.resolve():
            print(f"humanize-batch: refusing to overwrite input: {infile}", file=sys.stderr)
            failed += 1
            continue
        if outfile.exists() and not a.overwrite:
            print(f"[{i}/{len(jobs)}] skip existing {outfile}", file=sys.stderr)
            skipped += 1
            continue
        outfile.parent.mkdir(parents=True, exist_ok=True)
        cmd = [sys.executable, "-m", "humanizer.hz", str(infile), "-o", str(outfile),
               "--retries", str(a.retries)]
        if a.model:
            cmd += ["--ollama-model", a.model]
        if a.ollama_url:
            cmd += ["--ollama-url", a.ollama_url]
        report = None
        if report_root:
            rel = outfile.name if src.is_file() else str(outfile.relative_to(dst))
            report = report_root / (rel + ".json")
            report.parent.mkdir(parents=True, exist_ok=True)
            cmd += ["--json", "--quiet"]
        print(f"[{i}/{len(jobs)}] {infile} -> {outfile}", file=sys.stderr)
        if report:
            with report.open("w", encoding="utf-8") as fh:
                result = subprocess.run(cmd, stdout=fh)
        else:
            result = subprocess.run(cmd)
        if result.returncode == 0:
            done += 1
        else:
            failed += 1

    print(f"humanize-batch: {done} written, {skipped} skipped, {failed} failed", file=sys.stderr)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
