# 图中文字与可读性复核（2026-10-06）

[返回当前状态](../roadmap.md) · [图稿风格](../../figures/STYLE.md)

## 本轮目的与分工

把图中的主标签改成容易读懂的动作和状态，同时保留源码定位需要的原名、分支和执行条件。沿用已采用的配色、字体与轻手绘线条；按内容选择流程、时序、状态机或对照布局，没有统一套成分层图。

主编负责十张概念与对照图、合稿、原生导出和构建检查；两名协作 Agent 分别处理十一张执行／扩展图与十张状态／记忆图；独立审查 Agent 只读检查全部最终 PNG、图源标签、箭头与文字说明。未创建新的侧栏会话，也未触及其他仓库。

## 表达和技术精度

- 主标签先说动作，例如“分工清单”“查询原操作”“核对结果”。`runLoop`、`ToolPart`、`SessionStatus`、`registerTool` 等原名仍在图中或文字说明中，方便继续读源码。
- 区分等待结果、成功、错误和未知结果；审批拒绝某次动作与结束整个任务分别表达。恢复原操作、查询回执与重新执行也分别画出。
- 条件没有随改短文字被删掉。例如，Browser Use 保存历史仍需要动作结果和网页摘要；OpenClaw 使用连接身份检查权限；Mem0 的入围候选仍只取语义检索结果；Hermes 保留正常会话与 detached 情况的区别；远端操作只有安全且获准时才可重试。
- OpenCode 补齐运行中调用的收尾清理分支；`ToolPart` 的单次调用进度与整个会话的 `SessionStatus` 仍分开。模型流的重试与 `continue / compact / stop` 三种外层处理结果也分别说明。
- 同步了相关正文与图说明中引用的旧标签。固定版本的上游证据链接未改成本轮未经复核的新版本；本轮没有新增真实产品运行验证。

## 视觉返修

31 张最终 PNG 已逐张查看，并对照图源文字、箭头与 README。审查发现并关闭了以下问题：

1. Browser Use 首次请求标签靠近标题框、返回摘要标签贴着上一条箭头；调整了间距并重新导出。
2. OpenCode 错误标签与斜线相交，首次移位又碰到清理标签；将清理文字移到右侧空白，最终版再次实看确认。
3. Mem0 的四个椭圆内文字靠近弧线；加高椭圆、居中文字，并调整箭头端点。
4. Codex、Kimi、OpenHands 的部分小字在 A4 几何预检中低于 8 pt；放大文字并调整框内空间，返修后预检为零告警，实际 PNG 也复看过。

图稿覆盖：`agent-loop`、`agent-stack`、`agent-workflow-multiagent`、`browser-use-step`、`claude-code-codex`、`codex-exec-approval`、`computer-browser-use`、`context-vs-memory`、`delegation-and-handoff`、`dsh-tool-batch`、`gpt-researcher-evidence`、`hermes-session-memory`、`http-receipt-timeline`、`interruption-recovery`、`kimi-code`、`langgraph-checkpoints`、`letta-memory`、`loop-and-stop`、`mcp-skill-permission`、`mem0-retrieval`、`mimo-code`、`mini-swe-loop`、`observation-evaluation`、`openclaw-session-gates`、`opencode-tool-state`、`openhands-action-events`、`permission-and-recovery`、`pi-architecture`、`pi-extensions`、`qwen-code-deferred-tools`、`sandbox-execution`。

## 导出与自动检查

全部图从同一份 `.excalidraw` 经未改动的原生 renderer 导出 SVG 与 4× PNG。最终再次重建图源、重复导出后，31 组图源／SVG／PNG 共 93 个文件的 SHA-256 相同。

`check_repo.py` 新增逐行检查图源与 SVG 的文字、重复次数、字号和颜色，防止修改图源却留下旧 SVG。它不检查 PNG 同步、字体回退或箭头布局，不能冒充像素一致性验收。新增十个测试覆盖旧文字、重复标签丢失、字号／颜色差异和坏输入。

统一重建命令也覆盖 `build_scene.py`，补上 Kimi 的非标准文件名；三个覆盖测试防止以后漏掉生成器。本轮检查结果：

| 检查 | 结果与范围 |
| --- | --- |
| 图包与 Markdown 本地链接 | 通过；包含图源／SVG 标签检查 |
| 固定来源台账 | 16 个系统记录通过结构检查，不是重新运行上游产品 |
| A4 图稿几何预检 | 31 张，0 个低于门槛的告警；仍需实页复核 |
| GitHub 书序目录 | 与 66 个书稿单元的清单一致 |
| 构建脚本测试 | 57 个通过 |
| 五组机制示例测试 | 40 个通过 |
| 网站单元测试 | 9 个通过 |
| 补丁空白检查 | 通过 |

## PDF 与阅读验收

最终图稿的本地审阅候选 PDF 为 155 页、66 个书稿单元、34 次正文图嵌入、817 个链接与九种嵌入字体，公共链接门禁通过。候选文件 SHA-256 为 `c72390ca5c18817a82cc517d179daeabce3d024fcb869fd011b2e763ab872165`；它是本地未提交稿的审阅文件，不是上线后的版本号。

155 页全部渲染为 2200 px 实页图；34 次正文图嵌入的像素与当前 PNG 相同，31 张图全部进入书稿。独立审查已实际查看全部 34 个含图页：18、21、23、28、31、37、39、41、46、49、51、59、63、65、69、72、76、79、83、86、89、93、96、100、105、109、113、117、121、124、129、133、137、143。放大的文字、箭头留白、图边裁切与前后标题未发现新的阻断问题；主编另实看非图变动页 19、27、64、90。

实页审查发现第 137 页正文仍要求读者寻找图中没有画出的正常回执分支；源稿已改成沿“连接超时 → 查询原操作”阅读，再看三种可能的服务状态。发布文件必须从最终干净提交生成，按像素差异复核版本页及这一改句影响的页面，不能沿用旧 PDF 的版本信息。

公开预览沿用既有流程：先完成候选审查和提交，再从干净提交构建公共 PDF、Markdown ZIP 与网站，分别检查，并在上线后回读文件字节。精确线上提交与 PDF／ZIP 散列以 [`/version.json`](https://books.aimake.cc/version.json) 为准；本记录的本地候选散列不能代替它。

## 未核验范围

本轮未取得 Excalidraw MCP 画布像素回读，不能声称交互画布与原生导出在所有环境下逐像素一致。没有完成逐行上游源码终审、真实产品运行验收、非作者真人试读、整书辅助技术验收或打印样张；封面仍非印刷母版。保持公开预览定位，不新建正式 Release。
