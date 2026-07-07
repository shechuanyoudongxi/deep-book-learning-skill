from __future__ import annotations

import json
import re
import shutil
from dataclasses import asdict
from pathlib import Path

from .chunking import chunk_units, chunks_to_jsonl
from .parsers import parse_book

TEMPLATE_FILE_ESCAPES = [
    r"00_\u5b66\u4e60\u603b\u63a7.md",
    r"01_\u4e66\u7c4d\u7ed3\u6784\u626b\u63cf\u62a5\u544a.md",
    r"02_\u6838\u5fc3\u5fc3\u667a\u6a21\u578b.md",
    r"03_\u4f5c\u8005\u8bba\u8bc1\u6811.md",
    r"04_\u6838\u5fc3\u4e89\u8bae\u4e0e\u8fb9\u754c.md",
    r"05_\u5b66\u4e60\u524d\u8ba4\u77e5\u98ce\u9669\u6e05\u5355.md",
    r"06_\u9ad8\u9636\u95ee\u9898\u5e93.md",
    r"07_\u4e2a\u4eba\u9519\u9898\u672c.md",
    r"08_\u4e2a\u4eba\u8ba4\u77e5\u6f0f\u6d1e\u6863\u6848.md",
    r"09_\u8d39\u66fc\u89e3\u91ca\u6d4b\u8bd5.md",
    r"10_\u73b0\u5b9e\u8fc1\u79fb\u6848\u4f8b.md",
    r"11_\u53cd\u9a73\u4e0e\u6279\u5224.md",
    r"12_\u4e2a\u4eba\u77e5\u8bc6\u4f53\u7cfb.md",
    r"13_\u6700\u7ec8\u9a8c\u6536\u62a5\u544a.md",
    r"14_\u5185\u5bb9\u9009\u9898\u5e93.md",
    r"15_\u5546\u4e1a\u5e94\u7528\u6a21\u578b.md",
    r"16_\u53cd\u5e38\u8bc6\u89c2\u70b9\u5e93.md",
    r"17_\u77ed\u89c6\u9891\u9009\u9898\u4e0e\u94a9\u5b50.md",
    r"18_\u4e00\u9875\u7eb8\u5168\u4e66\u5730\u56fe.md",
]
TEMPLATE_FILES = [name.encode("ascii").decode("unicode_escape") for name in TEMPLATE_FILE_ESCAPES]
PROJECT_SUFFIX = r"\u6df1\u5ea6\u5b66\u4e60\u9879\u76ee".encode("ascii").decode("unicode_escape")


def slugify(value: str) -> str:
    value = re.sub(r"[\\/:*?\"<>|]+", " ", value).strip()
    value = re.sub(r"\s+", "_", value)
    return value[:80] or "book"


def init_project(book_path: str | Path, output: str | Path) -> Path:
    parsed = parse_book(book_path)
    title = parsed.report.title or Path(book_path).stem
    project_dir = Path(output) / f"{slugify(title)}_{PROJECT_SUFFIX}"
    meta_dir = project_dir / ".book_learning"
    cache_dir = meta_dir / "cache"
    meta_dir.mkdir(parents=True, exist_ok=True)
    cache_dir.mkdir(exist_ok=True)

    chunks = chunk_units(parsed.units)
    manifest = build_manifest(parsed, chunks)
    source_index = parsed.to_source_index()
    state = {
        "book_id": manifest["book_id"],
        "user_goal": "general deep learning",
        "current_stage": 0,
        "progress": {"stage_0_inspection": parsed.report.status},
        "completed_tasks": ["inspection", "parse", "chunk", "project_init"],
        "active_question": None,
        "question_history": [],
        "user_answers": [],
        "scores": [],
        "mastered_models": [],
        "weak_models": [],
        "cognitive_traps_triggered": [],
        "review_queue": [],
        "next_actions": ["generate structure map", "extract mental models", "build argument tree"],
        "last_updated": None,
    }
    write_json(meta_dir / "manifest.json", manifest)
    write_json(meta_dir / "state.json", state)
    write_json(meta_dir / "source_index.json", source_index)
    write_json(meta_dir / "parsing_report.json", parsed.report.to_dict())
    write_json(meta_dir / "review_queue.json", [])
    (meta_dir / "chunks.jsonl").write_text(chunks_to_jsonl(chunks), encoding="utf-8")
    (meta_dir / "extracted_text.md").write_text(parsed.text, encoding="utf-8")

    skill_root = Path(__file__).resolve().parents[1]
    for name in TEMPLATE_FILES:
        src = skill_root / "templates" / name
        dest = project_dir / name
        if src.exists() and not dest.exists():
            text = src.read_text(encoding="utf-8")
            text = text.replace("{{title}}", title).replace("{{status}}", parsed.report.status)
            dest.write_text(text, encoding="utf-8", newline="\n")
    return project_dir


def build_manifest(parsed, chunks) -> dict:
    return {
        "book_id": parsed.report.checksum_sha256[:16],
        "title": parsed.report.title or parsed.source_path.stem,
        "author": parsed.report.author,
        "format": parsed.report.format,
        "source_file_name": parsed.source_path.name,
        "checksum_sha256": parsed.report.checksum_sha256,
        "status": parsed.report.status,
        "total_pages": parsed.report.page_count,
        "total_chapters": parsed.report.chapter_count,
        "text_char_count": parsed.report.text_char_count,
        "chunk_count": len(chunks),
        "warnings": parsed.report.warnings,
        "units": [
            {
                "unit_id": u.id,
                "title": u.title,
                "level": u.level,
                "source_location": u.source.location,
                "char_count": len(u.text),
                "token_estimate": max(1, len(u.text) // 4),
                "extraction_status": "PASS" if u.text.strip() else "EMPTY",
                "checksum": __import__("hashlib").sha256(u.text.encode("utf-8")).hexdigest()[:16],
            }
            for u in parsed.units
        ],
    }


def write_json(path: Path, data) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
