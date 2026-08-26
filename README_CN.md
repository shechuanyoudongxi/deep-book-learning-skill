# Deep Book Learning Skill（电子书深度学习 Skill）

上传一本书，得到一个本地私人导师：它会建立结构化知识地图、提炼心智模型、追问你的理解、记录错题和认知漏洞，并帮助你形成可迁移、可批判、可调用的个人知识体系。

新的默认入口是 **全书知识树**：先用一张可离线打开、可无限缩放的 SVG 图，看清整本书的核心问题、核心命题、知识模块、关键知识点、案例、边界、误解和来源，再进入 00-18 的详细学习材料。

## 核心能力

- 支持 PDF、EPUB、DOCX、TXT、Markdown。
- 先做 Book Inspection，再解析正文，不假装读完整本书。
- 为长书建立 manifest、source index、chunks 和可恢复 state。
- 生成结构扫描、核心心智模型、作者论证树、争议边界、认知风险、高阶问题库。
- 支持一题一答苏格拉底导师模式、动态错题本、复习队列、费曼测试、现实迁移、反驳作者和最终验收。

## 快速开始

```bash
pip install -r requirements.txt
python scripts/inspect_book.py path/to/book.pdf
python scripts/init_learning_project.py path/to/book.pdf --output outputs
python scripts/render_knowledge_tree.py outputs/MyBook_深度学习项目
```

然后在 Agent 中使用 `$deep-book-learning-skill` 继续学习项目。

## 输出结构

每本书会生成一个 `*_深度学习项目/` 文件夹，包含 00-19 的 Markdown 学习文件，以及 `.book_learning/manifest.json`、`state.json`、`source_index.json`、`parsing_report.json`、`review_queue.json`、`knowledge_tree.json`、`chunks.jsonl` 和 `extracted_text.md`。

## 全书知识树

完成核心综合后，Agent 先生成 `.book_learning/knowledge_tree.json`，再由确定性 renderer 生成：

- `19_全书知识树.svg`：必选主视觉，离线、可缩放、中文可读。
- `19_全书知识树.md`：可搜索的文字版，保留完整结构和来源。
- `19_全书知识树.png`：可选兼容图片，适合手机相册、微信和普通图片浏览器。

它不是章节目录，而是知识中心结构：

```text
核心问题
└─ 核心命题
   ├─ 知识模块
   │  ├─ 知识点
   │  │  ├─ 机制
   │  │  ├─ 案例
   │  │  ├─ 边界 / 误解
   │  │  └─ 来源 ID
```

`18_一页纸全书地图.md` 是极度压缩摘要；`19_全书知识树.svg` 是正式的视觉浏览入口。

## 隐私

默认本地处理。不要把用户书籍、完整抽取文本、学习项目、缓存、OCR 临时文件、API key 或 secrets 提交到 Git。用户需要确认自己有权处理相关电子书。

## 已知限制

v0.1.0 不内置 OCR；扫描型 PDF 会被识别为需要 OCR 或部分可读。PDF 表格、脚注、双栏和复杂版式可能需要人工复核。PNG 渲染依赖可选本地后端 `cairosvg`，缺失时不影响 SVG 和 Markdown 生成。

## License

MIT
