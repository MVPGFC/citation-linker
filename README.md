# Citation Linker (学术引用自动关联工具)

![License](https://img.shields.io/badge/license-MIT-blue.svg) ![Python](https://img.shields.io/badge/python-3.11+-green.svg) ![OpenAlex](https://img.shields.io/badge/data-OpenAlex-orange.svg)

**Citation Linker** 是一个强大 Skill，旨在解决学术写作中的痛点：它能自动扫描文本中的伪引用标记（如 `[1]`, `[10]`），智能分析上下文，通过全球最大的开放学术图谱 **OpenAlex** 匹配真实存在的学术论文，并一键生成标准的参考文献列表（Bibliography）。

---

## ✨ 核心功能

*   **🔍 智能语义匹配**：不只是简单的关键词搜索。它能提取引用位置的前文（句子/段落），通过内置的**多学科术语映射表**（覆盖工程、AI、医学等），将中文描述精准翻译为英文学术查询词。
*   **📚 全球学术覆盖**：基于 [OpenAlex API](https://openalex.org/)，检索范围覆盖全球 2.7 亿篇论文，远超 arXiv 的学科限制。
*   **🔓 免费 PDF 直达**：自动检测论文的 Open Access (OA) 状态，优先提供**免费 PDF 直达链接**。如果论文付费，则提供官方 DOI 链接以便溯源。
*   **📝 自动生成参考文献**：在输出详细匹配信息的同时，文末自动附带标准格式的 **Bibliography** 列表，可直接复制到论文中。
*   **🚀 零依赖/自适应**：无需申请 API Key，无需复杂的环境配置。脚本会自动适配当前 Agent 环境中的联网工具（如 `WebSearch` 或 `Browser`）。

---

## 🛠️ 安装方法

### 方式一：Agent 自动安装（推荐 🚀）
如果你不想手动操作文件，可以直接对你的 Agent 说：
> “请帮我安装这个 GitHub 仓库里的 Skill：https://github.com/MVPGFC/citation-linker”

Agent 会自动克隆仓库并将其放置在正确的配置目录下。

### 方式二：OpenClaw (小龙虾)
1.  找到你的 OpenClaw 配置目录（通常在 `~/.openclaw/skills/` 或项目根目录下的 `.openclaw/skills/`）。
2.  将本仓库中的 `citation-linker` 文件夹完整复制进去。
3.  重启 OpenClaw 或重新加载配置，Skill 即可生效。

### 方式二：Claude Code
1.  在你的项目根目录下创建 `.claude/skills/` 文件夹（如果不存在）。
2.  将 `citation-linker` 文件夹复制到该目录下。
3.  Claude Code 会自动扫描并加载该 Skill，你可以在对话中直接调用。

### 方式三：Trae IDE
将本仓库中的 `citation-linker` 文件夹完整复制到你的 Trae 项目根目录下的 `.trae/skills/` 文件夹中即可。
路径示例：`你的项目/.trae/skills/citation-linker/`

---

## 📖 使用指南

### 1. 触发 Skill
在 Agent 的对话框中，直接输入包含引用标记的文本，并要求 Agent “找出这些引用”或“生成参考文献”。

**示例指令：**
> “请帮我为下面这段文字中的 [1] 和 [2] 找到真实的参考文献：
> 深度学习在图像识别领域取得了巨大突破[1]。与此同时，Transformer 架构彻底改变了 NLP 的范式[2]。”

### 2. 查看结果
Agent 会自动执行以下步骤：
1.  分析文本，提取 `[1]` 对应的“深度学习/图像识别”和 `[2]` 对应的“Transformer/NLP”。
2.  在 OpenAlex 中搜索相关度最高、引用量最高的顶级论文。
3.  输出每篇论文的详细信息（标题、作者、期刊、PDF 链接）。
4.  在最后生成一份完整的参考文献列表。

---

## 📊 输出示例

```text
============================================================
引用 [1] → 关联论文:
标题: Deep learning
作者: Yann LeCun, Yoshua Bengio, Geoffrey E. Hinton
年份: 2015
期刊: Nature
DOI: https://doi.org/10.1038/nature14539
直达PDF: https://hal.science/hal-04206682 (✅ 免费开源)
引用: 78794 次引用
...

============================================================
参考文献列表 (Bibliography)
============================================================
[1] Yann LeCun, Yoshua Bengio, Geoffrey E. Hinton, "Deep learning," Nature, 2015. DOI: https://doi.org/10.1038/nature14539
...
```

## 🤝 贡献与反馈

如果你发现某些领域的专业术语匹配不准确，或者有新的功能建议，欢迎提交 Issue 或 PR！

*   **作者**: Adelaide Guo
*   **联系邮箱**: mvpgfc@live.com

---

## 📜 许可证

MIT License
