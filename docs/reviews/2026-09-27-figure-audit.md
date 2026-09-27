# 2026-09-27 图稿独立审稿

审稿基线：工作树起点 `3456188`。按 `AGENTS.md`、`figures/STYLE.md` 与 `excalidraw-agent` 约定审稿；这是内部 QA，不冒充外部读者试读。

## 实际检查范围

- 用 `view_image` 实际打开了全部 25 张 `preview.png`，先看委派、职责、中断恢复与 GPT Researcher，再看其余。工具展示对大图做了缩放；没有将缩放图当成原像素截图。
- 完整读了 25 份图目录的文字版；读取全部 scene 的字体、字号、roughness 与 SVG 文本节点；对问题项读取具体元素 ID、坐标和箭头路径。
- 图文语义深入抽样：委派、职责、中断恢复、GPT Researcher、Agent loop、MiMo Code 与循环对照正文。其他系统仅做图与图目录文字版对应检查，不宣称重新审计了全部上游源码。
- `python3 scripts/check_figure_legibility.py --strict`：25 组估算均不低于 8 pt，PNG/SVG 比例及最小字号没有脚本提示的不一致。**这不是实际 PDF 页、手机 UI、打印样张、MCP 画布或重导像素一致性的验收。** 本轮未检查 MCP、未打印，也未重导全部 25 图。

结论：没有发现全库文字裁切或箭头退化成不可辨认的现象；多数图已经是清楚的轻手绘、浅填色、短节点。但仍有两处需优先修正，不能用“几何预检通过”盖过它们。

## P1：下一批公开更新前修正

### P1-1 观察与评测：汇合箭头穿过关系标签

- 图：`figures/observation-evaluation`，右侧五条箭头汇入“有范围的结论”。
- 目视：`过程关联`、`汇总表现`、`复核体验`附近的斜线进入文字区；密集汇合使箭头语义不如左侧清楚。
- 源定位：`log-conclusion` 的斜段 `(803,153) → (904,360)` 穿过 `trace-relation` 的文字框 `(795,242,100,30)`；`eval-conclusion` 斜段 `(803,661) → (904,492)` 穿过 `eval-relation` `(795,625,100,30)`；`human-conclusion` 斜段 `(803,866) → (904,540)` 穿过 `human-relation` `(795,809,100,30)`，也经过评测标签区。
- 修法：关系标签放在各自水平段上方或左方，再把汇合斜段整体移到标签右侧的独立走线区；不要把标签盖白当成真正避让。保留当前证据尺度和颜色，不改成顺序流水线。
- 阻塞：阻塞此图本轮最终视觉验收；不表示整站必须下线。
- 状态：已交主代理返修，需重导、PNG 目视与实际含图 PDF 页复核。

### P1-2 四种循环：OpenCode 的 `error` 层级未写清

- 图：`figures/loop-and-stop`，OpenCode 行右卡 `blocked / error：停止`。
- 问题：中卡只写 `ToolPart → runLoop`，右卡的裸 `error` 很容易被读成 ToolPart 的错误必然终止会话；而正文明确说“单个 part error 不自动令 session 停止或重试”。文字版还说明 processor 的出口是 `continue / stop / compact`，现图却未显式展示 `stop`。
- 修法：重开固定源码核对 processor 出口；中卡明确经过 processor/外层循环，右卡显示 `continue / stop / compact` 的决策意义，另写“流内 retry”为内部条件路径而非第四个出口。不得把“所有 error 都停”换成“所有 error 都重试”。
- 阻塞：阻塞此图作为精确源码对照的本轮验收；其他单系统图不受此项直接影响。
- 状态：本审稿代理已按主代理指派独立返修；新 SVG/PNG 与文字版同步，预览目视通过本轮局部修正，实际含图 PDF 页仍待合稿复核。返修证据见下方。

## P2：易读性与教学完整性

