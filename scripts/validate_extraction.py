from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
import argparse
import json
from deep_book_learning.validation import validate_project, validate_project_knowledge_tree

parser = argparse.ArgumentParser(description="Validate a deep book learning project or .book_learning directory.")
parser.add_argument("project")
parser.add_argument("--knowledge-tree", action="store_true", help="Also validate knowledge_tree.json when present.")
args = parser.parse_args()
ok, messages = validate_project(args.project)
if args.knowledge_tree:
    tree_ok, tree_messages = validate_project_knowledge_tree(args.project)
    ok = ok and tree_ok
    messages.extend(tree_messages)
print(json.dumps({"ok": ok, "messages": messages}, ensure_ascii=False, indent=2))
raise SystemExit(0 if ok else 1)
