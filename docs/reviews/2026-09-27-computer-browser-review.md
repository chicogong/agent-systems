# Computer / Browser Use：来源与图意二审

日期：2026-09-27。审查对象：[机制草稿](../concepts/computer-and-browser-use.md)、[图的文字版](../../figures/computer-browser-use/README.md)与实际本地 PNG。仅新增本评审，不改主稿、图或公共索引。审稿者没有参与该机制稿与图的创作；另检查的 sandbox 图由本审稿者参与创作，属于**作者自查，不算独立二审**。

## 结论

未发现身份、截图缩放、观察通道、服务端结果证据等核心主张的阻断性事实错误。入预览前建议修正下列两处教学表达；当前不是运行任务或终审通过记录。

### P2：刷新后仍可能继续执行旧提案

位置：机制稿“一个只填表、不提交的任务”的伪逻辑，审查时第 39 行。

```text
if target_or_focus_changed(): refresh_and_replan()
result = host_execute(proposal)
```

触发：已得到提案后目标或焦点发生变化。影响：刷新/重规划返回值没有重绑定到 `proposal`，也未显式跳过本轮，读者按伪逻辑顺序会理解成继续执行旧提案。正文已正确要求重新观察，但示例控制流没有落实该要求。

最小修改：将刷新分支写成独立多行并 `continue`，下一轮重新观察和提案；或明确取得新提案并重跑范围/权限/当前状态校验，不只替换动作后立即执行。它标为不可运行教学伪逻辑，不是声称已发现某个上游工具的生产漏洞。

### P2：图中的回路需要显式注明继续条件

位置：实际 PNG 底部绿色虚线“下一轮：刷新观察与定位”。

触发：读者看到“结果符合任务吗？”后，仅有回观察区的箭头。影响：可能理解为即使满足完成标准也必须继续操作；文字版已说明可以结束，但主图的停止合同仍偏隐含。

最小修改：将回路标为“未满足停止条件 → 下一轮”，或增加短的“满足条件 → 结束并报告”出口。无需塞进另一套完整状态机，也不要把“工具成功”接成自动完成出口。改图后同步图源、SVG、PNG和文字版，再看实际 PNG。

## 逐项来源核对

