---
language:
- zh
- en
license: mit
multilinguality:
- translation
task_categories:
- translation
- feature-extraction
- text-classification
tags:
- engineering
- civil-engineering
- construction
- standards
- terminology
- bilingual
- chinese-standards
- sqlite
size_categories:
- 1K<n<10K
configs:
- config_name: default
  data_files:
  - split: train
    path: data/train.parquet
---

# 中国工程建设标准双语专业术语库 (Chinese Standards Bilingual Term Bank)

<p align="center">
  <img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="License: MIT">
  <img src="https://img.shields.io/badge/Terms-9%2C665%2B-green.svg" alt="Terms Count">
  <img src="https://img.shields.io/badge/Standards-32%20Standards-orange.svg" alt="Standards Count">
  <img src="https://img.shields.io/badge/Domains-94%20Domains-purple.svg" alt="Domains Count">
  <img src="https://img.shields.io/badge/Format-SQLite%20%7C%20JSONL-brightgreen.svg" alt="Supported Formats">
</p>

本项目是由作者 **半城风雨 (Bancheng Fengyu / @banchengfengyu-maker)** 独立整理并开源的**中国工程建设国家标准/行业标准中英双语专业术语库**。

涵盖 **水文、电力、工程结构、供暖通风与空调、铁路工程、岩土工程、城市公共交通、生态环保** 等 **94 个细分工程领域**，汇聚 **32 部国家与行业权威规范**，收录了 **9,665+ 条具备条款级精确定位、权威度评分和双向检索加速的专业术语**。

> 💖 **开源不易，求个 Star 支持**：如果这个项目在工程翻译、标准查阅、涉外合同编制或大模型微调中帮到了你，请随手点一个 ⭐ **Star** (GitHub) 或 ❤️ **Like** (Hugging Face)！你的认可是作者持续整理与维护的最大动力！

---

## 🌟 核心亮点

* 🏛️ **权威标准背书**：术语 100% 提取自现行或行业主流国家标准（GB/T）与行业标准（CJJ/T 等），非网络爬虫或机器翻译推测。
* 🔍 **条款级精确定位**：每条术语均包含其在原规范中的条款编号（如 `2.1.1`）、发布年份、标准号与级别。
* ⚡ **极速双向检索**：内置 SQLite 数据库已提前完成分词归一化索引，生成 `zh_to_en_best` 与 `en_to_zh_best` 视图/表，实现毫秒级中英互查。
* 🎯 **多领域消除歧义**：同一词汇在不同领域提供精确的规范译名（例如在“暖通”与“电力”下的不同工程译法），并附带信任度打分与候选备选集。
* 📦 **开箱即用**：提供标准 SQLite 数据库文件与 JSONL 纯文本格式，附带轻量 Python CLI 查询脚本及代码调用示例，零外部第三方依赖。

---

## 📁 目录结构

```text
chinese-standards-termbank/
├── data/
│   ├── standard_term_bank.sqlite    # 核心 SQLite 数据库（约 11MB，含 9665+ 条术语及双向最优表）
│   ├── standard_terms_all.jsonl     # 全量术语 JSON Lines 数据集
│   └── standard_terms_report.json   # 32 部标准的提取质量与分类统计报告
├── examples/
│   └── quickstart.py                # Python 原生直连 SQLite 示例代码
├── query.py                         # 交互式双语快速查询命令行工具
├── LICENSE                          # MIT 开源许可（含署名要求）
└── README.md                        # 项目说明文档
```

---

## 🚀 快速上手

本项目无需安装任何庞大的第三方依赖库，仅需 Python 3.8+ 即可直接运行。

### 1. 命令行查询 (CLI Tool)

你可以直接使用项目根目录下的 `query.py` 工具进行双向查询（会自动根据输入语言判断方向）：

```bash
# 中译英查询
python query.py --term "水生态"

# 英译中查询
python query.py --term "hydroecology"

# 指定工程领域过滤
python query.py --term "建筑物" --domain "工程结构"

# 模糊/包含匹配 (Fuzzy Match)
python query.py --term "风机" --fuzzy

# 输出纯 JSON 格式（便于集成到其他自动化脚本或管线）
python query.py --term "门窗" --json
```

**查询效果示例：**
```text
🔍 查询词: '水生态' (共找到 1 条匹配结果):
---------------------------------------------------------------------------
[1] 水生态  ==>  hydroecology
    领域: 水文 | 信任分: 501
    来源标准: GB/T 50095-2014 水文基本术语和符号标准
---------------------------------------------------------------------------
```

### 2. Python 代码集成

#### 方式 A：通过 Hugging Face `datasets` 库一键加载 (推荐 AI 训练)
```python
from datasets import load_dataset

dataset = load_dataset("banchengfengyu/chinese-standards-termbank")
print(dataset["train"][0])
```

#### 方式 B：本地直接使用 `sqlite3` 查询 (推荐离线开发)

