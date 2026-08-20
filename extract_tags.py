#!/bin/python
import zipfile
import xml.etree.ElementTree as ET
import sys
import os
import re
import csv
import shutil
import argparse
from pathlib import Path


# Trailing "_N<n>" is only Word's way of keeping duplicate bookmark names apart
# (CRA_Art_11 / CRA_Art_11_N2 point at the same control), so it is stripped.
COLLISION_SUFFIX = re.compile(r"_N\d+$")


def normalize_control(name):
    """Drop the technical collision suffix so repeated references collapse into one control."""
    return COLLISION_SUFFIX.sub("", name)


def extract_tags(docx_path):
    # Word XML namespace
    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    tags = set()

    try:
        with zipfile.ZipFile(docx_path, "r") as docx:
            # Parse document.xml and any headers/footers where tags might be located
            for item in docx.namelist():
                if item.startswith("word/") and item.endswith(".xml"):
                    xml_content = docx.read(item)
                    try:
                        tree = ET.fromstring(xml_content)
                        # Find all bookmarkStart elements
                        for bookmark in tree.findall(".//w:bookmarkStart", ns):
                            name = bookmark.get(f"{{{ns['w']}}}name")
                            # "Hidden" bookmarks in Word start with an underscore (e.g. _GoBack, _Toc...)
                            if name and not name.startswith("_"):
                                tags.add(normalize_control(name))
                    except ET.ParseError:
                        continue
    except Exception as e:
        print(f"Error reading docx file '{docx_path}': {e}", file=sys.stderr)
        return None

    return sorted(list(tags))


def find_docx_files(directory):
    """Recursively find all .docx files, skipping temporary Word lock files (~$...)."""
    root = Path(directory)
    files = [p for p in root.rglob("*.docx") if not p.name.startswith("~$")]
    return sorted(files)


def collect_docx_files(paths):
    """Expand the given paths (files and/or directories) into a list of .docx files.

    Directories are scanned recursively; files are taken as-is. Duplicates that
    result from overlapping arguments (e.g. shell globs) are removed.
    """
    files = []
    for raw in paths:
        path = Path(raw)
        if path.is_dir():
            files.extend(find_docx_files(path))
        elif path.is_file():
            if path.suffix.lower() != ".docx" or path.name.startswith("~$"):
                print(f"Skipping non-docx file: {raw}", file=sys.stderr)
                continue
            files.append(path)
        else:
            print(f"Warning: path not found, skipping: {raw}", file=sys.stderr)

    return sorted({p.resolve() for p in files})


def common_base(files):
    """Directory all documents are relative to, used for the CSV column labels."""
    if not files:
        return None
    if len(files) == 1:
        return files[0].parent
    return Path(os.path.commonpath([str(f) for f in files]))


def iter_with_progress(items, label="Progress", stream=sys.stderr):
    """Yield items while drawing a single-line progress bar (only on a TTY)."""
    total = len(items)
    show = total > 0 and stream.isatty()

    def draw(done, current=""):
        bar_width = 28
        filled = int(bar_width * done / total)
        bar = "#" * filled + "." * (bar_width - filled)
        pct = 100 * done // total
        line = f"{label} [{bar}] {pct:3d}% {done}/{total} {current}"
        max_len = max(20, shutil.get_terminal_size((80, 24)).columns - 1)
        stream.write("\r" + line[:max_len].ljust(max_len))
        stream.flush()

    for i, item in enumerate(items):
        if show:
            draw(i, getattr(item, "name", str(item)))
        yield item

    if show:
        draw(total)
        stream.write("\n")
        stream.flush()


def build_matrix(files, base):
    """Extract tags from every document and build a control-to-document mapping.

    Documents without any control tag are left out entirely - they show up
    neither as a matrix column nor in the summary.

    Returns a tuple (doc_tags, all_controls) where:
      - doc_tags: dict mapping document path (relative to base) -> set of controls
      - all_controls: sorted list of every control found across all documents
    """
    doc_tags = {}
    all_controls = set()

    for docx_path in iter_with_progress(files, "Extracting tags"):
        tags = extract_tags(docx_path)
        if not tags:
            # Unreadable (None) or simply untagged - skip either way.
            continue
        try:
            rel = docx_path.relative_to(base).as_posix()
        except ValueError:
            rel = docx_path.as_posix()
        doc_tags[rel] = set(tags)
        all_controls.update(tags)

    return doc_tags, sorted(all_controls)


def write_matrix_csv(doc_tags, all_controls, output_path, delimiter=";", mark="X"):
    """Write a matrix: rows = controls, columns = documents."""
    documents = sorted(doc_tags.keys())
    with open(output_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f, delimiter=delimiter)
        # Header row
        writer.writerow(["Control"] + documents)
        # One row per control
        for control in all_controls:
            row = [control]
            for doc in documents:
                row.append(mark if control in doc_tags[doc] else "")
            writer.writerow(row)


def run_single(path):
    tags = extract_tags(path)
    if tags is None:
        sys.exit(1)
    if not tags:
        print("No tags found.")
    else:
        print(f"Found {len(tags)} tags:")
        for tag in tags:
            print(f"- {tag}")


def run_matrix(paths, output_path, delimiter):
    files = collect_docx_files(paths)

    if not files:
        print(f"No .docx files found in: {', '.join(paths)}")
        sys.exit(1)

    base = common_base(files)
    doc_tags, all_controls = build_matrix(files, base)

    if not doc_tags:
        print(f"No controls found in {len(files)} scanned document(s).")
        sys.exit(1)

    write_matrix_csv(doc_tags, all_controls, output_path, delimiter=delimiter)

    skipped = len(files) - len(doc_tags)
    print(
        f"Scanned {len(files)} document(s), found {len(all_controls)} distinct control(s) "
        f"in {len(doc_tags)} tagged document(s)."
    )
    if skipped:
        print(f"Ignored {skipped} document(s) without controls.")
    for doc in sorted(doc_tags.keys()):
        print(f"  - {doc}: {len(doc_tags[doc])} control(s)")
    print(f"\nMatrix written to: {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extract non-hidden document tags (controls/bookmarks) from Word documents. "
        "Pass a single .docx file to list its tags, or one or more directories "
        "(e.g. via a shell glob like 'normen/*') to build a control-to-document "
        "matrix by recursively scanning all .docx files."
    )
    parser.add_argument(
        "paths",
        nargs="+",
        help="One or more .docx files and/or directories to scan recursively. "
        "Shell globs such as 'normen/*' are expanded by the shell and accepted here.",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="control_matrix.csv",
        help="Output CSV file for the matrix (matrix mode only). "
        "Default: control_matrix.csv",
    )
    parser.add_argument(
        "-d",
        "--delimiter",
        default=";",
        help='CSV delimiter for the matrix (default: ";" for German Excel)',
    )
    args = parser.parse_args()

    # A single file argument keeps the old "just list the tags" behaviour.
    if len(args.paths) == 1 and Path(args.paths[0]).is_file():
        run_single(Path(args.paths[0]))
    elif len(args.paths) == 1 and not Path(args.paths[0]).exists():
        print(f"Error: path not found: {args.paths[0]}", file=sys.stderr)
        sys.exit(1)
    else:
        run_matrix(args.paths, args.output, args.delimiter)
