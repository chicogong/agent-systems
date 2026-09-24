# 跟着 browser-use 的 `Agent.step()` 走一轮

[返回剖面](README.md) · 固定源码 [`d8110c5`](https://github.com/browser-use/browser-use/tree/d8110c5ff87ccba887aaa726cdb780f2f84bef8d)

以下是教学用执行顺序，不是项目源码逐字复刻，也不代表异常、并发事件只有这一种时序。

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

1. `_prepare_context()` 调用 `BrowserSession.get_browser_state_summary(include_screenshot=True)`，检查下载、更新页面相关动作，再让消息管理器准备上一轮结果并构造当前状态消息；是否把截图置入模型消息由 `use_vision` 控制。[上下文准备](https://github.com/browser-use/browser-use/blob/d8110c5ff87ccba887aaa726cdb780f2f84bef8d/browser_use/agent/service.py#L1087-L1160) · [截图条件](https://github.com/browser-use/browser-use/blob/d8110c5ff87ccba887aaa726cdb780f2f84bef8d/browser_use/agent/message_manager/service.py#L449-L502)
2. 状态摘要不是简单读取一个缓存字段；`BrowserSession` 派发 `BrowserStateRequestEvent` 并等待结果。超时会清空选择器映射，回退到含错误的非可操作摘要。这说明观测失败时不能安全地沿用旧 DOM 索引。[状态请求与超时](https://github.com/browser-use/browser-use/blob/d8110c5ff87ccba887aaa726cdb780f2f84bef8d/browser_use/browser/session.py#L1595-L1679)
3. `_get_next_action()` 从消息管理器取得输入，带超时调用模型输出重试包装，将 `AgentOutput` 放进 `last_model_output`；`_execute_actions()` 把其中动作列表交给 `multi_act()`，并保存 `last_result`。[模型阶段](https://github.com/browser-use/browser-use/blob/d8110c5ff87ccba887aaa726cdb780f2f84bef8d/browser_use/agent/service.py#L1175-L1217)
4. `multi_act()` 逐一调用 `Tools.act()`。它在余下动作存在时检查注册动作的 `terminates_sequence` 与动作前后 URL/焦点目标变化；结果完成或报错也会提前停止。`Tools.act()` 再通过动作注册表执行实际动作，使用每动作超时，并把常见异常转成 `ActionResult(error=...)`。[多动作守卫](https://github.com/browser-use/browser-use/blob/d8110c5ff87ccba887aaa726cdb780f2f84bef8d/browser_use/agent/service.py#L2730-L2828) · [工具分发](https://github.com/browser-use/browser-use/blob/d8110c5ff87ccba887aaa726cdb780f2f84bef8d/browser_use/tools/service.py#L2178-L2253)
5. `_finalize()` 先要求 `last_result` 存在；只有当前浏览器摘要也可用时，才调用 `_make_history_item()`。后者从摘要保存 URL、标题、标签页、交互元素和可用截图路径，并与模型输出、动作结果、step 元数据组成 `AgentHistory`。有摘要和模型输出时，`_finalize()` 还派发 `CreateAgentStepEvent`。[最终处理](https://github.com/browser-use/browser-use/blob/d8110c5ff87ccba887aaa726cdb780f2f84bef8d/browser_use/agent/service.py#L1356-L1415) · [历史项构造](https://github.com/browser-use/browser-use/blob/d8110c5ff87ccba887aaa726cdb780f2f84bef8d/browser_use/agent/service.py#L1738-L1780)

这里的历史项保存的是该 step 采集的状态摘要和执行结果，不等同于动作后重新抓取的完整网页快照；下一步会再调用 `_prepare_context()` 获取浏览器状态。这个区分来自 `step()` 的调用顺序和 `_make_history_item()` 的入参，尚未用运行日志验证。[调用顺序](https://github.com/browser-use/browser-use/blob/d8110c5ff87ccba887aaa726cdb780f2f84bef8d/browser_use/agent/service.py#L1063-L1085) · [入参](https://github.com/browser-use/browser-use/blob/d8110c5ff87ccba887aaa726cdb780f2f84bef8d/browser_use/agent/service.py#L1378-L1385)