```python
import sqlite3
from pathlib import Path

db_path = Path("data/standard_term_bank.sqlite")
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# 查询中文术语对应的最佳标准英文译法
cur.execute("""
    SELECT zh, en, domain, source_name 
    FROM zh_to_en_best 
    WHERE zh_key = ?
""", ("建筑物(构筑物)",))

for zh, en, domain, source in cur.fetchall():
    print(f"[{domain}] {zh} -> {en} (依据: {source})")

conn.close()
```

更多示例请参考 [examples/quickstart.py](examples/quickstart.py)。

---

## 📊 数据库设计 (Schema)

数据库 `data/standard_term_bank.sqlite` 包含 3 张表：

| 表名 | 记录数 | 作用说明 | 主键 / 索引 |
| :--- | :--- | :--- | :--- |
| **`terms`** | 9,665 | 术语原始全量表，包含条款号、标准号、年份、权威度分值、提取元数据 | `id` (PK), `(zh_key, domain)`, `(en_key, domain)` |
| **`zh_to_en_best`** | 9,647 | 中译英最优去重表（依据信任评分最高优选），含其他备选列表 JSON | `(zh_key, domain)` |
| **`en_to_zh_best`** | 9,615 | 英译中最优去重表（依据信任评分最高优选），含其他备选列表 JSON | `(en_key, domain)` |

### 核心字段字典 (`terms` 表)

* `id`: 自增主键 ID
* `zh` / `en`: 中文标准术语 / 英文标准术语
* `zh_key` / `en_key`: 归一化搜索键（去除空格、小写化）
* `clause`: 标准原文中的章节条款编号（如 `2.1.1`）
* `domain`: 对应的专业工程领域（如 `水文`、`电力工程`、`暖通空调`）
* `source_name`: 来源标准全称
* `standard_code`: 标准编号（如 `GB/T 50095-2014`）
* `standard_level`: 标准级别（`national` 国家标准 / `industry` 行业标准）
* `trust_score`: 术语综合权威信任评分

---

## 📚 涵盖的主要标准与专业领域 (Top 15)

### 专业领域分布
* **水文** (1,582 条)
* **电力工程** (1,109 条)
* **工程结构** (1,025 条)
* **暖通空调** (662 条)
* **铁路工程** (649 条)
* **岩土工程** (419 条)
* **城市公共交通** (375 条)
* **工程测量** (340 条)
* **生态环境保护工程** (313 条)
* **民航工程** (266 条)
* **电子工程** (262 条)
* **建筑与结构** (210 条)
* **风景园林** (164 条)
* **医药工程** (156 条)
* **城市轨道交通** (130 条)

### 核心收录标准 (部分列举)
1. `GB/T 50095-2014` 《水文基本术语和符号标准》
2. `GB/T 50297-2018` 《电力工程基本术语标准》
3. `GB/T 50083-2014` 《工程结构设计基本术语标准》
4. 《民用航空工程术语标准》
5. `GB/T 50155-2015` 《供暖通风与空气调节术语标准》
6. `GB/T 50262-2024` 《铁路工程术语标准》
7. `GB/T 50279-2014` 《岩土工程基本术语标准》
8. `CJJ/T 119-2008` 《城市公共交通工程术语标准》
9. `GB/T 50833-2012` 《城市轨道交通工程基本术语标准》
10. `GB/T 51462-2024` 《生态环境保护工程术语标准》

---

## 📜 引用与署名说明 (Attribution & Citation)

本项目采用 **MIT 开源许可协议**。

根据作者要求，**任何个人、机构或企业在学术论文、商业软件、翻译工具、词典应用、开源项目或派生数据集中使用本术语库时，请务必保留署名并注明出处**：

### 文本引用格式
> **中文引用**：  
> 术语数据来源于：半城风雨 (Bancheng Fengyu) 整理之《中国工程建设标准双语专业术语库》，GitHub: https://github.com/banchengfengyu-maker/chinese-standards-termbank

> **English Citation**:  
> "Chinese Standards Bilingual Term Bank" collected and curated by Bancheng Fengyu (banchengfengyu-maker), available at: https://github.com/banchengfengyu-maker/chinese-standards-termbank

### BibTeX 引用
```bibtex
@misc{banchengfengyu2026termbank,
  author = {Bancheng Fengyu (banchengfengyu-maker)},
  title = {Chinese Standards Bilingual Term Bank (中国工程建设标准双语专业术语库)},
  year = {2026},
  publisher = {GitHub},
  journal = {GitHub repository},
  howpublished = {\url{https://github.com/banchengfengyu-maker/chinese-standards-termbank}}
}
```

---

## 🤝 支持与反馈 (Support & Feedback)

如果本项目对你的学习、工程实践或科研开发有所帮助，欢迎支持作者：
* ⭐️ **GitHub**：欢迎前往 [GitHub 仓库](https://github.com/banchengfengyu-maker/chinese-standards-termbank) 点个 **Star** 支持！
* ❤️ **Hugging Face**：欢迎前往 [Hugging Face 页面](https://huggingface.co/datasets/banchengfengyu/chinese-standards-termbank) 点击右上角 **Like**！
* 💡 **交流共建**：如有词条勘误、翻译优化或新国标扩充建议，欢迎提交 Issue 或 Pull Request！
