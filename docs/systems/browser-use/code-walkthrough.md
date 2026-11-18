# 跟着 browser-use 的 `Agent.step()` 走一轮

[返回首页](README.md) · 固定源码 [`d8110c5`](https://github.com/browser-use/browser-use/tree/d8110c5ff87ccba887aaa726cdb780f2f84bef8d)

翻开 `Agent.step()` 的源码，有两处细节最值得细品：第一，上一轮的 `last_result` 为什么不在上一轮末尾清零，非要拖到本轮 `_prepare_context()` 之后才清空？第二，为什么 `_finalize(summary)` 必须包在 `finally` 块里，还要反复核对 `last_result` 和 `summary` 是否齐全？

顺着下面这条骨架走一遍，这两个状态生命周期的设计意图就会一目了然：

```text
step():
  summary = _prepare_context()           // 采集当前页摘要 + 把「上一步 last_result」拼进本轮模型输入
  clear(last_model_output, last_result)   // 旧结果已完成使命，此刻清零，防止本轮中途失败时串入脏数据
  _get_next_action(summary)               // 带超时与重试请求模型，产出结构化 AgentOutput.action
  _execute_actions()                      // multi_act() → Tools.act() 逐项执行并检测跳变熔断
  _post_process()                         // 检查文件下载、更新计划与连续失败计数
finally:
  _finalize(summary)                      // 仅当 summary 与本轮新 last_result 俱全时写入 AgentHistory
```

## 1. 准备上下文：交接上一步反馈，防住超时脏索引

`_prepare_context()` 先调用 `BrowserSession.get_browser_state_summary(include_screenshot=True)` 拉取带截图的当前页面摘要，顺带检查下载文件、刷新与当前页面绑定的动态动作定义，然后通知消息管理器把**上一步留下的执行结果**（`last_result`）与**当前页面摘要**组装成模型输入。正因为本轮提示词依赖上一步的执行结果，`last_result` 必须活到 `_prepare_context()` 结束之后才能安全清零。[准备模型输入](https://github.com/browser-use/browser-use/blob/d8110c5ff87ccba887aaa726cdb780f2f84bef8d/browser_use/agent/service.py#L1087-L1160)

消息管理器拼装多模态内容时，通过 `use_vision` 控制图片 token 预算：页面摘要带有截图时，`True` 直接把图片塞入消息，`False` 完全忽略图片，而 `"auto"` 只在上一步动作结果明确要求看图时才附带截图。[选择截图输入](https://github.com/browser-use/browser-use/blob/d8110c5ff87ccba887aaa726cdb780f2f84bef8d/browser_use/agent/message_manager/service.py#L449-L502)

而在底层浏览器侧，`BrowserSession` 通过发出 `BrowserStateRequestEvent` 采集 DOM 与可交互元素映射。一旦页面卡死导致状态采集超时，它会立刻清空缓存的元素查找表（selector map），返回一份标明错误的降级摘要——宁可让模型这一轮「看不见按钮」等待重试，也绝不允许模型用上一页的残留编号误点当前页。[获取状态和处理超时](https://github.com/browser-use/browser-use/blob/d8110c5ff87ccba887aaa726cdb780f2f84bef8d/browser_use/browser/session.py#L1595-L1679)

## 2. 决策与执行：异常转结构化结果，页面一变立刻停手

拿到消息后，`_get_next_action()` 通过带超时与重试保护的模型接口取得结构化输出 `AgentOutput`，存入 `last_model_output`；紧接着 `_execute_actions()` 把其中的动作数组交给 `multi_act()` 执行，并将返回列表写入 `last_result`。[请求模型并取出动作](https://github.com/browser-use/browser-use/blob/d8110c5ff87ccba887aaa726cdb780f2f84bef8d/browser_use/agent/service.py#L1175-L1217)

单步执行落脚在 `Tools.act()`：它在动作注册表里查出目标函数，套上单动作超时保护后调用底层浏览器接口；常见的元素失效或执行报错不会直接炸穿主循环，而是被捕获封装成带错误信息的 `ActionResult` 返回给下一轮模型调整策略。[执行实际动作](https://github.com/browser-use/browser-use/blob/d8110c5ff87ccba887aaa726cdb780f2f84bef8d/browser_use/tools/service.py#L2178-L2253)

当一次输出包含多个连续动作时，`multi_act()` 每执行完一项就会做一次「能否继续」的安全体检：

- 该动作自身标记了 `terminates_sequence`（要求独占本轮结尾）；
- 点击或输入触发了**页面 URL 改变或焦点目标切换**（说明原页面快照的索引可能已失效）；
- 当前动作返回错误，或产出了代表整项任务完结的 `is_done` 标记。

只要命中上面任何一条，剩余未执行的动作当场作废；只有前一项正常完成且页面未发生跳变时，才会顺延执行下一项。[检查继续条件](https://github.com/browser-use/browser-use/blob/d8110c5ff87ccba887aaa726cdb780f2f84bef8d/browser_use/agent/service.py#L2730-L2828)

## 3. 收尾归档：因果配对写入历史，新页面留给下一轮观察

无论正流程顺利跑完还是中途抛错，控制流最终都会进入 `finally` 里的 `_finalize(summary)`。也正因为开头已经提前清空了上一轮的旧 `last_result`，`_finalize()` 只需检查本轮是否同时拿到了新的 `last_result` 与浏览器摘要 `summary`：两者齐全才调用 `_make_history_item()`，把 URL、标题、标签页、交互元素与截图路径打包，再与 `last_model_output`、`last_result` 及耗时元数据合成一条完整的 `AgentHistory`。若摘要与模型输出均就绪，还会同步广播 `CreateAgentStepEvent` 供外部监听。[收尾处理](https://github.com/browser-use/browser-use/blob/d8110c5ff87ccba887aaa726cdb780f2f84bef8d/browser_use/agent/service.py#L1356-L1415) · [组成历史记录](https://github.com/browser-use/browser-use/blob/d8110c5ff87ccba887aaa726cdb780f2f84bef8d/browser_use/agent/service.py#L1738-L1780)

注意这里传给 `_finalize(summary)` 的始终是**本轮动作执行前**采集到的那份页面摘要。这样回放任意一步 `AgentHistory` 时，读者看到的都是严丝合缝的决策现场：「当时页面长这样 → 模型据此决定点这里 → 得到了这样的 `ActionResult`」；至于点击之后长什么样，将由下一轮 `step()` 开头的 `_prepare_context()` 重新揭晓。[观察与执行的顺序](https://github.com/browser-use/browser-use/blob/d8110c5ff87ccba887aaa726cdb780f2f84bef8d/browser_use/agent/service.py#L1063-L1085) · [传入哪份摘要](https://github.com/browser-use/browser-use/blob/d8110c5ff87ccba887aaa726cdb780f2f84bef8d/browser_use/agent/service.py#L1378-L1385)

## 来源与边界

本篇导读依据 [`browser-use/browser-use@d8110c5ff87ccba887aaa726cdb780f2f84bef8d`](https://github.com/browser-use/browser-use/tree/d8110c5ff87ccba887aaa726cdb780f2f84bef8d) 静态追踪 `Agent.step()` 及其下游调用链；并发浏览器事件、外部暂停信号与特定站点的异步加载时序需结合运行日志另行核验。
