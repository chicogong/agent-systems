# 写作、校稿与持续更新

[返回首页](../README.md) · [当前进度与缺口](roadmap.md) · [书稿与两种导出](../book/README.md) · [出版验收单](publication-checklist.md)

本书采用“**图解建立理解 + 具体例子讲清机制 + 固定版本源码按需核对**”。默认阅读不要求安装环境或完成作业；代码与实验是可选加深，不把书改成必须逐级通关的编程课。`docs/` 和 `book/frontmatter/`、`book/backmatter/` 是唯一正文；`figures/` 保留原生图源、展示图和图的文字版；`sources/` 记录上游版本与范围。PDF 和可携带 Markdown 阅读包都由 [`book/manifest.txt`](../book/manifest.txt) 指定同一批章节与顺序生成。导出目录不是写作位置，也不把 Obsidian 特有语法写进源稿。

## 仓库各处的职责

| 位置 | 单一职责 |
| --- | --- |
| `README.md`、`docs/concepts/`、`docs/systems/`、`docs/comparisons/` | 读者入口、机制、固定版本案例和横向综合。 |
| `book/frontmatter/`、`book/backmatter/`、`book/manifest.txt` | 卷首卷末正文与两种导出的章序；不复制章节正文。 |
| `figures/`、`sources/` | 可编辑图源及文字等价说明；上游版本与证据台账。 |
| `docs/roadmap.md`、`docs/program.md`、`docs/curriculum-expansion.md`、本文件 | 当前状态、候选选题、教学设计、写作方法各一处；历史 Pi 工单不是整本书的路线。 |
| `scripts/`、`.github/workflows/`、`output/` | 本地构建与检查、定时审稿、忽略提交的 PDF/Markdown 产物。 |

## 章节各负其责

| 类型 | 回答的问题 | 必须包含 |
| --- | --- | --- |
| 机制 `docs/concepts/` | 一类 Agent 设计怎样工作，边界在哪里？ | 一个具体问题、最小例子、主图及文字版、正常路径、失败/反例、至少一个真实系统映射。 |
| 系统 `docs/systems/<name>/` | 某个固定版本如何实现一条路径？ | 仓库与 commit、范围、入口、关键状态与分支、5–10 步代码导读、停止/失败路径、来源定位和未覆盖项。按[模板](systems/TEMPLATE.md)起稿。 |
| 对照 `docs/comparisons/` | 同一问题为何有不同取舍？ | 同一比较维度，双方证据的版本、核对日期与粒度；开源实现固定 commit，闭源侧只用官方文档或可复现观察，不作实现层等价断言。写出不同点的原因与代价；证据不足的格子留空。 |
| 练习 `docs/labs/` | 怎样亲自观察一个机制，并用反例验收？ | 学习目标、前置条件、可复制命令、预期轨迹、一个失败输入、修改后的验收和机制章链接。标准库模拟器明确标为模拟，不借其测试替真实产品背书。 |
| 可选连续教程（候选 `docs/tutorials/`） | 想动手时，怎样构建助手并迁移到新任务？ | 同一项目、逐步产物、待补实现、新输入任务、分级提示与独立答案。测试必须作用于读者实现；离线回放和真实模型分开声明。未交付前不算现有章节，不作为图解阅读前置。 |

图不是装饰，也不替代正文。一张图只回答一个主要问题；按需要使用时序、状态、泳道、层级、数据流或矩阵，不把同一种卡片布局套给所有项目。正文要能在不看图时独立理解，图的文字版要能说明节点、箭头与省略的边界。[图稿规范](../figures/STYLE.md)规定可读字号、线条、颜色与导出检查。

## 让不同读者找到入口

