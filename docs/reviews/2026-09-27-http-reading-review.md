# HTTP 新章与学习入口：本地阅读验收

日期：2026-09-27。结论：首轮五页／十视口及解压阅读包检查通过，未发现新的阻断项；手机窄表仍有非阻断 P3。随后主代理为 PDF 排版缩短 Hermes 自测题 2 与 HTTP 代码导读第 5 项，以下保留首轮版本与最终稿的区别，不能把首轮截图当作最终导出的全部证据。

## 范围与版本

- 本地静态构建：`site/.vitepress/dist`，检查前确认指定页面与 sitemap 的本次更新时间为 21:35，并确认没有 VitePress 构建进程。只绑定 `127.0.0.1:18474` 的临时只读服务，未部署、访问私人 Obsidian 库、改正文或提交。
- 五页各在 **1280 × 900** 与 **390 × 900** 浏览器视口验证：`/learning-path`、`/systems/dsh`、`/systems/hermes`、`/concepts/computer-and-browser-use`、`/labs/http-receipt`。手机项是窄视口，不是实体手机触控或屏幕阅读器验收。
- 已完整阅读 `webapp-testing`、`playwright-best-practices` 主说明，先运行 `with_server.py --help`，再用生命周期管理器、原生 Python Playwright 与 headless Chromium。后一技能引用的 `core/`、`advanced/` 文件在本机缺失，采用主说明的等待／隔离／实际操作流程，不宣称读过不存在的参考。
- 首轮 HTTP HTML SHA-256：`f5baa426b140ba60f33187904c1334e13585f780aade0c5bc94e5a9962fe7162`。
- 首轮 HTTP 原 SVG SHA-256：`f558e23e44e410d8230825395bc074229545f9b6bef7d138085cbc40478d042b`。
- **实际解压审查的首轮 ZIP** SHA-256：`aa468912d007a645bf230b72cae5589bcaba42bf583b3c9af6ca7e33e450873c`。结束时磁盘 ZIP 已变为 `5bfa171494c3283f5955fef44353830f0fe8f8abd209ebd0f145a09ecbab079b`，不能将前一个解压目录的验收自动授予后一个包。

## 网页实际检查

| 页面 | 两视口的重点与结果 |
| --- | --- |
| `/learning-path` | 当前只选一个项目的最短路线、可选比较和本地 HTTP 入口存在；标题与正文正常换行。上一页阅读指南、下一页职责概念均本地 HTTP 200。 |
| `/systems/dsh` | 固定版本声明、插件范围、prepare／dispatch／ready 释义保留；图显示执行可重叠、连续 ready 顺序提交和 ask 缺通道拒绝。代码导读导航可用，图无重复。 |
| `/systems/hermes` | 快照／写入／待批准的主要边界与中文术语修订保留；图源原尺寸链接可打开。首轮自测题仍为较长问句，最终短句需新导出再核对。 |
| `/concepts/computer-and-browser-use` | 仅一图；两观察通道不是互斥分类。预算／取消等未完成停止说明已在网页出现，伪逻辑代码块在手机局部横滚而不撑宽正文。 |
| `/labs/http-receipt` | 仅 **一张** HTTP 图及一条原尺寸 SVG 入口；实际点击原尺寸链接打开 **1027 × 975** SVG。图后“不看图的说明”、完整图文字版和 fixture 说明存在。16 测试、默认 normal、两种 404 与 host／observer 区分未丢失。前后页为内存回执练习／完成证据对照，均 200。 |

十个视口均等待 `networkidle` 与字体就绪；用新浏览器 context 隔离，捕获 console error 与 pageerror。**页面、图、原尺寸图和上下篇目标均 200，console／JavaScript 错误 0；document 与 body 的 scrollWidth 均等于视口宽度。** 五页反馈邮件的主题、章节和 `books.aimake.cc` 对应页面均已预填；只检查链接，不实际发送邮件。

手机 HTTP 模式表的局部宽度为 342、内容宽度 557；实际滚至右侧 `scrollLeft=215`。首个代码块内容宽度约 619，实际滚至右侧 `scrollLeft=229`。因此不是“文字消失”：可读完整命令和右侧结论，页面本身没有横向溢出。

**非阻断 P3：** 390px 下 HTTP 输出字段表、模式表的说明列会收得很窄，部分中文逐字竖排，读者需要较长纵向滚动；DSH 的术语表同样有窄列。可以给这些表适当最小宽度并保留横滚，或为手机改为逐项卡片。这属于易读性改进，不是结论错误或资源不可访问。HTTP 图缩小后不宜硬读所有小字，原尺寸 SVG 和文字说明入口已清晰可见，不据缩略图声称手机图中文字全可读。

## 实际目视与临时证据

证据目录：`/tmp/agent-http-reading.iQIakf/`，只放临时脚本／截图，未加入仓库。`report.json` 保留十视口逐页结果，`md-report.json` 保留解压检查。实际目视了五页的桌面／手机开头、DSH／Hermes／Computer 桌面图、HTTP 原尺寸 SVG、手机缩略图与原尺寸入口、代码和模式表两侧、HTTP 两种视口页尾；没有声称每页全部像素或所有截图都已逐一人工审完。

代表性截图路径：

- `/tmp/agent-http-reading.iQIakf/learning-path-{1280,390}-top.png`。
- `/tmp/agent-http-reading.iQIakf/systems-dsh-{1280,390}-top.png`、`systems-dsh-1280-figure-0.png`、`systems-dsh-390-table-0.png`。
- `/tmp/agent-http-reading.iQIakf/systems-hermes-{1280,390}-top.png`、`systems-hermes-1280-figure-0.png`。
- `/tmp/agent-http-reading.iQIakf/concepts-computer-and-browser-use-{1280,390}-top.png`、`concepts-computer-and-browser-use-1280-figure-0.png`。
- `/tmp/agent-http-reading.iQIakf/labs-http-receipt-{1280,390}-top.png`、`labs-http-receipt-1280-original-svg.png`、`labs-http-receipt-390-figure-and-link.png`。
- `/tmp/agent-http-reading.iQIakf/labs-http-receipt-390-table-scrolled-right.png`、`labs-http-receipt-390-code-scrolled-right.png`、`labs-http-receipt-{1280,390}-footer.png`。

