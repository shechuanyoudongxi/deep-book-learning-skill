# Architecture

The project separates Skill instructions, parser code, stage references, templates, and generated user outputs. Scripts call `deep_book_learning` modules and write all private outputs into a chosen project folder.

Knowledge tree delivery follows a JSON-first architecture:

```text
book analysis -> synthesis -> knowledge_tree.json -> validation -> Markdown -> SVG -> optional PNG
```

`knowledge_tree.py` owns schema, normalization, ID/source validation, density warnings, provenance rules, and compatibility behavior. `knowledge_tree_renderer.py` owns deterministic Markdown/SVG rendering and best-effort PNG conversion. The renderer does not infer book meaning; it only renders the already synthesized JSON.
