from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
import argparse
import json
from deep_book_learning.validation import validate_project

parser = argparse.ArgumentParser(description="Validate a deep book learning project or .book_learning directory.")
parser.add_argument("project")
args = parser.parse_args()
ok, messages = validate_project(args.project)
print(json.dumps({"ok": ok, "messages": messages}, ensure_ascii=False, indent=2))
raise SystemExit(0 if ok else 1)
