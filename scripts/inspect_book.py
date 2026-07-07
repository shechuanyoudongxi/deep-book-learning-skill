from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
import argparse
import json
from deep_book_learning.parsers import inspect_book

parser = argparse.ArgumentParser(description="Inspect an ebook before deep learning analysis.")
parser.add_argument("book")
args = parser.parse_args()
print(json.dumps(inspect_book(args.book).to_dict(), ensure_ascii=False, indent=2))
