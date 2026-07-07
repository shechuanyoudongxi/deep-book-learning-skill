from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
import argparse
import json
from deep_book_learning.project import init_project
from deep_book_learning.validation import validate_project

parser = argparse.ArgumentParser(description="Create a resumable deep-learning project from a book.")
parser.add_argument("book")
parser.add_argument("--output", required=True)
args = parser.parse_args()
project = init_project(args.book, args.output)
ok, messages = validate_project(project)
print(json.dumps({"project": str(project), "ok": ok, "messages": messages}, ensure_ascii=False, indent=2))
raise SystemExit(0 if ok else 1)
