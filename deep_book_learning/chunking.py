from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Iterable

from .models import BookUnit


@dataclass
class Chunk:
    id: str
    unit_id: str
    title: str
    text: str
    source: dict
    char_count: int
    token_estimate: int


def chunk_units(units: Iterable[BookUnit], max_chars: int = 6000, overlap: int = 600) -> list[Chunk]:
    chunks: list[Chunk] = []
    for unit in units:
        paragraphs = [p.strip() for p in unit.text.split("\n\n") if p.strip()]
        if not paragraphs:
            paragraphs = [unit.text.strip()] if unit.text.strip() else []
        buf: list[str] = []
        current_len = 0
        part = 1
        for para in paragraphs:
            if current_len and current_len + len(para) + 2 > max_chars:
                text = "\n\n".join(buf).strip()
                chunks.append(_chunk(unit, part, text))
                part += 1
                carry = text[-overlap:] if overlap > 0 else ""
                buf = [carry, para] if carry else [para]
                current_len = sum(len(x) for x in buf) + 2 * max(0, len(buf) - 1)
            else:
                buf.append(para)
                current_len += len(para) + 2
        if buf:
            chunks.append(_chunk(unit, part, "\n\n".join(buf).strip()))
    return chunks


def _chunk(unit: BookUnit, part: int, text: str) -> Chunk:
    cid = f"{unit.id}-c{part:03d}"
    return Chunk(cid, unit.id, unit.title, text, unit.source.location, len(text), max(1, len(text) // 4))


def chunks_to_jsonl(chunks: list[Chunk]) -> str:
    import json
    return "\n".join(json.dumps(asdict(c), ensure_ascii=False) for c in chunks) + ("\n" if chunks else "")
