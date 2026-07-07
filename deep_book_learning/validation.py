from __future__ import annotations

import json
from pathlib import Path

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