| 图与位置 | 具体问题 | 建议修法 | 是否阻塞 |
| --- | --- | --- | --- |
| `agent-loop`，验证后的返工回路 | 只有“通过”及“未通过且可修正”；文字版自己承认“不可修正停止”没有画出来。正文强调失败/停止不可省略，读者只看总览图仍可能以为无限返工终会交付。 | 验证处分出明确的“不可修正/超限 → 停止并说明未完成”，可保持短标签；同步文字版，别画成又一种成功交付。 | 阻塞该图完整任务生命周期主张；已交主代理返修。 |
| `codex-exec-approval`，ExecPolicy 下方 Skip/NeedsApproval 走线 | 两条水平折线的 y 坐标分别约 333 和 335，线宽 3，长段重叠；实际图中橙线覆盖部分绿线，使分支来源不够清楚。 | 折线分配独立高度并留明显间距；给 NeedsApproval 向执行的箭头加“批准”短标签，以免卡内“拒绝停止”与出线关系依赖猜测。 | 不阻塞当前带正文的预览；正式印前前宜改。 |
| `openhands-action-events`，确认区 | `WAITING_FOR_CONFIRMATION` 和“获准后再次 run”虽用虚线，仍占主时序位置；“无需确认：同轮继续”只有旁注，初学者可能顺序读成每次必经两次 run。 | 将两条虚线放入明确 `需确认时` 的 opt 区；旁边写 `否则同轮执行`，保留拒绝分支。不要改泳道或把普通同步步画成两个线程。 | 不阻塞正文预览；教学版优化。 |
| `mimo-code`，没有可用状态 → 现场等待 writer | 成功的现场 writer 没有显式回到重建；当前只给失败/超时/禁用后的 compaction 注释。正文写的是“启动并有限等待，成功后插入重建边界”。 | 节点改为“启动并有限等待 writer”，加成功回到“重建边界 → 继续”的条件箭头；失败三种条件仍独立。别让两个判断阶段被画成主 Agent 每步等待 writer。 | 不阻塞带正文预览；正式版前宜补。 |
| `gpt-researcher-evidence`，Hybrid 加固定标签及风险提示 | 章节把“固定标签令空材料非空”限定在非 Granite PromptFamily；图文字版首段和风险条未保留此范围。单独打开图或文字版可能泛化到 Granite。 | 文字版首段补 `非 Granite PromptFamily`；风险短标签可写“本图提示词路径：空正文仍可能非空”，详细边界放图下。 | 不阻塞在线带正文预览；独立图分发前必须补范围。 |

## 建议：保留多样性，不做机械换色

- `openclaw-session-gates` 的源形状及箭头均 `roughness=0`，是全库最明显的直线门卡风格；正常/Code 两套字体仍协调、授权路径清楚。可按用户偏好只将主箭头与框轮廓调到轻手绘约 1，而保留方正的“关口”语言。不是要换成 Pi 分层图。
- `agent-loop` 多数形状 `roughness=0`，视觉比近期委派/恢复图更规整。若本轮加失败分支，顺手把关键路径调成轻手绘即可，不须全图粗描边。
- `context-vs-memory`、`observation-evaluation` A4 最小估算约 8.1 pt，虽然过几何线，底部注释/关系字仍需实际 PDF 页和样张复核。手机整图在窄栏内不能保证所有字无放大可读；原尺寸 SVG 和文字版入口要继续保留。
- 有些图标题很大但解释标签短，不是缺陷；标题/分层框不应为追求全书统一而强加给所有图。`permission-and-recovery`、`interruption-recovery`、`gpt-researcher-evidence` 的机制区分和轻手绘线条可作为近期基准。
- `check_figure_legibility.py` 的“0 need manual review”容易被读成免人工检查；它实际只统计几何风险。未来可将输出改成“0 geometric flags; visual review still required”。本轮没有改脚本。

## 逐图记录

以下每项均实际看过 PNG，并读图目录文字版。数字是当前 A4 估算最小字号，**不是主观读懂率**。未列出问题仅表示此次预览扫查未发现明显缺陷，不表示源码/运行/打印全面通过。

