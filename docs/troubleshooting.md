# Troubleshooting

If extraction is PARTIAL or FAILED, inspect `.book_learning/parsing_report.json`. Install optional dependencies for PDF or DOCX. Use OCR externally for scanned PDFs.

If knowledge tree rendering fails, validate `.book_learning/knowledge_tree.json` with:

```bash
python scripts/validate_extraction.py <project_dir> --knowledge-tree
```

If PNG is unavailable but SVG and Markdown exist, the delivery is still valid.
