from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

SCHEMA_VERSION = "1.0"
ALLOWED_STATUS = {"NOT_STARTED", "PARTIAL", "READY", "WARNING", "FAILED"}
ALLOWED_PROVENANCE = {
    "original explicit content",
    "synthesis from original content",
    "AI inference",
    "external knowledge",
}
MAX_MODULES = 8
MAX_POINTS = 80


@dataclass
class KnowledgeTreeValidation:
    ok: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def pending_knowledge_tree(title: str | None = None, author: str | None = None) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "book": {
            "title": title or "",
            "author": author or "",
            "root_question": "",
            "core_thesis": "",
        },
        "modules": [],
        "cross_links": [],
        "generation": {
            "status": "NOT_STARTED",
            "warnings": ["Knowledge tree has not been synthesized yet."],
            "renderer_version": "1.0",
        },
    }


def collect_source_ids(manifest: dict[str, Any] | None = None, chunks: list[dict[str, Any]] | None = None) -> set[str]:
    ids: set[str] = set()
    for unit in (manifest or {}).get("units", []):
        unit_id = unit.get("unit_id")
        if isinstance(unit_id, str):
            ids.add(unit_id)
    for chunk in chunks or []:
        chunk_id = chunk.get("id")
        unit_id = chunk.get("unit_id")
        if isinstance(chunk_id, str):
            ids.add(chunk_id)
        if isinstance(unit_id, str):
            ids.add(unit_id)
    return ids


def validate_knowledge_tree(
    tree: dict[str, Any],
    valid_source_ids: set[str] | None = None,
) -> KnowledgeTreeValidation:
    errors: list[str] = []
    warnings: list[str] = []
    source_ids = valid_source_ids or set()

    if tree.get("schema_version") != SCHEMA_VERSION:
        errors.append("schema_version must be 1.0")

    generation = tree.get("generation") if isinstance(tree.get("generation"), dict) else {}
    status = generation.get("status")
    if status not in ALLOWED_STATUS:
        errors.append(f"generation.status must be one of {sorted(ALLOWED_STATUS)}")

    book = tree.get("book") if isinstance(tree.get("book"), dict) else {}
    modules = tree.get("modules") if isinstance(tree.get("modules"), list) else None
    if modules is None:
        errors.append("modules must be a list")
        modules = []

    if status == "READY":
        for key in ["title", "root_question", "core_thesis"]:
            if not str(book.get(key) or "").strip():
                errors.append(f"READY tree requires book.{key}")
        if not modules:
            errors.append("READY tree requires at least one module")

    if len(modules) > MAX_MODULES:
        warnings.append(f"tree has {len(modules)} modules; recommended maximum is {MAX_MODULES}")

    seen_ids: set[str] = set()
    total_points = 0
    for index, module in enumerate(modules, start=1):
        if not isinstance(module, dict):
            errors.append(f"module {index} must be an object")
            continue
        module_id = _required_string(module, "id", errors, f"module {index}")
        _required_string(module, "name", errors, f"module {module_id or index}")
        if module_id:
            _check_duplicate(module_id, seen_ids, errors)
        points = module.get("knowledge_points")
        if not isinstance(points, list):
            errors.append(f"module {module_id or index} knowledge_points must be a list")
            points = []
        if status == "READY" and not points:
            errors.append(f"READY module {module_id or index} must contain knowledge_points")
        total_points += len(points)
        for point_index, point in enumerate(points, start=1):
            if not isinstance(point, dict):
                errors.append(f"knowledge point {point_index} in {module_id or index} must be an object")
                continue
            point_id = _required_string(point, "id", errors, f"knowledge point {point_index}")
            _required_string(point, "name", errors, f"knowledge point {point_id or point_index}")
            _required_string(point, "summary", errors, f"knowledge point {point_id or point_index}")
            if point_id:
                _check_duplicate(point_id, seen_ids, errors)
            provenance = point.get("provenance", "synthesis from original content")
            if provenance not in ALLOWED_PROVENANCE:
                errors.append(f"{point_id or point_index} has invalid provenance: {provenance}")
            confidence = point.get("confidence")
            if confidence is not None and not isinstance(confidence, (int, float)):
                errors.append(f"{point_id or point_index} confidence must be numeric when present")
            _validate_source_ids(point.get("source_ids"), source_ids, errors, warnings, point_id or f"point {point_index}")
            examples = point.get("examples", [])
            if examples is None:
                examples = []
            if not isinstance(examples, list):
                errors.append(f"{point_id or point_index} examples must be a list")
                examples = []
            for example_index, example in enumerate(examples, start=1):
                if not isinstance(example, dict):
                    errors.append(f"example {example_index} in {point_id or point_index} must be an object")
                    continue
                if not str(example.get("summary") or "").strip():
                    warnings.append(f"example {example_index} in {point_id or point_index} has no summary")
                example_type = example.get("type", "book_case")
                if example_type == "AI-generated transfer example":
                    warnings.append(f"{point_id or point_index} includes AI-generated transfer example")
                _validate_source_ids(
                    example.get("source_ids"),
                    source_ids,
                    errors,
                    warnings,
                    f"example {example_index} in {point_id or point_index}",
                )

    if total_points > MAX_POINTS:
        warnings.append(f"tree has {total_points} knowledge points; recommended maximum is {MAX_POINTS}")

    cross_links = tree.get("cross_links", [])
    if not isinstance(cross_links, list):
        errors.append("cross_links must be a list")
    else:
        for link_index, link in enumerate(cross_links, start=1):
            if not isinstance(link, dict):
                errors.append(f"cross_link {link_index} must be an object")
                continue
            for key in ["from", "to"]:
                target = link.get(key)
                if target and target not in seen_ids:
                    errors.append(f"cross_link {link_index} {key} references unknown id: {target}")

    return KnowledgeTreeValidation(ok=not errors, errors=errors, warnings=warnings)


def _required_string(obj: dict[str, Any], key: str, errors: list[str], label: str) -> str:
    value = obj.get(key)
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{label} requires non-empty {key}")
        return ""
    return value


def _check_duplicate(value: str, seen: set[str], errors: list[str]) -> None:
    if value in seen:
        errors.append(f"duplicate id: {value}")
    seen.add(value)


def _validate_source_ids(
    values: Any,
    valid_source_ids: set[str],
    errors: list[str],
    warnings: list[str],
    label: str,
) -> None:
    if values is None:
        warnings.append(f"{label} has no source_ids")
        return
    if not isinstance(values, list):
        errors.append(f"{label} source_ids must be a list")
        return
    if not values:
        warnings.append(f"{label} has empty source_ids")
        return
    if not valid_source_ids:
        warnings.append(f"{label} source_ids cannot be verified because no source index was supplied")
        return
    for value in values:
        if value not in valid_source_ids:
            errors.append(f"{label} references unknown source_id: {value}")