阅读体验参考 [Diátaxis 的教程／操作指南／参考／解释分工](https://www.diataxis.fr/map/)、[Hugging Face Agents Course 的渐进式课程](https://huggingface.co/learn/agents-course/unit0/introduction)和 [Brown 版 Rust Book 的误解自测](https://rust-book.cs.brown.edu/)，但不照搬目录或把每页做成同一模板。本书当前以**解释机制**与**固定源码案例**为主体。面向初学者、逐步构建能力的内容属于 [tutorial](https://diataxis.fr/tutorials/)；面向已有基础者解决具体问题的操作指南才是 [how-to](https://diataxis.fr/how-to-guides/)，不能把所有逐步操作都归为后者。连续教程按[教学设计](curriculum-expansion.md)连接现有机制与源码篇，命令、配置与术语索引属于参考材料；不把教程操作混成上游源码事实。读者既可按章序学习，也可从首页的问题表跳入一篇文章。

一篇新专题尽量依次回答：读完能判断什么、一个真实或明确标为虚构的任务如何经过各层、一张必要的图及文字版、来源与关键代码、失败边界、两三个自测问题。此顺序服务因果理解，不强制每篇使用相同标题或图形。系统篇仍以固定 commit 的实现证据为准；闭源工具的用法和官方行为可写，但不得伪装成源码剖面。

## AI 陪读是可选入口，不是第二套课程

通用方法只维护在[阅读指南](../book/frontmatter/reading-guide.md#和-ai-一起读)。先选 Agent loop、职责分工与上下文三篇校准，不给全部章节机械追加提示词块；默认仍可只读图文。AI 负责拆解疑问、追问与变式，书负责正常例子、关系图、术语与可追溯证据。

需要专题陪读入口时，只补该章独有的三件事：读者应解释的关系、可改变的一项条件、回到哪段文字或来源核对。任务先正常、后变化；答案不预填在问题里，不让 AI 一边出题一边自称证明学习效果。卡住时可以直接给小例子，不以持续追问增加读者负担。

校稿先检查不同阅读方式都能操作：普通 Markdown/PDF 可复制当前材料或图的文字版，不依赖按钮、图片识别或联网功能；代码篇的提示保留固定版本，不让助手凭最新版知识补旧结论。先验收这些静态入口，再考虑网页的材料复制快捷方式；内置聊天、API 接入、学习账号和自动评分均不是当前已实现功能。

试读分别记录：没有 AI 能否读懂图；AI 帮助后解决了哪个卡点；放下 AI 后能否解释同类新例子。只记录经读者同意、脱敏后的问题与反馈，不收集完整私人聊天。模拟助手对话只能检查设计缺陷，不能代替真人学习验收；对外不承诺学习效率提升或某模型始终遵守提示。

## 一篇内容怎样进入书

1. **定义读者问题和范围。** 用一句话说明读者读完能判断什么；列出常见误解、正常路径和至少一个失败边界。新系统必须贡献新的设计取舍，而不是因为热度高就入书。
2. **固定证据。** 记录规范仓库、commit/tag、核对日期、具体文件或官方文档、取得方式与许可。标清源码事实、文档声明、运行观察、工程推断、未知；没有环境与轨迹时不写“实测”。
   GitHub 的 `#L` 锚点须按固定版本的原始文件核对。网页工具可能压缩空行或重排文本，其提取行号不是源码行号；遇到差异先读 raw 文件或检出固定提交，不能直接据提取结果批量改链接。
3. **先写因果链，再画图。** 在 Markdown 中走通“输入 → 谁决策 → 谁执行 → 状态/副作用 → 怎样验证或恢复”。图只保留帮助理解的关键关系；把长注释移到图下。
4. **补关键代码逻辑。** 系统篇沿入口、状态、条件分支、副作用、结束/恢复解释，不堆大段第三方源码。机制篇连接至少一个可核对的系统路径，对照篇引用已写的系统剖面。
5. **校图文同源。** 从 `.excalidraw` 导出 SVG/PNG，检查线条、箭头、字体、裁切和 README 常见宽度；用文字版复述图意。MCP 交互画布若展示，另查画布，不能把本地导出检查当作画布像素验收。
6. **交叉审稿。** 第二位审稿者核对核心来源、术语、图中每个事实箭头，以及正常/失败路径；再请未参与写作的人只凭图文解释该章主张。不能复述就返工。
7. **决定是否入清单。** 完成正文、来源、图稿和本地检查后才加入 `book/manifest.txt`。清单代表进入预览版两种导出，不代表正式出版。更换上游 commit 是一次新的研究修订，要说明旧结论的范围。

并行研究时，各写作者只负责自己的 `docs/systems/<name>/` 或机制专题与对应 `figures/<figure>/`；README、书稿清单、路线、术语和公共构建脚本由合稿者统一修改。研究 Agent 给出的源码审计是初稿，不能替代另一位审稿者重开固定来源、检查主张和图中箭头。

## 每次变更的检查

```bash
python3 scripts/check_repo.py
python3 scripts/check_sources.py
python3 scripts/build_contents.py --check
python3 -m unittest discover -s scripts -p 'test_*.py'
python3 -m unittest discover -s examples/first-agent-loop -p 'test_*.py'
python3 -m unittest discover -s examples/context-budget -p 'test_*.py'
python3 -m unittest discover -s examples/remote-effect -p 'test_*.py'
python3 -m unittest discover -s examples/evidence-contract -p 'test_*.py'
python3 -m unittest discover -s examples/http-receipt -p 'test_*.py'
python3 scripts/check_figure_legibility.py --strict
python3 scripts/build_markdown.py
python3 scripts/build_book.py
python3 scripts/check_book_pdf.py
```

首次构建 PDF 前还需安装 [`book/requirements.txt`](../book/requirements.txt) 并运行 `python3 scripts/fetch_book_font.py`。图源生成器的确定性另由 CI 检查；若改生成图，先确认没有未保存的手工图稿编辑再运行 `scripts/rebuild_scenes.py`。人工还要打开阅读包中的首页、跨章节链接和 SVG/PNG，检查 PDF 受影响页、所有含图页及前后页；脚本通过不等于视觉、源码或许可审稿通过。

## 一个源稿，四个阅读界面

- **GitHub** 从[自动生成的书序目录](../book/CONTENTS.md)读源 Markdown，保留项目结构和可编辑图源。
- **在线阅读站** 从同一清单生成 HTML 章节、书序导航与图的文字说明，适合手机、搜索、引用和反馈。
- **Markdown ZIP** 沿同一清单生成可携带目录，适合 Obsidian 等本地阅读器；不在导出副本改稿，避免形成另一份事实来源。
- **PDF** 负责固定页序、目录、字体、印刷与封面校样；其位图化的正文图要以实际 A4 页面检查字号，不能只看独立高清 PNG。

PR 和每周 Action 都可生成两种离线导出供审稿；定时任务不会发布。每月抽查上游链接、项目版本和许可，记录“保持固定版 / 需新版剖面 / 链接损坏”；不要静默把旧源码结论改写成新版本事实。正式版本按[出版验收单](publication-checklist.md)留下候选版证据，人工完成外链、第三方内容、隐私、移动端、打印实样与非作者试读审查，再批准 tag/Release，并同时附 PDF 与 Markdown ZIP。具体未完成项只在[路线页](roadmap.md)维护。
