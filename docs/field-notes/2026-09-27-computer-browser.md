# Computer Use / Browser Use 研究记录

核对日期：2026-09-27。产出：[机制草稿](../concepts/computer-and-browser-use.md)与[教学图](../../figures/computer-browser-use/README.md)。本记录用于合稿审查，不是运行实验报告。

## 搜索范围与方法

完整读 Exa Search 技能及 searching、source-quality、synthesis、patterns-code 参考。按四个独立角度搜索，每次 `numResults=5`，`sources_reviewed: 20`：Anthropic 的宿主执行／截图安全；Playwright MCP 的结构化快照／profile；Chrome DevTools MCP 的协议／浏览器数据；OSWorld 与 BrowserGym 的环境／结果验收。这里 20 是技能规定的返回结果槽位统计，不是 20 篇独立全文均经审稿。

搜索结果只作发现入口。排除教程站镜像、功能排行和未经证实的效率宣传；正文只依赖第一方文档、固定官方仓库与原论文。没有用“Fast”“Reliable”等项目自述证明性能优于截图路线。没有操作真实浏览器、账号、桌面或下载用户数据。

## 已重开和核对的证据

| 来源 | 取得方式与质量 | 对应主张与限制 |
| --- | --- | --- |
| [Anthropic Computer Use 官方文档](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool) | Exa 全文；产品定义者公开执行循环和安全限制 | 应用运行工具请求；页面／图像存在提示注入风险。没有抄录易漂移的模型名单与定价。 |
| [claude-quickstarts 固定工具实现](https://github.com/anthropics/claude-quickstarts/blob/dee71163217524eed07d79d00ffea5a7d02cedda/computer-use-demo/computer_use_demo/tools/computer.py#L230-L302) | GitHub API 固定 SHA，raw 原文件及行号再次核对；示例维护者源码 | 截图与物理显示尺寸可能不同，`screenshot_size()` 和 `scale_coordinates()`。不当成所有 Computer Use 的标准接口。 |
| [Playwright MCP 固定 README](https://github.com/microsoft/playwright-mcp/blob/e87bb897e15a6f2af402afb0f10b45eced9e1f9b/README.md) | GitHub API 解码原始 README 再核对；维护者能力／配置说明 | 辅助功能快照、截图、persistent／isolated／extension、origin 过滤限制；不将 snapshot 误说成原始 DOM。 |
| [Playwright 官方认证文档](https://playwright.dev/docs/auth) | Exa 全文；框架维护者列明认证文件风险 | cookie／storage 状态可携带身份；未执行认证示例。 |
| [Chrome DevTools MCP 固定 README](https://github.com/ChromeDevTools/chrome-devtools-mcp/blob/ae0aaef884c41445d83f86f099ef211f4584b791/README.md) | 固定 SHA raw 文档；浏览器工具维护者 | Puppeteer 自动化、网络／控制台／trace，客户端暴露浏览器数据。没有根据营销措辞给可靠性排名。 |
| [CDP 官方规范入口](https://chromedevtools.github.io/devtools-protocol/) | Exa 全文；协议维护方列明 domains／命令事件与版本边界 | 协议是工具访问层，不是视觉模型，不能把 tip-of-tree 当稳定兼容保证。 |
| [Apple 辅助功能归档模型](https://developer.apple.com/library/archive/documentation/Accessibility/Conceptual/AccessibilityMacOSX/OSXAXModel.html) | Exa 全文；原生接口定义者 | 属性、动作、通知与控件实现义务。现代 AXUIElement 页面返回错误，转读归档概念文档；不用于现代权限安装步骤。 |
| [OSWorld 原论文](https://arxiv.org/abs/2404.07972) | Exa 论文全文；研究作者给环境与任务验收定义 | 跨应用环境、任务初态、执行结果评价；不拿 2024 年实验排名代表今天工具水平。 |
| [BrowserGym 固定 task.py](https://github.com/ServiceNow/BrowserGym/blob/9e779f087de9a65668b6974d11f9ce9816026e96/browsergym/core/src/browsergym/core/task.py#L101-L111) | GitHub API 解码原始文件及行号再核对；研究实现作者 | `OpenEndedTask` 在 `exit` 时结束，reward 恒零。可运行环境不意味着任意开放任务具备自动验收器。 |
| [本书固定 Browser Use step](../systems/browser-use/code-walkthrough.md) | 先读既有两篇剖面，沿其固定链接引用 | 状态超时清空映射、多动作 URL／焦点守卫；没有重写原项目系统篇，也未再做运行验收。 |

固定仓库 SHA 由 GitHub API 在本轮取得；其中 Browser Use 沿用书中已有 `d8110c5ff87ccba887aaa726cdb780f2f84bef8d`。

## 易错点与写作决定

- Exa 的 GitHub/raw 提取结果曾呈现较旧的格式／内容片段；关键 Anthropic 与 BrowserGym 主张最终按 GitHub 原始文件核对。网页提取行号不作为源码锚点。
- Computer Use 与 Browser Use 是任务范围词，`browser-use` 是具体项目。章节开头先拆开名字，随后按观测面／定位／执行／验收解释，而不是按品牌分类。
- 辅助功能树分浏览器语义快照与原生 OS 接口；DOM、AX、CDP、截图不处于同一抽象层。章节直接讲差别，图只抽象两个可组合通道。
- 填表不提交是虚构本地示例；正文补了自动保存例外，不把禁止点击提交当成网络零副作用保证。伪逻辑明确不是上游，也不是可运行 SDK。
- 没有引用第三方代码长段、图片、logo 或生成真实认证文件；不新增未经测量的成功率、耗时与产品推荐排名。

## 交叉审稿与下一步

合稿者应复核所有固定 SHA 链接、DOM／AX 术语、失败分支、虚构任务与上游事实的边界。图检验箭头不代表“模型直接执行”或“所有 Agent 必经两条观察通道”；文字版说明刷新循环有正常停止条件。

本轮本地验证：原生导出器前两轮均在加载 pinned jsDelivr 模块时超时，第三轮同引擎导出 SVG 与 4× PNG 成功，未改引擎或制造替代图。实际打开 PNG 检查了框内字形、箭头起止、反馈线与标签间距，没有观察到裁切或穿字。PNG 为 4352×2780；调用仓库 `inspect_figure()` 按 A4 同一规则估算，最小字约 9.6 pt、有效密度约 658 PPI，scene／SVG 最小字号一致。因章尚未加入公共清单，不能把 `--figure` 的清单检查当成已完成 PDF 页验收。生成器重复执行的 scene SHA-256 一致；`check_repo.py` 与 `git diff --check` 通过。MCP 交互画布没有视觉验收，也未声称与本地图源字体完全一致。

待补的是受控本地表单实验：设置弹层／自动保存／过期引用三种故障，按字段读回、动作日志、请求日志分别验收。再安排未参与写作的审稿 Agent 校准，本轮仍不能代替真实读者理解与真实网页端到端验证。
