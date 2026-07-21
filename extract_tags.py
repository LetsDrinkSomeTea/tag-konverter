import zipfile
import xml.etree.ElementTree as ET
import sys
import csv
import argparse
from pathlib import Path

def extract_tags(docx_path):
    # Word XML namespace
    ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    tags = set()

    try:
        with zipfile.ZipFile(docx_path, 'r') as docx:
            # Parse document.xml and any headers/footers where tags might be located
            for item in docx.namelist():
                if item.startswith('word/') and item.endswith('.xml'):
                    xml_content = docx.read(item)
                    try:
                        tree = ET.fromstring(xml_content)
                        # Find all bookmarkStart elements
                        for bookmark in tree.findall('.//w:bookmarkStart', ns):
                            name = bookmark.get(f"{{{ns['w']}}}name")
                            # "Hidden" bookmarks in Word start with an underscore (e.g. _GoBack, _Toc...)
                            if name and not name.startswith('_'):
                                tags.add(name)
                    except ET.ParseError:
                        continue
    except Exception as e:
        print(f"Error reading docx file '{docx_path}': {e}", file=sys.stderr)
        return None

    return sorted(list(tags))


def find_docx_files(directory):
    """Recursively find all .docx files, skipping temporary Word lock files (~$...)."""
    root = Path(directory)
    files = [p for p in root.rglob('*.docx') if not p.name.startswith('~$')]
    return sorted(files)


def build_matrix(directory):
    """Scan a directory recursively and build a control-to-document mapping.

    Returns a tuple (doc_tags, all_controls) where:
      - doc_tags: dict mapping relative document path -> set of controls
      - all_controls: sorted list of every control found across all documents
    """
    root = Path(directory)
    doc_tags = {}
    all_controls = set()

    for docx_path in find_docx_files(directory):
        tags = extract_tags(docx_path)
        if tags is None:
            continue
        rel = docx_path.relative_to(root).as_posix()
        doc_tags[rel] = set(tags)
        all_controls.update(tags)

    return doc_tags, sorted(all_controls)


def write_matrix_csv(doc_tags, all_controls, output_path, delimiter=';', mark='X'):
    """Write a matrix: rows = controls, columns = documents."""
    documents = sorted(doc_tags.keys())
    with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f, delimiter=delimiter)
        # Header row
        writer.writerow(['Control'] + documents)
        # One row per control
        for control in all_controls:
            row = [control]
            for doc in documents:
                row.append(mark if control in doc_tags[doc] else '')
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


def run_directory(directory, output_path, delimiter):
    doc_tags, all_controls = build_matrix(directory)

    if not doc_tags:
        print(f"No .docx files found in '{directory}'.")
        sys.exit(1)

    write_matrix_csv(doc_tags, all_controls, output_path, delimiter=delimiter)

    print(f"Scanned {len(doc_tags)} document(s), found {len(all_controls)} distinct control(s).")
    for doc in sorted(doc_tags.keys()):
        print(f"  - {doc}: {len(doc_tags[doc])} control(s)")
    print(f"\nMatrix written to: {output_path}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Extract non-hidden document tags (controls/bookmarks) from Word documents. '
                    'Pass a single .docx file to list its tags, or a directory to build a '
                    'control-to-document matrix by recursively scanning all .docx files.')
    parser.add_argument('path', help='Path to a .docx file or a directory to scan recursively')
    parser.add_argument('-o', '--output', default='control_matrix.csv',
                        help='Output CSV file for the matrix (directory mode only). '
                             'Default: control_matrix.csv')
    parser.add_argument('-d', '--delimiter', default=';',
                        help='CSV delimiter for the matrix (default: ";" for German Excel)')
    args = parser.parse_args()

    target = Path(args.path)
    if target.is_dir():
        run_directory(target, args.output, args.delimiter)
    elif target.is_file():
        run_single(target)
    else:
        print(f"Error: path not found: {args.path}", file=sys.stderr)
        sys.exit(1)
