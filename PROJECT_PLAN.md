# Project Plan: Deep Book Learning Skill

## Product Goal

Create an open-source Agent Skill that turns a local ebook into a private, resumable deep-learning project: structure map, mental models, argument tree, controversies, cognitive-risk prediction, high-order questions, Socratic tutoring, error tracking, transfer, critique, personal knowledge system, and final assessment.

## User Flow

1. Install the skill locally.
2. Provide a PDF, EPUB, DOCX, TXT, or Markdown book.
3. Run inspection and parsing.
4. Create a learning project folder with `.book_learning/` state.
5. Generate staged learning artifacts with source traceability.
6. Enter one-question-at-a-time tutor mode.
7. Accumulate error logs, cognitive-gap profile, review queue, and final assessment.

## Skill Structure

- `SKILL.md`: concise trigger, workflow, scripts, state, and safety rules.
- `scripts/`: executable parsing, chunking, validation, and project-init commands.
- `deep_book_learning/`: reusable Python implementation.
- `references/`: methodology loaded only when needed.
- `templates/`: Markdown output skeletons for each learning artifact.
- `tests/`: standard-library tests and generated fixtures.
- `docs/`: architecture, workflow, formats, privacy, troubleshooting.

## Modules

- `inspect`: identify file type, metadata, status, warnings, checksums.
- `parsers`: parse PDF, EPUB, DOCX, TXT, Markdown, and best-effort HTML/RTF/ODT.
- `manifest`: build hierarchical book and chunk manifests.
- `chunking`: split by chapter/heading/paragraph before fixed windows.
- `project`: create output files, state files, and template artifacts.
- `validation`: fail loudly on missing outputs, empty text, bad JSON, or partial extraction.

## Technology Choices

Python 3.10+, standard library where possible, `pypdf` for PDF when available, `python-docx` for DOCX when available, ZIP/XML parsing for EPUB and ODT, `unittest` for tests. Optional OCR is detected but not bundled in v0.1.0.

## Risks

PDF extraction can be low quality; metadata can be wrong; long books require layered synthesis; hallucinated source locations are prevented by source indexes; private books must not be committed or uploaded without consent; GitHub publishing requires `gh` or manual repository creation.

## Development Phases

Research -> requirements -> architecture -> prototype -> core implementation -> tests -> integration -> documentation -> clean validation -> Git -> GitHub publish -> release.

## Acceptance Criteria

Valid `SKILL.md`, project initialization, first-class PDF/EPUB/DOCX/TXT/Markdown paths, explicit extraction status, source index, long-book chunking, resumable state, tests, English/Chinese README, privacy-safe `.gitignore`, and no false claims about GitHub publication before it happens.
