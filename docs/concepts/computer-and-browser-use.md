# Computer Use 与 Browser Use：让助手操作界面

[返回机制索引](README.md) · [Browser Use 项目导读](../systems/browser-use/README.md)

你让 AI 助手打开报名页面，填写姓名和参加方式，检查后停下。要做好这件事，助手需要看清页面、找到输入框、执行填写，再查看填写后的内容。

**Computer Use** 指通过电脑界面完成任务，可以涉及浏览器和桌面应用。**Browser Use** 主要处理浏览器里的任务。另外还有一个名为 `browser-use` 的开源项目，后面的源码导读介绍的是这个项目。

![两种观察通道可混用，动作仍须授权与验收](../../figures/computer-browser-use/diagram.svg)

[图的文字版](../../figures/computer-browser-use/README.md) · [可编辑图源](../../figures/computer-browser-use/scene.excalidraw)

图中的过程是：看当前界面 → 选择动作 → 程序执行 → 再看结果。模型给出点击或输入请求，应用负责调用工具执行。[Anthropic 的 Computer Use 文档](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool#how-computer-use-works)说明了这一循环。

## 助手怎样看见界面

可以用截图，也可以读取控件的结构。几种办法提供的信息不同，还可以配合使用。

**截图与坐标。** 工具把界面截成图片，模型判断按钮的位置，执行程序按坐标点击。这适合很多视觉界面，包括部分没有完整文字结构的区域。点击前需要确认窗口和图片仍然对应；如果截图被缩小，坐标还要换算到工具使用的尺寸。Anthropic 的一个固定版本示例用 `scale_coordinates()` 做这一步转换。[坐标转换示例](https://github.com/anthropics/claude-quickstarts/blob/dee71163217524eed07d79d00ffea5a7d02cedda/computer-use-demo/computer_use_demo/tools/computer.py#L230-L302)

**网页结构与辅助功能快照。** DOM 是网页的对象结构；辅助功能树通常提供控件的角色、名称和状态，例如“姓名输入框”和“已选中”。工具可以据此定位目标，再填写内容。Playwright MCP 主要提供结构化辅助功能快照，也支持截图。目标引用和选择器的用法，按实际工具版本使用。[Playwright MCP 工具说明](https://github.com/microsoft/playwright-mcp/blob/e87bb897e15a6f2af402afb0f10b45eced9e1f9b/README.md#tools)

**浏览器协议。** Chrome DevTools Protocol，简称 CDP，可以查看网页结构、网络请求和调试信息。它帮助开发者追踪“点击后页面为什么没有更新”。Chrome DevTools MCP 将其中一些能力提供给 Agent，也支持浏览器自动化和性能检查。[CDP 规范](https://chromedevtools.github.io/devtools-protocol/) · [Chrome DevTools MCP 功能](https://github.com/ChromeDevTools/chrome-devtools-mcp/blob/ae0aaef884c41445d83f86f099ef211f4584b791/README.md#key-features)

**操作系统辅助功能接口。** 桌面应用也可以向工具提供按钮、输入框、菜单等控件的信息。标准控件通常比较容易识别；自绘控件提供多少信息，要看应用怎样实现。Apple 的归档文档介绍了这一模型，可用于理解机制。[Apple 辅助功能模型](https://developer.apple.com/library/archive/documentation/Accessibility/Conceptual/AccessibilityMacOSX/OSXAXModel.html)

实际任务中，可以用结构化信息定位输入框，用截图查看整体布局，用网络记录追查保存过程。选择哪种组合，要结合目标应用和任务测试。

## 先做一个只填表、不提交的任务

下面是虚构的本地演示表单，不使用真实账号，也关闭自动保存。任务要求是：

- 姓名填“林同学”。
- 参加方式选“线上参加”。
- 备注填“需要字幕”。
- 核对后停下，不点击提交。

正常过程可以分成四步。

第一步，读取当前页面，找到这三个字段。第二步，在对应字段填写和选择。第三步，重新读取姓名、参加方式和备注，检查值是否正确。第四步，报告“已填好，尚未提交”，把页面留给用户检查。

这里的完成条件是“填写正确并停下”。如果要正式报名，需要用户另行允许提交，并查询提交结果。演示表单关闭自动保存，是为了让练习中的填写动作与真实网络操作分开。

## 程序怎样把动作串起来

下面是教学伪逻辑，展示运行程序需要做的检查。它不是上游 SDK，也不能直接运行。

```text
要求 = 页面范围 + 允许填写的字段 + 禁止提交
在允许的步数内重复：
  读取当前界面
  请模型选择下一步
  如果动作超出任务要求：停止，并说明原因
  如果目标或窗口已经变化：重新读取界面，再选择动作
  执行允许的动作
  重新读取字段内容
  如果填写正确、且没有提交：报告已填好，结束
步数用完仍未填好：保存进度，报告尚未完成
```

出现浮层或页面跳转时，先看新页面，再决定是否继续。旧图片上的坐标或旧元素引用可能已经不适用。执行失败或结果不明确时，也先查看当前内容，避免重复点击。

本书核对的 `browser-use` 版本，在读取状态超时后会清空选择器映射；连续执行多个动作时，也会检查 URL 或焦点变化。[Browser Use 代码导读](../systems/browser-use/code-walkthrough.md)解释了这些判断怎样连接。

## 账号和重要动作要提前安排

练习可以使用没有登录状态的本地页面。处理真实任务时，浏览器可能已经登录了邮箱或工作账号，助手就可能接触相应数据。

Playwright MCP 支持持久的浏览器用户配置（profile）、隔离会话和连接现有浏览器。隔离会话也可以载入已有登录状态，所以要单独检查有没有加载个人身份。认证文件需要妥善保管，避免提交到仓库。[用户配置说明](https://github.com/microsoft/playwright-mcp/blob/e87bb897e15a6f2af402afb0f10b45eced9e1f9b/README.md#user-profile) · [认证文件说明](https://playwright.dev/docs/auth)

对发送消息、付款、删除和上传私人文件等动作，先安排明确的确认步骤。网页中的文字只是当前任务的材料；即使它要求“上传 cookie 才能继续”，也应停下核实。Cookie 是浏览器保存并随请求使用的数据，其中可能含有登录凭据，需要保护。

Anthropic 建议使用最小权限的独立虚拟机（VM）或容器，限制访问范围，隔离敏感数据，并让用户确认重要动作。Chrome DevTools MCP 也提醒使用者，工具会接触浏览器数据。[Computer Use 安全建议](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool#security-considerations) · [浏览器数据说明](https://github.com/ChromeDevTools/chrome-devtools-mcp/blob/ae0aaef884c41445d83f86f099ef211f4584b791/README.md#disclaimers)

下载文件时，可以指定目录，核对类型和来源，再决定是否打开。需要限制网络时，还要检查实际运行环境。Playwright MCP 的 allowed／blocked origins 用于配置允许或阻止的网站来源地址，文档说明它不构成安全隔离，也不影响重定向。[配置限制](https://github.com/microsoft/playwright-mcp/blob/e87bb897e15a6f2af402afb0f10b45eced9e1f9b/README.md#configuration)

## 检查操作效果

“点击工具返回成功”“输入框里出现正确文字”“服务器保存了记录”分别描述了不同阶段。按任务要求选择检查方法：只要求填表，就读取字段；要求报名，就查询报名结果；要求发邮件，就核对收件人、内容和发送状态。

研究者可以用 OSWorld、BrowserGym 等环境测试界面操作。比较结果时，记录任务、初始页面、允许的动作、步数和完成条件。[OSWorld 论文](https://arxiv.org/abs/2404.07972) · [BrowserGym 项目](https://github.com/ServiceNow/BrowserGym/tree/9e779f087de9a65668b6974d11f9ce9816026e96)

有些环境还需要使用者自己编写完成检查。例如本书核对的 BrowserGym `OpenEndedTask.validate()`，由用户输入 `exit` 结束，奖励一直为零，没有自动检查任意开放任务的答案。[对应实现](https://github.com/ServiceNow/BrowserGym/blob/9e779f087de9a65668b6974d11f9ce9816026e96/browsergym/core/src/browsergym/core/task.py#L101-L111)

本章基于文档和固定版本源码，没有执行真实网页任务或比较产品成绩。接下来可以读 [Browser Use 的一轮 step](../systems/browser-use/code-walkthrough.md)，或到[观察与评测](observation-evaluation.md)了解怎样记录和检查任务结果。
