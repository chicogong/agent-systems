# 跟着 browser-use 的 `Agent.step()` 走一轮

[返回首页](README.md) · 固定源码 [`d8110c5`](https://github.com/browser-use/browser-use/tree/d8110c5ff87ccba887aaa726cdb780f2f84bef8d)

继续看网页助手的一轮工作。它先获取当前页面，模型据此提出动作，程序逐项执行，再把本轮输入和执行结果放在一起保存。下面的摘要帮助定位函数，具体行为依据固定源码。

```text
step():
  summary = _prepare_context()           # BrowserSession 当前状态
  clear(last_model_output, last_result)   # 保留前一步结果用于构造提示后再清
  _get_next_action(summary)               # 模型返回 AgentOutput.action
  _execute_actions()                      # multi_act → Tools.act
  _post_process()                         # 下载、计划、失败计数等
finally:
  _finalize(summary)                      # 有 last_result 且 summary 时记录 AgentHistory
```

## 先把当前网页和上一步结果交给模型

`_prepare_context()` 请求 `BrowserSession.get_browser_state_summary(include_screenshot=True)`，也就是带截图的当前网页摘要。它还检查下载、更新页面相关动作，再让消息管理器把前一步结果和当前状态整理成消息。[准备模型输入](https://github.com/browser-use/browser-use/blob/d8110c5ff87ccba887aaa726cdb780f2f84bef8d/browser_use/agent/service.py#L1087-L1160)

有可用截图时，`use_vision=True` 会把它加入模型消息，`False` 会省略它，`"auto"` 只在动作结果明确要求截图时加入。[选择截图输入](https://github.com/browser-use/browser-use/blob/d8110c5ff87ccba887aaa726cdb780f2f84bef8d/browser_use/agent/message_manager/service.py#L449-L502)

`BrowserSession` 通过状态请求事件 `BrowserStateRequestEvent` 获取摘要。请求超时时，会清空元素查找映射，并返回带错误的状态。旧页面的元素索引暂时不可用，需要重新取得可用状态后再按索引操作。[获取状态和处理超时](https://github.com/browser-use/browser-use/blob/d8110c5ff87ccba887aaa726cdb780f2f84bef8d/browser_use/browser/session.py#L1595-L1679)

## 模型提出动作，程序逐项执行

`_get_next_action()` 从消息管理器取出输入，通过带超时和重试处理的接口请求模型。模型输出 `AgentOutput` 存入 `last_model_output`；`_execute_actions()` 把其中的动作列表交给 `multi_act()`，执行结果存入 `last_result`。[请求模型并取出动作](https://github.com/browser-use/browser-use/blob/d8110c5ff87ccba887aaa726cdb780f2f84bef8d/browser_use/agent/service.py#L1175-L1217)

`multi_act()` 逐个调用 `Tools.act()`。`Tools.act()` 在动作注册表中找到对应实现，设置这次动作的超时，再执行；常见异常会整理成带错误信息的 `ActionResult`。[执行实际动作](https://github.com/browser-use/browser-use/blob/d8110c5ff87ccba887aaa726cdb780f2f84bef8d/browser_use/tools/service.py#L2178-L2253)

余下动作是否继续，还要看执行后的情况。`terminates_sequence` 表示该动作要求结束这一串动作；网页地址或焦点目标变化时，也会停止剩余项。报错或任务结束标记 `is_done` 同样会让序列停下；单个动作正常完成后，可以继续下一项。[检查继续条件](https://github.com/browser-use/browser-use/blob/d8110c5ff87ccba887aaa726cdb780f2f84bef8d/browser_use/agent/service.py#L2730-L2828)

## 保存的是本轮看到的页面，加上执行结果

`_finalize()` 先检查是否有 `last_result`。还要有浏览器摘要，才会调用 `_make_history_item()`，保存页面地址、标题、标签页、交互元素和可用截图路径，再与模型输出、动作结果和本轮信息组成 `AgentHistory`。有摘要和模型输出时，还会发出 `CreateAgentStepEvent`，通知其他组件这一轮的内容。[收尾处理](https://github.com/browser-use/browser-use/blob/d8110c5ff87ccba887aaa726cdb780f2f84bef8d/browser_use/agent/service.py#L1356-L1415) · [组成历史记录](https://github.com/browser-use/browser-use/blob/d8110c5ff87ccba887aaa726cdb780f2f84bef8d/browser_use/agent/service.py#L1738-L1780)

这里传入的是本轮执行前取得的摘要。要看动作之后的新页面，下一轮会重新调用 `_prepare_context()`。回看历史时，可以依次看“本轮采集了哪些页面信息、模型提出了哪些动作、执行结果是什么”。是否把其中的截图交给模型，还要看上面的 `use_vision` 条件。[观察与执行的顺序](https://github.com/browser-use/browser-use/blob/d8110c5ff87ccba887aaa726cdb780f2f84bef8d/browser_use/agent/service.py#L1063-L1085) · [传入哪份摘要](https://github.com/browser-use/browser-use/blob/d8110c5ff87ccba887aaa726cdb780f2f84bef8d/browser_use/agent/service.py#L1378-L1385)

本篇尚未用真实浏览器日志核对上述流程。实际超时、暂停和并发事件会影响具体时间顺序，截图是否取得也需要查看当次结果。