| 重点 | 本轮重新核对的证据 | 结论 |
| --- | --- | --- |
| 应用执行动作，不是模型直接接管 OS | [Anthropic Computer Use 执行循环](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool#how-computer-use-works) | 官方文档将工具调用交由应用运行、返回结果；草稿表述成立。 |
| 缩放截图与真实屏幕坐标要转换 | [固定版 computer.py](https://github.com/anthropics/claude-quickstarts/blob/dee71163217524eed07d79d00ffea5a7d02cedda/computer-use-demo/computer_use_demo/tools/computer.py) | 重新阅读固定源码内容，`screenshot_size()` 与 `scale_coordinates()` 区分截图/API坐标和屏幕坐标；草稿没有声称所有工具都有同名 API。 |
| 隔离 BrowserContext/profile 不等于没有身份 | [固定版 Playwright MCP profile](https://github.com/microsoft/playwright-mcp/blob/e87bb897e15a6f2af402afb0f10b45eced9e1f9b/README.md#user-profile)与[Playwright auth](https://playwright.dev/docs/auth) | 隔离模式可通过 `contextOptions` 或 `--storage-state`载入状态；官方明确警告认证状态可冒用账号。草稿成立。 |
| DOM、浏览器 AX、截图、协议和原生 AX 是不同能力 | [Playwright MCP 工具](https://github.com/microsoft/playwright-mcp/blob/e87bb897e15a6f2af402afb0f10b45eced9e1f9b/README.md#tools)、[CDP](https://chromedevtools.github.io/devtools-protocol/)、[Apple 归档模型](https://developer.apple.com/library/archive/documentation/Accessibility/Conceptual/AccessibilityMacOSX/OSXAXModel.html) | 快照、截图、浏览器域命令和原生控件接口分别有第一方证据；组合是教学建议，不应推成每个工具均支持每个通道。正文已明确此边界。 |
| 浏览器数据可被 MCP 客户端读取和修改 | [固定版 Chrome DevTools MCP disclaimer](https://github.com/ChromeDevTools/chrome-devtools-mcp/blob/ae0aaef884c41445d83f86f099ef211f4584b791/README.md#disclaimers) | 官方明确暴露浏览器内容与数据，草稿没有把协议层当沙箱。 |
| allowed/blocked origins 不是安全隔离 | [固定版 Playwright MCP 配置](https://github.com/microsoft/playwright-mcp/blob/e87bb897e15a6f2af402afb0f10b45eced9e1f9b/README.md#configuration) | 重新读到两项明确写“不是安全边界、不影响重定向”；草稿成立。 |
| 网页/图像指令可能构成提示注入 | [Anthropic 安全说明](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool#security-considerations) | 官方建议最小权限、敏感数据隔离、域名限制与重要后果人工确认；本书“材料不是新授权”是清楚的工程边界。 |
| 环境能够运行，不等于任意任务自动验收 | [BrowserGym 固定 `OpenEndedTask.validate()`](https://github.com/ServiceNow/BrowserGym/blob/9e779f087de9a65668b6974d11f9ce9816026e96/browsergym/core/src/browsergym/core/task.py#L101-L111)、[OSWorld 原始论文](https://arxiv.org/abs/2404.07972) | 前者只遇用户 `exit` 后结束且奖励保持零；原始 raw 第 101–111 行已核对。后者提供任务初态与 execution-based 判据；草稿不引用历史分数排当前产品。 |

自动保存例外属于本书演示前提与工程建议，不是声称所有页面自动保存，也不是声称某个 SDK 能统一阻止它。正文明确“禁用自动保存与真实账号”；这让 `filled_not_submitted` 只表示受控演示中的填写结果，而非无任何网络副作用或完成报名。

网络取得方式与范围：优先重新取固定 raw 源与第一方文档。直接 raw 下载出现超时，GitHub contents API 返回 403；改用 Exa fetch 读取相同固定 raw 内容，不更换版本。**computer.py 的语义已核对，但本二审没有成功逐行重算其原始 `#L230-L302` 范围**，也没有依据网页抽取行号擅改链接。Playwright MCP 的 profile、origin 配置、snapshot、screenshot 章节已定点全文重读；Browser Use 的超时/多动作路径本轮对读了现有剖面，未重复下载该系统的全部固定源码。不能把本记录说成全链路源码审计。

## 实际图片检查

- 已通过 `view_image` 打开 Computer / Browser 的本地最终 PNG：4352×2780，字号层级清楚，两通道汇入动作提案，宿主拒绝路径、重新观察与读回路径可分辨；未见明显裁切、文字压箭头或重叠。唯一图意补强为上面的停止条件。
- 同时已打开 sandbox 的最新本地 PNG：4760×3024，资源合同、执行环境、账本/验收、结束环境、远端状态可辨识；验收标签在竖箭头右侧，橙色虚线明确是条件出网。没有把本地环境清理接成远端回滚。该项是作者自查。
- 共用 A4 几何检查对 Computer / Browser 估计最小字约 9.6 pt、约 658 PPI；这只是尺寸估计，不是 A4 PDF 页或纸样检查。
- 未查看实际 MCP 画布，不声称字体、坐标或像素与本地导出一致；未执行截图点击、DOM 填写或有账号页面任务。

审查快照 SHA-256：机制稿 `7e6f9e9d4b86c8a9d75787961c5f31f5a73f47b7d8ec59268d4f199e665dd9a2`；Computer / Browser PNG `788d43c42f67f2500fbd4eb4a132225eae76b0f4d5183fab60332d95b22707aa`；sandbox PNG `08987ecc16a29a1ad7b6ec731c5a46df4f3528cff888afe5ebb5f8eb62ab3043`。合稿后若文字或图发生修订，须另记修订的复核结果，不能沿用本快照声称自动通过。

## 仍需验收的缺口

1. 修正旧提案控制流与图的停止条件，再复核源码稿和最终 PNG。
2. 用完全本地、无账号、无自动保存的表单补可运行练习：动态移位/焦点变化、重复元素、自动保存反例、未获准提交、读回核对；不要直接拿真实报名或后台页面作练习。
3. 表单验收要区分字段读回、提交动作记录与服务端业务状态；截图和工具回执不能互相代替。网络副作用判据应由测试环境明确记录，不能仅证明“没点提交按钮”。
4. 新章进入书序后再查实际 Markdown 阅读包、390 px 网页与 PDF 含图页；本二审未做这些界面验收，也不是非作者真人试读。
