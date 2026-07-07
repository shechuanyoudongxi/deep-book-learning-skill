from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class SourceRef:
    unit_id: str
    label: str
    location: dict[str, Any]


@dataclass
class BookUnit:
    id: str
    title: str
    level: int
    text: str
    source: SourceRef

    @property
    def char_count(self) -> int:
        return len(self.text)


@dataclass
class InspectionReport:
    status: str
    path: str
    file_name: str
    extension: str
    format: str
    mime_type: str
    size_bytes: int
    checksum_sha256: str
    title: str | None = None
    author: str | None = None
    language: str | None = None
    page_count: int | None = None
    chapter_count: int | None = None
    toc: list[dict[str, Any]] = field(default_factory=list)
    text_char_count: int = 0
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    parser: str | None = None
    ocr_required: bool = False
    source_strategy: str = "unknown"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ParsedBook:
    source_path: Path
    report: InspectionReport
    units: list[BookUnit]

    @property
    def text(self) -> str:
        return "\n\n".join(unit.text for unit in self.units if unit.text.strip())

    def to_source_index(self) -> list[dict[str, Any]]:
        return [asdict(unit.source) for unit in self.units]
