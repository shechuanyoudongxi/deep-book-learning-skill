# Workflow

Inspect first, parse second, initialize state third, then generate stage artifacts. Tutor mode always asks one question at a time and updates state.

After synthesis, generate `.book_learning/knowledge_tree.json`, validate it against manifest/chunk/source IDs, then render `19_全书知识树.md`, `19_全书知识树.svg`, and optional `19_全书知识树.png`. The SVG is the primary visual entry point; 00-18 remain the detailed learning materials.
