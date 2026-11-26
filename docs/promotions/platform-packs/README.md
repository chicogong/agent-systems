# 《图解 Agent 系统》多平台宣发即用物料包 (Platform Packs)

[返回全渠道宣发库](../launch-pack.md) · [返回开源仓库首页](../../../README.md) · [在线阅读全书](https://books.aimake.cc/)

本目录包含针对主流开发者与技术传播平台的**即插即用、格式适配完成的宣发物料包**。所有内容均严格依据全书核心技术事实编写，图片已配置国内稳定加速 CDN，Markdown 排版与代码块均已适配各平台发布工具。

---

## 📦 物料包清单 (Manifest)

| 文件名 | 适用平台 / 场景 | 特色与排版重点 |
| :--- | :--- | :--- |
| **[wechat-longform.md](wechat-longform.md)** | **微信公众号** 深度技术长文 | 配备编辑元数据（3 组标题、封面建议、120 字摘要）、可视锚点、高亮引用块（`> 💡`、`> ⚠️`、`> 🔬`）、CDN 高清架构图、3 道读者自测微测验与试读招募。支持直接粘贴至 mdnice / doocs 一键排版。 |
| **[v2ex-post.md](v2ex-post.md)** | **V2EX** `/go/create`（分享创造） | 极简技术风格、拒绝营销辞令。包含 30 秒 TL;DR、真实踩坑痛点（时间戳摧毁缓存、模型假汇报）、三大硬核工程原则、五层稳定度递减排版 ASCII 图解与 V 友试读邀请。 |
| **[overseas-show-hn-reddit.md](overseas-show-hn-reddit.md)** | **海外社区** (Hacker News & Reddit) | 纯英文高水准草案。包含 **Part 1: Show HN**（架构视角、16 框架 Commit 锁死切面、预备答疑 Playbook）与 **Part 2: Reddit r/LocalLLaMA & r/MachineLearning**（聚焦本地推理引擎 vLLM / llama.cpp 的 KV Cache 显存经济学与纯标准库复现脚本）。 |

---

## 🚀 平台分发最佳实践

### 1. 微信公众号 (WeChat Official Account)
1. 打开 [wechat-longform.md](wechat-longform.md)；
2. 复制全文至 Markdown 微信转换工具（推荐 [mdnice.com](https://mdnice.com/) 或 [doocs.github.io/md](https://doocs.github.io/md/)）；
3. 选用“经典蓝”或“优雅黑灰”技术主题；
4. 点击“复制到公众号”，在微信后台编辑器直接粘贴；
5. 从文件开头的元数据配置中选择合适的标题与摘要即可发布。

### 2. V2EX
1. 打开 [v2ex-post.md](v2ex-post.md)；
2. 登录 V2EX 并进入 [分享创造](https://www.v2ex.com/go/create) 节点新建主题；
3. 选择文件顶部的标题方案（如方案 1），将正文草案复制粘贴至内容框；
4. 格式选择 Markdown，预览无误后点击发布并积极在评论区互动。

### 3. 海外社区 (Show HN & Reddit)
1. 打开 [overseas-show-hn-reddit.md](overseas-show-hn-reddit.md)；
2. **Show HN**：
   - 访问 [Hacker News Submit](https://news.ycombinator.com/submit)；
   - URL 填写 `https://books.aimake.cc/` 或 GitHub 仓库地址；
   - Title 采用 `Show HN: Illustrated Agent Systems – Visual architecture guide with 40 interactive traces`；
   - 提交后立即发布第一条作者自评（采用文中的 Show HN Text）；
   - 根据预备的 Q&A Playbook 针对性回复 HN 读者的技术探讨。
3. **Reddit**：
   - 进入 `r/LocalLLaMA`，选择 Flair `[Project]` 或 `[Discussion]`；
   - 粘贴专为本地 LLM / KV 缓存优化的正文内容，引发社区关于多步 Agent 显存优化的讨论。