花括号是两个实际文件名的简写，不是一个文件名。浏览器原 SVG 截图显示各事件编号、时间向下、客户端超时后另连查询、匹配三项确认、不再 POST；没有画一条保证到达的迟到回执，404 作为旁注也不宣称失败。

## Markdown 包的实际核对

将首轮 ZIP 解压到 `/tmp/agent-http-reading.iQIakf/md/agent-systems-md/`，从包内 `README.md` 实际读取入门说明和目录：

- **65 个章单元／207 个文件**；README 的 65 章顺序与当前 `book/manifest.txt` 逐项一致，HTTP 位于内存回执后、完成证据前。
- 对包内所有 Markdown 用 CommonMark token 解析器取得本地链接／图片，核查 **624 个本地引用**：目标都实际存在且字节可读，无缺失。跳转章节、SVG、PNG、Excalidraw 源和 Python 代码在包内；未将外部 URL 或锚点语义混算为已离线验证。
- HTTP 三个图资产与对应首轮仓库图资产字节一致；图源 JSON 解析为 `excalidraw`。当前 DSH、Computer 及 HTTP 示例源码／测试字节一致。学习路径的差异只有 roadmap 改为 GitHub 外链，这是维护页不进阅读包的预期转换。
- 首轮包中的 Hermes 自测问句、HTTP 慢登记说明仍为缩短前版本；与主代理通知的两项差异一致，语义未变，不冒称最终稿已导出。
- **在解压包根目录**分别运行五组练习测试，共 **40/40**：Agent loop 3、上下文 9、内存回执 4、证据合同 8、HTTP 16。均退出 0；不用模型、API Key 或互联网服务，HTTP 仍需允许本机 loopback 监听。
- 在解压包实际运行 HTTP 七模式，退出码 **0、0、0、2、2、2、2**，宿主状态与正文一致。这里是可执行阅读包验证，不是 Obsidian 真实插件兼容或操作系统沙箱测试。

临时服务器已由 helper 结束；随后 `lsof -nP -iTCP:18474 -sTCP:LISTEN` 无监听。此报告只收口首轮本地读法，未验最终 PDF、线上更新、整站搜索／辅助技术、外部事实或印刷效果；最终短句与图更新导出需要追加记录。

## 最终排版差量复验

主代理重建默认站后，确认 dist 页面时间 21:43、无残留构建进程；复跑**五页 390px＋HTTP 1280px**共六视口，继续仅本地只读。结果：全部页面／图／原尺寸链接／上下篇 HTTP 200，HTTP 仍仅一图、文字替代入口存在，反馈预填正常；console／JavaScript 错误 0，document／body 无横向溢出。两处短句已进入网页及新解压包：

- Hermes 自测题 2 为“能断言 Skill 已更新且下次必用吗？”，答案仍区分待批准、落盘、发现与读取。
- HTTP 代码导读第 5 项为“慢登记测试延迟 0.25 秒，确认登记早于读超时”，前面仍明确同步不作为宿主业务证据、账本是事后观察、错误夹具抛异常。

**窄表 P3 关闭。** 手机媒体规则将 th／td 最小列宽设为 9rem，实际目视 HTTP 两张表与 DSH 表不再逐字竖排；内容仍可局部横滚。HTTP 输出字段表宽 **496／342**、实际滚动 **154px**，模式表 **644／342**、实际滚动 **302px**，右侧说明可完整读到。桌面 HTTP 两表仍 **624／624** 无需横滚，代码可读，图与导航无回归。代码块手机仍局部滚动 229px，不撑宽正文。

差量截图与结果在 `/tmp/agent-http-reading.iQIakf/final/`：`report.json`，`labs-http-receipt-390-fields-scrolled-right.png`、`labs-http-receipt-390-table-scrolled-right.png`、`labs-http-receipt-390-short-sentence.png`、`systems-hermes-390-short-question.png`、`systems-dsh-390-table-0.png` 等。实际打开看过上述表格两侧与两处短句截图，不把 DOM 断言冒充目视。

最终差量版本：HTTP HTML SHA-256 **`ff9a0d3d608c07194a53985924794047564f74f608e9b8358821af680890ca91`**；HTTP 原 SVG 仍为 **`f558e23e44e410d8230825395bc074229545f9b6bef7d138085cbc40478d042b`**，本轮改变网页表格与文字，没有重画图。

另将当前 ZIP 先复制为临时固定快照 `final/agent-systems-md.checked.zip` 再解压，SHA-256 **`5bfa171494c3283f5955fef44353830f0fe8f8abd209ebd0f145a09ecbab079b`**。重新检查 **65 章／207 文件／624 本地引用**及目录顺序，全部通过；Hermes、HTTP、DSH、Computer 与 HTTP 代码／测试均与当前稿字节一致，learning-path 的差异仍仅是维护路线页转为 GitHub 外链。五组测试再跑 **40/40**，HTTP 七 CLI 退出码保持 0、0、0、2、2、2、2。首轮未同步短句的差异已经关闭。

每次 helper 均结束服务器，最后专用端口无监听。该差量仍不是部署、最终 PDF 或印刷验收；后续提交 ref 若只改包的版本／来源外链，应核对变更清单和正文／图指纹，不能靠新 hash 猜测一致。
