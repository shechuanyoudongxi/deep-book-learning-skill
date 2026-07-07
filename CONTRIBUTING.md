# Contributing

Keep contributions source-traceable, privacy-preserving, and testable.

- Do not commit copyrighted user books, extracted private text, caches, API keys, or generated learning projects.
- Add generated fixtures for tests instead of real books.
- Mark parser limitations explicitly instead of hiding partial extraction.
- Keep `SKILL.md` concise; put detailed methods in `references/`, `templates/`, or scripts.

```bash
python -m unittest discover -s tests
python scripts/init_learning_project.py tests/fixtures/sample.md --output outputs
```
