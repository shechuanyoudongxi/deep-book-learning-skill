from pathlib import Path
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from deep_book_learning.knowledge_tree_renderer import render_project


parser = argparse.ArgumentParser(description="Render knowledge_tree.json into Markdown, SVG, and optional PNG.")
parser.add_argument("project_dir")
parser.add_argument("--no-png", action="store_true", help="Skip optional PNG rendering.")
args = parser.parse_args()

result = render_project(args.project_dir, png=not args.no_png)
print(json.dumps(result, ensure_ascii=False, indent=2))
