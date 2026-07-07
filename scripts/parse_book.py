from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
import argparse
import json
from pathlib import Path
from dataclasses import asdict
from deep_book_learning.parsers import parse_book
from deep_book_learning.project import build_manifest, write_json
from deep_book_learning.chunking import chunk_units, chunks_to_jsonl

parser = argparse.ArgumentParser(description="Parse a book into normalized text and source indexes.")
parser.add_argument("book")
parser.add_argument("--output-dir", required=True)
args = parser.parse_args()
out = Path(args.output_dir)
out.mkdir(parents=True, exist_ok=True)
parsed = parse_book(args.book)
chunks = chunk_units(parsed.units)
write_json(out / "parsing_report.json", parsed.report.to_dict())
write_json(out / "source_index.json", parsed.to_source_index())
write_json(out / "manifest.json", build_manifest(parsed, chunks))
(out / "extracted_text.md").write_text(parsed.text, encoding="utf-8")
(out / "chunks.jsonl").write_text(chunks_to_jsonl(chunks), encoding="utf-8")
print(json.dumps({"status": parsed.report.status, "output_dir": str(out), "chunks": len(chunks)}, ensure_ascii=False, indent=2))
