from __future__ import annotations

import html
import json
import textwrap
from pathlib import Path
from xml.etree import ElementTree as ET

from .knowledge_tree import collect_source_ids, validate_knowledge_tree

SVG_NAME = "19_\u5168\u4e66\u77e5\u8bc6\u6811.svg"
PNG_NAME = "19_\u5168\u4e66\u77e5\u8bc6\u6811.png"
MD_NAME = "19_\u5168\u4e66\u77e5\u8bc6\u6811.md"
RENDERER_VERSION = "1.0"


def render_project(project_dir: str | Path, png: bool = True) -> dict:
    project = Path(project_dir)
    meta = project / ".book_learning"
    tree_path = meta / "knowledge_tree.json"
    if not tree_path.exists():
        raise FileNotFoundError(f"missing {tree_path}")
    tree = json.loads(tree_path.read_text(encoding="utf-8"))
    manifest = _read_json(meta / "manifest.json")
    chunks = _read_jsonl(meta / "chunks.jsonl")
    result = render_tree(tree, project, collect_source_ids(manifest, chunks), png=png)
    _update_state(meta, result)
    return result


def render_tree(tree: dict, output_dir: str | Path, valid_source_ids: set[str] | None = None, png: bool = True) -> dict:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    validation = validate_knowledge_tree(tree, valid_source_ids)
    if not validation.ok:
        raise ValueError("; ".join(validation.errors))
    md_path = out / MD_NAME
    svg_path = out / SVG_NAME
    png_path = out / PNG_NAME
    md_path.write_text(to_markdown(tree, validation.warnings), encoding="utf-8", newline="\n")
    svg_text = to_svg(tree, validation.warnings)
    svg_path.write_text(svg_text, encoding="utf-8", newline="\n")
    png_status = "SKIPPED"
    png_warning = None
    if png:
        png_status, png_warning = _try_write_png(svg_text, png_path)
    return {
        "status": "PASS",
        "markdown": str(md_path),
        "svg": str(svg_path),
        "png": str(png_path) if png_status == "PASS" else None,
        "png_status": png_status,
        "warnings": validation.warnings + ([png_warning] if png_warning else []),
    }


def to_markdown(tree: dict, warnings: list[str] | None = None) -> str:
    book = tree.get("book", {})
    lines = [
        f"# {book.get('title') or 'Untitled Book'} 全书知识树",
        "",
        f"- 作者：{book.get('author') or 'unknown'}",
        f"- 核心问题：{book.get('root_question') or '未生成'}",
        f"- 核心命题：{book.get('core_thesis') or '未生成'}",
        f"- 生成状态：{tree.get('generation', {}).get('status', 'UNKNOWN')}",
        "",
    ]
    for module in tree.get("modules", []):
        lines.extend([f"## {module.get('order', '')}. {module.get('name', '')}".strip(), "", module.get("summary", ""), ""])
        for point in module.get("knowledge_points", []):
            lines.extend([
                f"### {point.get('name', '')}",
                "",
                f"- 摘要：{point.get('summary') or 'unavailable'}",
                f"- 机制：{point.get('mechanism') or 'unavailable'}",
                f"- 边界：{point.get('boundary') or 'unavailable'}",
                f"- 常见误解：{point.get('misconception') or 'unavailable'}",
                f"- 来源：{', '.join(point.get('source_ids') or []) or 'unavailable'}",
                f"- Provenance：{point.get('provenance', 'synthesis from original content')}",
                "",
            ])
            examples = point.get("examples") or []
            if examples:
                lines.append("案例：")
                for example in examples:
                    lines.append(f"- [{example.get('type', 'case')}] {example.get('summary') or 'unavailable'}")
                lines.append("")
    if tree.get("cross_links"):
        lines.extend(["## Cross Links", ""])
        for link in tree["cross_links"]:
            lines.append(f"- {link}")
        lines.append("")
    if warnings:
        lines.extend(["## Warnings", ""])
        lines.extend(f"- {warning}" for warning in warnings)
        lines.append("")
    return "\n".join(lines)


