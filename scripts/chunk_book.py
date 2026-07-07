from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
import argparse
import json
from pathlib import Path
from deep_book_learning.parsers import parse_book
from deep_book_learning.chunking import chunk_units, chunks_to_jsonl

parser = argparse.ArgumentParser(description="Chunk a book or parsed project text.")
parser.add_argument("book_or_dir")
parser.add_argument("--max-chars", type=int, default=6000)
parser.add_argument("--overlap", type=int, default=600)
args = parser.parse_args()
p = Path(args.book_or_dir)
if p.is_dir() and (p / ".book_learning" / "extracted_text.md").exists():
    text_path = p / ".book_learning" / "extracted_text.md"
    parsed = parse_book(text_path)
    out = p / ".book_learning" / "chunks.jsonl"
else:
    parsed = parse_book(p)
    out = p.parent / "chunks.jsonl"
chunks = chunk_units(parsed.units, args.max_chars, args.overlap)
out.write_text(chunks_to_jsonl(chunks), encoding="utf-8")
print(json.dumps({"chunks": len(chunks), "path": str(out)}, ensure_ascii=False, indent=2))
