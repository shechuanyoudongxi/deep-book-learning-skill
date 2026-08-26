from __future__ import annotations

import json
from pathlib import Path

from .knowledge_tree import collect_source_ids, validate_knowledge_tree

REQUIRED = ["manifest.json", "state.json", "source_index.json", "parsing_report.json", "review_queue.json", "chunks.jsonl", "extracted_text.md"]


def validate_project(path_like: str | Path) -> tuple[bool, list[str]]:
    root = Path(path_like)
    meta = root / ".book_learning" if (root / ".book_learning").exists() else root
    messages: list[str] = []
    ok = True
    for name in REQUIRED:
        p = meta / name
        if not p.exists():
            ok = False
            messages.append(f"missing {name}")
    for name in ["manifest.json", "state.json", "source_index.json", "parsing_report.json", "review_queue.json"]:
        p = meta / name
        if p.exists():
            try:
                json.loads(p.read_text(encoding="utf-8"))
            except Exception as exc:
                ok = False
                messages.append(f"invalid JSON {name}: {exc}")
    text = meta / "extracted_text.md"
    if text.exists() and not text.read_text(encoding="utf-8").strip():
        ok = False
        messages.append("extracted_text.md is empty")
    report = meta / "parsing_report.json"
    if report.exists():
        status = json.loads(report.read_text(encoding="utf-8")).get("status")
        if status in {"PARTIAL", "FAILED"}:
            messages.append(f"extraction status is {status}; review limitations before analysis")
    return ok, messages


def validate_project_knowledge_tree(path_like: str | Path) -> tuple[bool, list[str]]:
    root = Path(path_like)
    meta = root / ".book_learning" if (root / ".book_learning").exists() else root
    tree_path = meta / "knowledge_tree.json"
    if not tree_path.exists():
        return True, ["knowledge_tree_status=NOT_STARTED"]
    try:
        tree = json.loads(tree_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return False, [f"invalid JSON knowledge_tree.json: {exc}"]
    manifest = _read_json(meta / "manifest.json")
    chunks = _read_jsonl(meta / "chunks.jsonl")
    validation = validate_knowledge_tree(tree, collect_source_ids(manifest, chunks))
    return validation.ok, validation.errors + validation.warnings


def _read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows
