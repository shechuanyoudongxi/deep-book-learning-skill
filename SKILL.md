---
name: deep-book-learning-skill
description: Build a private deep-learning project from an ebook or long-form book file. Use when the user asks to deeply learn, master, teach, analyze, map, quiz, or build a learning system from a PDF, EPUB, DOCX, TXT, Markdown, or other book-like document; when they ask for mental models, argument trees, controversies, cognitive traps, high-order questions, Socratic tutoring, Feynman tests, transfer exercises, or a personal knowledge system for a book. Do not trigger for ordinary document summarization, contract review, short article extraction, or one-off file conversion unless the user explicitly wants a book-learning workflow.
---

# Deep Book Learning Skill

## Overview

Turn a book into a resumable learning project: inspect the source, parse and chunk it, build source-traceable intermediate artifacts, then guide the user through mental models, argument analysis, cognitive-risk prediction, Socratic tutoring, error tracking, transfer, critique, and final assessment.

The core rule is evidence discipline: never pretend the whole book was read, never invent pages or quotes, and mark unknown, partial, inferred, and external claims explicitly.

## Quick Start

When the user provides a book file or path:

1. Run `scripts/inspect_book.py <book_path>` to identify format, metadata, completeness, parsing risks, and status.
2. If inspection is not `FAILED`, run `scripts/init_learning_project.py <book_path> --output <workspace>` to create the project folder and `.book_learning/` state files.
3. Read `references/workflow.md` before generating stage artifacts.
4. Read only the stage-specific reference needed for the current task:
   - `references/learning_methodology.md` for structure maps, staged learning, state, and assessment.
   - `references/mental_models.md` for model extraction.
   - `references/argument_analysis.md` for claims, evidence, assumptions, controversy, and critique.
   - `references/socratic_tutoring.md` for one-question-at-a-time tutoring and hint ladders.
   - `references/cognitive_traps.md` for risk prediction, error logs, and review queues.
5. Generate or update Markdown outputs from `templates/` and keep state in `.book_learning/state.json`.
6. After the synthesis stages are complete, create `.book_learning/knowledge_tree.json`, validate it, then run `scripts/render_knowledge_tree.py <project_dir>` to generate the primary visual entry point.

## Supported Inputs

First-class formats: PDF, EPUB, DOCX, TXT, Markdown. Best-effort formats: HTML, RTF, ODT. If a parser is unavailable, mark the run `PARTIAL` or `FAILED` and explain what was not read.

## Workflow

### Stage 0: Book Inspection

Inspect before analysis. Record title, author, format, language if detectable, page or chapter count, table of contents, extraction status, warnings, checksums, OCR need, image/table/footnote risk, and source-location strategy. Statuses are `PASS`, `WARNING`, `PARTIAL`, and `FAILED`.

### Stage 1-6: Build the Learning Substrate

Generate `01_书籍结构扫描报告.md`, `02_核心心智模型.md`, `03_作者论证树.md`, `04_核心争议与边界.md`, `05_学习前认知风险清单.md`, `06_高阶问题库.md`, and `18_一页纸全书地图.md`.

Use layered synthesis: chunk evidence -> chapter claims/evidence/models/assumptions/counterexamples -> cross-chapter links -> whole-book argument structure -> mental models -> controversies and boundaries. Do not summarize summaries as a substitute for whole-book reasoning.

### Stage 7: Socratic Tutor Mode

Ask one question, wait for the user's answer, then evaluate. Do not reveal full answers immediately after a wrong answer. Use a hint ladder: direction -> model reminder -> chapter/source reminder -> partial logic -> complete answer.

Score: factual accuracy 20, structure 20, causal understanding 20, boundary awareness 15, transfer 15, expression 10. Update `07_?????.md`, `08_????????.md`, `.book_learning/review_queue.json`, and `.book_learning/state.json`.

### Stage 8-13: Mastery

Run Feynman explanations, real-world transfer, attack-the-author critique, personal knowledge-system reconstruction, and final assessment. Keep outputs source-traceable and distinguish original content, synthesis, AI inference, and external knowledge.

### Stage 19: Final Visual Knowledge Delivery

Use the existing synthesis files instead of re-summarizing the whole book independently. Prefer `01_书籍结构扫描报告.md`, `02_核心心智模型.md`, `03_作者论证树.md`, `04_核心争议与边界.md`, `10_现实迁移案例.md`, `12_个人知识体系.md`, `18_一页纸全书地图.md`, `.book_learning/manifest.json`, `.book_learning/source_index.json`, and `.book_learning/chunks.jsonl`.

Create `.book_learning/knowledge_tree.json` first. It must be knowledge-centric, not chapter-centric: root question -> core thesis -> 3-8 core modules -> 20-60 key knowledge points in normal books -> details such as summary, mechanism, book example, transfer example, boundary, misconception, provenance, confidence, and real `source_ids`.

Then run `scripts/render_knowledge_tree.py <project_dir>` to generate:

- `19_全书知识树.md`: searchable text fallback and detailed source-traceable tree.
- `19_全书知识树.svg`: required offline scalable visual delivery.
- `19_全书知识树.png`: best-effort compatibility image; missing PNG backend must not fail SVG/Markdown delivery.

In the final user-facing response, make `19_全书知识树.svg` the first suggested entry point. Then mention that detailed learning files remain in 00-18.

### Optional Content Creator Mode

Only enable when the user asks for content strategy, self-media, video topics, hooks, business applications, or counterintuitive viewpoints. Then generate files 14-17 from the templates. Keep this off for ordinary learners.

## Scripts

- `scripts/inspect_book.py <book>`: inspect format, metadata, extraction quality, and risks.
- `scripts/parse_book.py <book> --output-dir <dir>`: extract normalized text, structure, source index, and parsing report.
- `scripts/build_manifest.py <parsed-dir>`: rebuild `manifest.json`.
- `scripts/chunk_book.py <parsed-dir> --max-chars 6000 --overlap 600`: create semantic chunks.
- `scripts/validate_extraction.py <parsed-dir> --knowledge-tree`: validate manifest, source index, chunks, warnings, and the optional knowledge tree.
- `scripts/init_learning_project.py <book> --output <dir>`: end-to-end project initialization.
- `scripts/render_knowledge_tree.py <project-dir>`: render `.book_learning/knowledge_tree.json` to Markdown, SVG, and optional PNG.

## State And Recovery

Use `.book_learning/` in each project: `manifest.json`, `state.json`, `source_index.json`, `parsing_report.json`, `review_queue.json`, `knowledge_tree.json`, and `cache/`.

On resume, read `state.json`, `manifest.json`, and the latest stage files before continuing. Do not rely only on chat context.

Old projects may not have `knowledge_tree.json` or `knowledge_tree_status`. Treat missing values as `NOT_STARTED`, not as project failure.

## Stop Conditions

Pause and tell the user exactly what is missing when the file cannot be read, appears corrupt, is DRM-protected, requires unavailable OCR for core text, extraction is `FAILED`, or continuing would upload private book content to an unapproved service.