| 图 | 最小估算 pt | 本次判断 |
| --- | --- | --- |
| agent-loop | 8.7 | P2：缺非成功停止；其他节点与回路清楚。 |
| agent-stack | 9.2 | 一轮边界明确写非进程边界；Skill 虚线、工具结果回路清楚。 |
| agent-workflow-multiagent | 8.4 | 三行比较与并行分工没有误画为跨行流水线；灰色说明较小，需 PDF 复核。 |
| browser-use-step | 10.1 | 四泳道与截图/vision 条件对应文字版；未见穿字。 |
| claude-code-codex | 10.2 | 两行证据范围分开；拒绝/阻断有条件标识；未见裁切。 |
| codex-exec-approval | 8.7 | 返修前 P2：分支局部重叠；返修后独立折线与“批准”标签已 PNG 目视确认。 |
| context-vs-memory | 8.1 | 来源到本轮输入界限清楚；底部小注需实页。 |
| delegation-and-handoff | 8.4 | 回报汇合与验收返工环清楚，虚线含义与文字版一致；没有发现旧版文字偏出卡片问题。 |
| gpt-researcher-evidence | 9.2 | 先加载后 gather、空文档回退均明确；返修后图内及文字版补非 Granite 范围，已 PNG 目视确认。 |
| interruption-recovery | 9.1 | 已创建/可重试/未知三路、重试次数与副作用边界清楚；文字版匹配。 |
| kimi-code | 8.6 | steer 缓冲与停止前检查区分；取消/上限提示保留。 |
| langgraph-checkpoints | 9.3 | 原分支仍保留，新分支/配置指向清楚；未见字体截断。 |
| letta-memory | 9.2 | system prompt 与 conversation 不混；底部两种写入路径并列。 |
| loop-and-stop | 9.9 | 返修前 P1：OpenCode 出口层级歧义；返修后 PNG 已目视，三种出口与流内条件退避区分清楚。 |
| mem0-retrieval | 9.1 | 候选池仅语义结果，BM25/实体可用条件都写出；未见三路并集误画。 |
| mimo-code | 12.0 | 提前写与溢出两个阶段清楚；P2：现场 writer 成功回路缺失。 |
| mini-swe-loop | 9.8 | 消息账本、尾部 exit、下一轮/返回两分支清楚。 |
| observation-evaluation | 8.1 | P1：右侧关系标签被斜线穿过。 |
| openclaw-session-gates | 8.8 | 真实目标授权与请求 key 区分清楚；返修后轮廓/箭头 roughness 1，拓扑不变，已 PNG 目视确认。 |
| opencode-tool-state | 13.1 | 调用层与会话层区分清楚；pending 清理虚线可见。 |
| openhands-action-events | 9.4 | P2：确认条件需 opt 标识强化，文字版已说明条件路径。 |
| permission-and-recovery | 9.6 | 可能世界虚线、目标在途和回执未知都清楚，不把已接收当已完成。 |
| pi-architecture | 9.2 | 核心与 coding-agent 会话记录分开；C 来源由 AgentEvent 标签表达，不误作 B 的内部存储。 |
| pi-extensions | 9.3 | Skill 与 Extension 两路明确，交叉点在图下独立说明。 |
| qwen-code-deferred-tools | 10.8 | schema 文本与模型声明不等、发现与执行分开，目标条件保留。 |

## 返修验收记录

### loop-and-stop：P1-2 已局部修正

固定源码重新核对（2026-09-27）：

定位方法：最终链接行号以固定 commit 的 raw 文件字节经 `curl` 获取、`nl -ba` 编号核对；不使用网页抽取器的显示行号。抽取器会省略空行，曾造成此次过程中的错误锚点判断；该判断已撤回，图目录和本报告已按原始行号修正。

