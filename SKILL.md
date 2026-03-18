---
description: 将文本中的伪引用标识（如 [1]、[10]）关联到真实学术论文。 基于 OpenAlex API（默认），支持扩展接入其他学术数据源（arXiv、Semantic Scholar、CrossRef 等）。 覆盖全球学术论文（物理、工程、地球科学、医学、计算机、农业等全学科）。 当用户提供包含 [数字] 格式引用标记的文本，并需要将这些引用关联到真实论文时触发。
name: citation-linker
author: Adelaide Guo <mvpgfc@live.com>
---

# Citation Linker

基于 OpenAlex API，将文本中的伪引用替换为真实学术论文。

## 数据源

**OpenAlex** — 全球最大的开放学术知识图谱：
- 覆盖 2.7 亿篇论文、书籍、数据集
- 完全免费，无需 API Key
- 包含 DOI、期刊、作者、引用数、主题分类
- ✅ MCP 工具可直接访问（`extract_content_from_websites`）

## 工作流程

### Step 1：提取引用

```bash
python3 scripts/citation_linker.py --extract "<文本>"
```

输出 JSON：
```json
[
  {
    "cite_key": "10",
    "context": "煤岩动力失稳...应变率敏感效应[10]",
    "search_query_en": "coal rock split hopkinson pressure bar crack propagation",
    "openalex_url": "https://api.openalex.org/works?filter=title_and_abstract.search:..."
  }
]
```

### Step 2：Agent 调用 MCP 或搜索工具

对每个引用的 `openalex_url`，Agent 需要获取其内容。

**工具调用优先级：**
1.  **首选**：如果你安装了 MCP 工具 `extract_content_from_websites`，请优先使用它来抓取 URL 内容。
2.  **备选**：如果没有该 MCP 工具，请使用你环境中的 `WebSearch`、`Browser` 或任何具备**读取网页/搜索 URL** 能力的工具。

**URL 格式：**
```
https://api.openalex.org/works?filter=title_and_abstract.search:<英文关键词>&per_page=35
```

### Step 3：格式化输出

```bash
cat results.json | python3 scripts/citation_linker.py --format text "<文本>"
```

输出示例：
```
引用 [10] → W4362593306
标题: Dynamic characteristics and crack evolution laws of coal and rock under SHPB
作者: Xiaoyuan Sun, Tingxu Jin et al.
年份: 2023
期刊: Measurement Science and Technology
DOI: https://doi.org/10.1088/1361-6501/acca3b
引用: 25 次引用
```

## 搜索策略（通用原则）

OpenAlex 的 `title_and_abstract.search` 字段对不同类型文本有不同的适配方式，遵循以下原则：

**1. 优先用脚本生成的中译英关键词**
脚本内置了 50+ 常用学术术语映射（中→英），优先使用其输出作为 `search_query_en`。

**2. OpenAlex 对 4 字以下词索引差**
- ❌ 避免：`CT`、`bar`、`MPa`、`SHPB`（单独使用）
- ✅ 替代：`synchrotron CT`、`split Hopkinson pressure bar`、`strain rate`、`pressure`

**3. 搜索结果为 0 时的重试策略**
- 换用更通用的上位词（如 "machine learning" → "deep learning"）
- 减少关键词数量，只保留最核心的 2-3 个词
- 用上位概念替代下位概念（如 "transformer" → "attention mechanism"）
- 换用纯英文 `batch_web_search` 搜索，再手动匹配 OpenAlex ID

**4. 领域自适应**
搜索策略由脚本的 `translate_query()` 和 `build_search_query()` 自动生成，适用于任何学科（医学、计算机、农业、材料等），无需人工维护领域特定表。

## 输出字段

| 字段 | 说明 |
|------|------|
| `cite_key` | 引用编号 |
| `title` | 论文标题 |
| `authors` | 作者列表 |
| `year` | 发表年份 |
| `journal` | 期刊名 |
| `doi` | DOI（可跳转） |
| `url` | 论文链接 |
| `pdf_url` | 论文PDF直达链接（如果有） |
| `is_oa` | 是否免费开源 (Open Access) |
| `cited_by` | 被引次数 |
| `topics` | OpenAlex 主题分类 |
| `abstract` | 摘要（部分论文有） |

## 作者

- **Adelaide Guo** (mvpgfc@live.com)

## 依赖

- Python 3.11+（内置库，无需安装）
- OpenAlex API（MCP 工具访问）
- 无需 API Key
