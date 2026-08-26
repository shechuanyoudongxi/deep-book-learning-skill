import json
import shutil
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
from xml.etree import ElementTree as ET

from deep_book_learning.knowledge_tree import collect_source_ids, pending_knowledge_tree, validate_knowledge_tree
from deep_book_learning.knowledge_tree_renderer import assert_valid_svg, render_project, render_tree, to_svg
from deep_book_learning.project import init_project
from deep_book_learning.validation import validate_project, validate_project_knowledge_tree


class KnowledgeTreeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path.cwd() / ".test-tmp" / self.id().replace(".", "_")
        shutil.rmtree(self.tmp, ignore_errors=True)
        self.tmp.mkdir(parents=True, exist_ok=True)
        self.fixture = json.loads((Path("tests") / "fixtures" / "knowledge_tree_cn.json").read_text(encoding="utf-8"))
        self.source_ids = {"u0001", "u0001-c001", "u0002", "u0002-c001"}

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_schema_validation_pass(self):
        result = validate_knowledge_tree(self.fixture, self.source_ids)
        self.assertTrue(result.ok, result.errors)

    def test_duplicate_ids_detected(self):
        tree = json.loads(json.dumps(self.fixture, ensure_ascii=False))
        tree["modules"][1]["id"] = "module_01"
        result = validate_knowledge_tree(tree, self.source_ids)
        self.assertFalse(result.ok)
        self.assertTrue(any("duplicate id" in error for error in result.errors))

    def test_invalid_source_detected(self):
        tree = json.loads(json.dumps(self.fixture, ensure_ascii=False))
        tree["modules"][0]["knowledge_points"][0]["source_ids"] = ["missing-source"]
        result = validate_knowledge_tree(tree, self.source_ids)
        self.assertFalse(result.ok)
        self.assertTrue(any("unknown source_id" in error for error in result.errors))

    def test_empty_ready_tree_is_invalid(self):
        tree = pending_knowledge_tree("Empty", "Nobody")
        tree["generation"]["status"] = "READY"
        result = validate_knowledge_tree(tree, self.source_ids)
        self.assertFalse(result.ok)
        self.assertTrue(any("at least one module" in error for error in result.errors))

    def test_svg_rendering_contains_core_content(self):
        result = render_tree(self.fixture, self.tmp, self.source_ids, png=False)
        svg_path = Path(result["svg"])
        svg = svg_path.read_text(encoding="utf-8")
        assert_valid_svg(svg_path)
        self.assertIn("精要主义", svg)
        self.assertIn("探索", svg)
        self.assertIn("选择", svg)
        self.assertIn("案例", svg)

    def test_chinese_rendering_is_not_corrupted(self):
        svg = to_svg(self.fixture)
        self.assertIn("精要主义", svg)
        self.assertIn("探索", svg)
        self.assertIn("选择", svg)
        self.assertIn("案例", svg)

    def test_xml_special_chars_are_escaped(self):
        tree = json.loads(json.dumps(self.fixture, ensure_ascii=False))
        tree["modules"][1]["knowledge_points"][0]["name"] = 'A & B < C > "D"'
        svg = to_svg(tree)
        ET.fromstring(svg)
        self.assertIn("A &amp; B &lt; C &gt; &quot;D&quot;", svg)

    def test_long_text_does_not_crash(self):
        tree = json.loads(json.dumps(self.fixture, ensure_ascii=False))
        tree["modules"][0]["knowledge_points"][0]["summary"] = "very long " * 200
        result = render_tree(tree, self.tmp, self.source_ids, png=False)
        assert_valid_svg(result["svg"])

    def test_old_project_without_knowledge_tree_is_compatible(self):
        meta = self.tmp / ".book_learning"
        meta.mkdir()
        for name, data in {
            "manifest.json": {"units": [{"unit_id": "u0001"}]},
            "state.json": {},
            "source_index.json": [],
            "parsing_report.json": {"status": "PASS"},
            "review_queue.json": [],
        }.items():
            (meta / name).write_text(json.dumps(data), encoding="utf-8")
        (meta / "chunks.jsonl").write_text("", encoding="utf-8")
        (meta / "extracted_text.md").write_text("text", encoding="utf-8")
        ok, messages = validate_project(self.tmp)
        tree_ok, tree_messages = validate_project_knowledge_tree(self.tmp)
        self.assertTrue(ok, messages)
        self.assertTrue(tree_ok, tree_messages)
        self.assertIn("knowledge_tree_status=NOT_STARTED", tree_messages)

    def test_new_project_initializes_pending_tree_and_template(self):
        book = self.tmp / "sample.md"
        book.write_text("# Book\nIntro\n\n## Chapter\nText", encoding="utf-8")
        project = init_project(book, self.tmp / "out")
        self.assertTrue((project / "19_全书知识树.md").exists())
        pending = json.loads((project / ".book_learning" / "knowledge_tree.json").read_text(encoding="utf-8"))
        self.assertEqual(pending["generation"]["status"], "NOT_STARTED")
        state = json.loads((project / ".book_learning" / "state.json").read_text(encoding="utf-8"))
        self.assertEqual(state["knowledge_tree_status"], "NOT_STARTED")

    def test_optional_png_failure_does_not_fail_render(self):
        with patch.dict(sys.modules, {"cairosvg": None}):
            result = render_tree(self.fixture, self.tmp, self.source_ids, png=True)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["png_status"], "UNAVAILABLE")
        self.assertTrue(Path(result["svg"]).exists())

    def test_render_project_updates_state(self):
        book = self.tmp / "sample.md"
        book.write_text("# Book\nIntro\n\n## Chapter\nText", encoding="utf-8")
        project = init_project(book, self.tmp / "out")
        meta = project / ".book_learning"
        chunks = [json.loads(line) for line in (meta / "chunks.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
        source_ids = collect_source_ids(json.loads((meta / "manifest.json").read_text(encoding="utf-8")), chunks)
        tree = json.loads(json.dumps(self.fixture, ensure_ascii=False))
        tree["modules"][0]["knowledge_points"][0]["source_ids"] = [next(iter(source_ids))]
        tree["modules"][0]["knowledge_points"][0]["examples"][0]["source_ids"] = [next(iter(source_ids))]
        tree["modules"][0]["knowledge_points"][1]["source_ids"] = [next(iter(source_ids))]
        tree["modules"][1]["knowledge_points"][0]["source_ids"] = [next(iter(source_ids))]
        tree["modules"][1]["knowledge_points"][0]["examples"][0]["source_ids"] = [next(iter(source_ids))]
        (meta / "knowledge_tree.json").write_text(json.dumps(tree, ensure_ascii=False, indent=2), encoding="utf-8")
        result = render_project(project, png=False)
        self.assertTrue(Path(result["svg"]).exists())
        state = json.loads((meta / "state.json").read_text(encoding="utf-8"))
        self.assertEqual(state["knowledge_tree_status"], "READY")


if __name__ == "__main__":
    unittest.main()