- [`SessionProcessor.process`](https://github.com/anomalyco/opencode/blob/18ef3cc7c5a25b82114c953a80ccc09f4988f74e/packages/opencode/src/session/processor.ts#L641-L695)：流内部调用重试策略并做清理后，仅返回压缩、停止或继续。需压缩判断在前；停止判断依据处理器阻塞或 assistant 消息错误，并非任意 ToolPart 错误。
- [`failToolCall`](https://github.com/anomalyco/opencode/blob/18ef3cc7c5a25b82114c953a80ccc09f4988f74e/packages/opencode/src/session/processor.ts#L186-L205)：收束调用错误；只有特定权限/问题拒绝与配置条件可设置处理器阻塞。
- [`外层消费出口`](https://github.com/anomalyco/opencode/blob/18ef3cc7c5a25b82114c953a80ccc09f4988f74e/packages/opencode/src/session/prompt.ts#L1319-L1335)：停止出口退出循环；压缩出口建立压缩任务后再处理；其余继续。外层还有结构化输出等额外判断，不在此图展开。
- [`SessionRetry.policy`](https://github.com/anomalyco/opencode/blob/18ef3cc7c5a25b82114c953a80ccc09f4988f74e/packages/opencode/src/session/retry.ts#L183-L204)：错误可重试判定与次数上限决定是否进入退避；它不是处理器第四种出口。

实际修改仅在此图目录：`build.py` 与 `scene.excalidraw` 的 OpenCode 中卡改为“流事件写 ToolPart / processor → 外层 loop”；右卡改成“continue / compact：再处理”“stop：结束外层循环”“流内 retry：有条件退避”；文字版补层级说明和固定源码链接。沿用原四行比较布局、Code 字体、浅色填充、roughness 1；没有改其他三行。

生成及导出命令：

其中 `EXCALIDRAW_AGENT_SKILL` 指向本机安装的同版 skill 目录；这里隐去机器专属路径。

```bash
python3 figures/loop-and-stop/build.py
uv run --project "$EXCALIDRAW_AGENT_SKILL/scripts" python "$EXCALIDRAW_AGENT_SKILL/scripts/render_excalidraw.py" figures/loop-and-stop/scene.excalidraw --output figures/loop-and-stop/diagram.svg
uv run --project "$EXCALIDRAW_AGENT_SKILL/scripts" python "$EXCALIDRAW_AGENT_SKILL/scripts/render_excalidraw.py" figures/loop-and-stop/scene.excalidraw --output figures/loop-and-stop/preview.png --scale 4
python3 scripts/check_figure_legibility.py --figure loop-and-stop --strict
```

首次 SVG 导出因 pinned renderer 的网络加载超时失败，随后原命令重试成功；没有换用自行拼 SVG 的替代渲染器。PNG 导出成功后实际用 `view_image` 打开，确认两行中卡与三行右卡不越框、不穿箭头；其他三行外观未改变。PNG 4056 × 3072，A4 放置估算 168 × 127 mm，最小文字约 9.9 pt。生成器连续重建两次的 scene SHA-256 一致。`check_repo.py` 与此范围 `git diff --check` 通过。

产物 SHA-256：scene `8e0ed6ded050906906781a88ad8966c21d660accd2f50f0b0c1ec07d49404b9c`；SVG `6e861e13fad3dbe6f4226229104fe1bdff4e3cb852a6e83d6f861fb7c1f20e47`；PNG `6e6c2103eb3f24c063fd19c5c8f04083a0c3bd695e29e83aaec472abe8bb360b`。

未验证：没有运行这个 OpenCode 固定版本的 provider、审批、退避或端到端循环；没有检查 MCP 画布、真实手机视图或打印样张；本轮新图尚未置入最终 PDF 实页。P1-2 的图内歧义已修，不据此宣称源码运行路径全面通过。其他图由主代理选择返修，本文件不会提前记作通过。

### codex-exec-approval：P2 走线已局部修正

重开固定 `c44deff7` 的 raw [`orchestrator.rs`](https://github.com/openai/codex/blob/c44deff7b1083e9660ac55d02122481f1cdf139b/codex-rs/core/src/tools/orchestrator.rs#L164-L221)，按原始行号确认 `Forbidden` 拒绝返回、`NeedsApproval` 审批获准才进入后续尝试。图保留 `Skip`“免普通审批 ≠ 免沙箱”的措辞，不将它泛化为所有配置完全免审核。

三个分支的水平走线改为 y=316、345、330，Skip 与 NeedsApproval 的长段不再覆盖；获准出线旁加“批准”。原图形、颜色、字体与粗细不变，文字版补出线条件与来源链接。原 pinned renderer 的 SVG 和 4× PNG 重试后均成功导出；实际打开新 PNG，三分支清楚可辨，“批准”不压线，节点文字没有新裁切。PNG 4800 × 3532；A4 估算 168 × 124 mm、最小 8.7 pt。生成器连续重建 scene 哈希一致。

此项不再阻塞局部图稿验收；实际含图 PDF 页仍待合稿复核。未运行真实审批/沙箱/平台后端。

### gpt-researcher-evidence：P2 范围已局部修正

对固定 `6f998577` 原始 `prompts.py` 用 `curl … | nl -ba` 再核对：默认拼接实际位于 [L564-L566](https://github.com/assafelovic/gpt-researcher/blob/6f998577d547b1e54ec662dac63583aa11e3b84b/gpt_researcher/prompts.py#L564-L566)；[Granite 家族 L756-L834](https://github.com/assafelovic/gpt-researcher/blob/6f998577d547b1e54ec662dac63583aa11e3b84b/gpt_researcher/prompts.py#L756-L834) 按模型族选择不同覆写。此前网页抽取行号不能用于源码锚点，正文原有锚点没有本轮误报的问题。

图标题下加“仅限非 Granite PromptFamily 的 Hybrid 路径”，文字版首段同步范围；风险条解释的依旧是默认格式，未扩大到所有 Granite 配置。其余拓扑/字形/颜色不变。原 pinned renderer 重试后导出 SVG 与 4× PNG，实际打开新 PNG，范围短注位于标题与阶段标签之间，没有撞字；分支和风险条可辨。PNG 4160 × 2388；A4 估算 168 × 96 mm，最小 9.2 pt。生成器连续重建哈希一致。本项独立图范围问题已收口；未运行检索、写作或实际空材料触发。

### openclaw-session-gates：轻手绘建议已落实

重开固定 `b373c9a9` 的原始 [请求路由](https://github.com/openclaw/openclaw/blob/b373c9a9bcd4954ccdab963e3ed71336302b82be/src/gateway/agent-turn/agent-request-routing.ts#L71-L105) 及 [规范化后授权](https://github.com/openclaw/openclaw/blob/b373c9a9bcd4954ccdab963e3ed71336302b82be/src/gateway/agent-turn/agent-turn-service.ts#L279-L334)，确认现有图仍只覆盖显式 key 的局部路径。

仅将六个关口框轮廓、九条箭头和底部说明框的 roughness 从 0 调为 1；保持顶栏实心、方角、原字体/颜色/坐标、所有文字和业务拓扑。scene 的差异只有这 16 项 roughness，不改文字版语义。原 pinned renderer 重试后导出 SVG 与 4× PNG，实际打开新 PNG，框线轻微手绘，授权出口及下方红字没有穿线；保持关口图而非套层级卡片。PNG 5172 × 2712；A4 估算 168 × 88 mm，最小 8.8 pt。生成器连续重建哈希一致。未启动 Gateway 或验证权限竞态。

### 本代理返修的最终状态

| 图 | scene / SVG / PNG | 实际新 PNG 目视 | A4 几何最小字号 | 下一道验收 |
| --- | --- | --- | --- | --- |
| loop-and-stop | 已同步 | 已检查 | 9.9 pt | 合稿实页 |
| codex-exec-approval | 已同步 | 已检查 | 8.7 pt | 合稿实页 |
| gpt-researcher-evidence | 已同步 | 已检查 | 9.2 pt | 合稿实页 |
| openclaw-session-gates | 已同步 | 已检查 | 8.8 pt | 合稿实页 |

四图运行 `check_figure_legibility.py --strict` 无几何标记；`check_repo.py` 及本代理修改范围的 `git diff --check` 通过。导出期间出现多次 CDN 启动超时，均重试原 pinned renderer；最终四图都有新 SVG 和新 4× PNG，没有混用旧 PNG 冒充验收，没有改 renderer，也没有提交或推送。其余交主代理返修的观察/评测、Agent loop、MiMo、OpenHands，仍需主代理单独记录结果；本报告的初始问题保留，不代替它们的复核。
