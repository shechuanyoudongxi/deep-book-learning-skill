from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
import argparse
import json
from pathlib import Path
from deep_book_learning.parsers import parse_book
from deep_book_learning.chunking import chunk_units
from deep_book_learning.project import build_manifest, write_json

parser = argparse.ArgumentParser(description="Build a manifest for a book or extracted text file.")
parser.add_argument("book_or_text")
parser.add_argument("--output", default=None)
args = parser.parse_args()
parsed = parse_book(args.book_or_text)
manifest = build_manifest(parsed, chunk_units(parsed.units))
out = Path(args.output) if args.output else Path("manifest.json")
write_json(out, manifest)
print(json.dumps({"manifest": str(out), "status": manifest["status"]}, ensure_ascii=False, indent=2))