def to_svg(tree: dict, warnings: list[str] | None = None) -> str:
    layout = _layout_tree(tree)
    width = layout["width"]
    height = layout["height"]
    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{_x(tree.get("book", {}).get("title", "Book"))} knowledge tree">',
        "<metadata>",
        _x(json.dumps({"generated_by": "deep-book-learning-skill", "schema_version": tree.get("schema_version"), "renderer_version": RENDERER_VERSION}, ensure_ascii=False)),
        "</metadata>",
        "<style>",
        "text{font-family:Arial,'Microsoft YaHei','PingFang SC',sans-serif;fill:#172033} .small{font-size:12px;fill:#4b5563}.title{font-size:24px;font-weight:700}.node-title{font-size:15px;font-weight:700}.node-body{font-size:12px}.line{stroke:#667085;stroke-width:1.6;fill:none}.root{fill:#f8fafc;stroke:#111827;stroke-width:2}.module{fill:#eef6ff;stroke:#2563eb}.point{fill:#fffdf5;stroke:#b45309}.case{fill:#f8fafc;stroke:#64748b}.warn{fill:#fff1f2;stroke:#be123c}",
        "</style>",
        f'<rect x="0" y="0" width="{width}" height="{height}" fill="#ffffff"/>',
    ]
    for line in layout["lines"]:
        parts.append(f'<path class="line" d="M {line[0]} {line[1]} C {line[2]} {line[1]}, {line[2]} {line[3]}, {line[4]} {line[3]}"/>')
    for node in layout["nodes"]:
        parts.extend(_svg_node(node))
    if warnings:
        y = height - 44
        parts.append(f'<text class="small" x="32" y="{y}">Warnings: {_x("; ".join(warnings)[:180])}</text>')
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def _layout_tree(tree: dict) -> dict:
    modules = tree.get("modules") or []
    point_count = sum(max(1, len(m.get("knowledge_points") or [])) for m in modules)
    width = 1850
    row_h = 132
    height = max(720, 180 + point_count * row_h)
    nodes = []
    lines = []
    book = tree.get("book", {})
    root_node = _node("root", 40, height // 2 - 110, 360, 220, book.get("title") or "Untitled Book", [
        f"Root: {book.get('root_question') or 'pending'}",
        f"Thesis: {book.get('core_thesis') or 'pending'}",
    ], "root")
    nodes.append(root_node)
    cursor_y = 90
    for module in modules:
        points = module.get("knowledge_points") or []
        block_h = max(row_h, len(points) * row_h)
        module_y = cursor_y + block_h // 2 - 54
        mod_node = _node(module.get("id", "module"), 500, module_y, 300, 108, module.get("name", ""), [module.get("summary", "")], "module")
        nodes.append(mod_node)
        lines.append((root_node["x"] + root_node["w"], root_node["y"] + root_node["h"] // 2, 450, mod_node["y"] + mod_node["h"] // 2, mod_node["x"]))
        if not points:
            points = [{"id": f"{module.get('id', 'module')}_pending", "name": "No knowledge points", "summary": "Pending synthesis.", "examples": []}]
        for idx, point in enumerate(points):
            y = cursor_y + idx * row_h
            point_node = _node(point.get("id", "point"), 900, y, 390, 112, point.get("name", ""), [
                point.get("summary", ""),
                f"Mechanism: {point.get('mechanism') or 'unavailable'}",
                f"Boundary: {point.get('boundary') or 'unavailable'}",
            ], "point")
            nodes.append(point_node)
            lines.append((mod_node["x"] + mod_node["w"], mod_node["y"] + mod_node["h"] // 2, 850, point_node["y"] + point_node["h"] // 2, point_node["x"]))
            example = _primary_example(point)
            detail_lines = [
                f"Case: {example}",
                f"Misread: {point.get('misconception') or 'unavailable'}",
                f"Source: {', '.join(point.get('source_ids') or []) or 'unavailable'}",
            ]
            case_node = _node(f"{point.get('id', 'point')}_case", 1390, y, 390, 112, "案例 / 边界 / 来源", detail_lines, "case")
            nodes.append(case_node)
            lines.append((point_node["x"] + point_node["w"], point_node["y"] + point_node["h"] // 2, 1340, case_node["y"] + case_node["h"] // 2, case_node["x"]))
        cursor_y += block_h + 36
    if not modules:
        pending = _node("pending", 520, height // 2 - 46, 420, 92, "Knowledge tree pending", ["Generate knowledge_tree.json after final synthesis."], "warn")
        nodes.append(pending)
        lines.append((root_node["x"] + root_node["w"], root_node["y"] + root_node["h"] // 2, 460, pending["y"] + pending["h"] // 2, pending["x"]))
    return {"width": width, "height": height, "nodes": nodes, "lines": lines}


def _node(node_id: str, x: int, y: int, w: int, h: int, title: str, body: list[str], kind: str) -> dict:
    return {"id": _safe_id(node_id), "x": x, "y": y, "w": w, "h": h, "title": title or "Untitled", "body": body, "kind": kind}


def _svg_node(node: dict) -> list[str]:
    lines = [f'<g id="{node["id"]}">', f'<rect class="{node["kind"]}" x="{node["x"]}" y="{node["y"]}" width="{node["w"]}" height="{node["h"]}" rx="8" ry="8"/>']
    lines.append(f'<text class="node-title" x="{node["x"] + 16}" y="{node["y"] + 24}">{_x(_clip(node["title"], 34))}</text>')
    y = node["y"] + 48
    for body in node["body"]:
        for wrapped in _wrap(body or "", max(18, (node["w"] - 32) // 8))[:3]:
            lines.append(f'<text class="node-body" x="{node["x"] + 16}" y="{y}">{_x(wrapped)}</text>')
            y += 18
    lines.append("</g>")
    return lines


def _wrap(text: str, width: int) -> list[str]:
    text = " ".join(str(text).split())
    if not text:
        return ["unavailable"]
    if any("\u4e00" <= ch <= "\u9fff" for ch in text):
        return [text[i : i + width] for i in range(0, min(len(text), width * 3), width)]
    return textwrap.wrap(text[: width * 3], width=width) or ["unavailable"]


def _clip(text: str, limit: int) -> str:
    text = " ".join(str(text).split())
    return text if len(text) <= limit else text[: limit - 1] + "…"


def _primary_example(point: dict) -> str:
    examples = point.get("examples") or []
    if not examples:
        return "unavailable"
    return examples[0].get("summary") or "unavailable"


def _safe_id(value: str) -> str:
    return "node_" + "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in str(value))


def _x(value: str) -> str:
    return html.escape(str(value), quote=True)


def _read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def _try_write_png(svg_text: str, png_path: Path) -> tuple[str, str | None]:
    try:
        import cairosvg  # type: ignore
    except Exception:
        return "UNAVAILABLE", "PNG backend unavailable; install cairosvg for PNG rendering."
    try:
        cairosvg.svg2png(bytestring=svg_text.encode("utf-8"), write_to=str(png_path))
    except Exception as exc:
        return "FAILED", f"PNG rendering failed: {exc}"
    return "PASS", None


def _update_state(meta: Path, result: dict) -> None:
    path = meta / "state.json"
    if not path.exists():
        return
    state = json.loads(path.read_text(encoding="utf-8"))
    state["knowledge_tree_status"] = "READY" if result["status"] == "PASS" else "WARNING"
    progress = state.setdefault("progress", {})
    progress["knowledge_tree"] = state["knowledge_tree_status"]
    completed = state.setdefault("completed_tasks", [])
    if "knowledge_tree_rendered" not in completed:
        completed.append("knowledge_tree_rendered")
    next_actions = state.setdefault("next_actions", [])
    state["next_actions"] = [item for item in next_actions if item != "render knowledge tree"]
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def assert_valid_svg(path: str | Path) -> None:
    ET.parse(path)
