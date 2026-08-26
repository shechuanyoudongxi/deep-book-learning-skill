# Deep Book Learning Skill

Upload a book. Get a private tutor that builds source-traceable mental models, challenges your understanding, tracks cognitive gaps, and helps you form your own knowledge system.

![version](https://img.shields.io/badge/version-0.1.0-blue) ![license](https://img.shields.io/badge/license-MIT-green)

## What It Does

Deep Book Learning is an Agent Skill for turning PDF, EPUB, DOCX, TXT, and Markdown books into a structured learning project. It is not a summarizer. It inspects the file, parses the book, creates a manifest and source index, chunks long text, then guides staged learning: structure map, mental models, argument tree, controversies, cognitive traps, high-order questions, Socratic tutoring, error tracking, transfer, critique, and final assessment.

The primary entry point is now the **Book Knowledge Tree**: one offline SVG map that shows the book's root question, core thesis, knowledge modules, key points, examples, boundaries, misconceptions, and source IDs.

## Workflow

```mermaid
flowchart LR
  A[Upload Book] --> B[Inspect]
  B --> C[Parse]
  C --> D[Manifest + Chunks]
  D --> E[Structure Map]
  E --> F[Mental Models]
  F --> G[Argument Tree]
  G --> H[Cognitive Risks]
  H --> I[Questions]
  I --> J[Socratic Tutor]
  J --> K[Error Tracking]
  K --> L[Transfer]
  L --> M[Knowledge Tree JSON]
  M --> N[SVG + Markdown + optional PNG]
```

## Install

Copy this folder into your Codex skills directory, or keep it as a repo and invoke it by path.

```bash
pip install -r requirements.txt
```

`pypdf` and `python-docx` are optional but recommended. EPUB, TXT, Markdown, HTML, RTF, and ODT use the Python standard library path in v0.1.0.

## Usage

```bash
python scripts/inspect_book.py path/to/book.pdf
python scripts/init_learning_project.py path/to/book.pdf --output outputs
python scripts/render_knowledge_tree.py outputs/MyBook_深度学习项目
```

Then ask your Agent to use `$deep-book-learning-skill` on the created project. The Agent should read `.book_learning/state.json`, `.book_learning/manifest.json`, and the relevant reference file before continuing.

## Outputs

Each book gets a project folder ending in `_深度学习项目/` with Markdown learning files plus `.book_learning/manifest.json`, `state.json`, `source_index.json`, `parsing_report.json`, `review_queue.json`, `knowledge_tree.json`, `chunks.jsonl`, and `extracted_text.md`.

## Book Knowledge Tree

After the Agent completes the core synthesis, it writes `.book_learning/knowledge_tree.json` first. The deterministic renderer then generates:

- `19_全书知识树.svg`: required, offline, scalable visual map.
- `19_全书知识树.md`: searchable text fallback with source traceability.
- `19_全书知识树.png`: best-effort compatibility image when a local PNG backend is available.

The tree is knowledge-centric, not chapter-centric:

```text
Root question
└─ Core thesis
   ├─ Core module
   │  ├─ Knowledge point
   │  │  ├─ Mechanism
   │  │  ├─ Case
   │  │  ├─ Boundary / misconception
   │  │  └─ Source IDs
```

`18_一页纸全书地图.md` remains a compressed conceptual summary. `19_全书知识树.svg` is the browsable visual map for understanding the book's knowledge system before entering the detailed 00-18 files.

## Privacy

The skill is local-first. Do not commit user books, extracted full text, generated private projects, caches, OCR artifacts, API keys, or secrets. The included `.gitignore` excludes these paths by default.

Users must have the right to process the books they provide.

## Limits

Scanned PDFs are detected but OCR is not bundled in v0.1.0. PDF layout, tables, footnotes, and two-column pages may need manual review. PNG rendering is optional and uses `cairosvg` when installed; SVG and Markdown still succeed without it. The skill marks partial extraction instead of pretending success.

## License

MIT
