# 跟着 OpenHands SDK 走完一条事件闭环

> Synthesized concept page maintained by Aimake LLM Wiki.

## Key Evidence & Provenance

### Source Snapshot (2026-11-22)
- **Origin**: `/Users/haorangong/Github/chicogong/experiments/agent-systems/docs/systems/openhands/code-walkthrough.md`
- **SHA-256**: `951ce400f25d09be` · Raw: [[../raw/2026-11-22-跟着-openhands-sdk-走完一条事件闭环.md|2026-11-22-跟着-openhands-sdk-走完一条事件闭环.md]]
- 如果在接入 OpenHands SDK 时，外层服务看到 `run()` 返回就顺手再调一次 `run()`，会发生什么？答案是：原本停下来等待人工审批的高危工具调用，会被立刻放行执行。
- 为什么会这样？顺着同步 `LocalConversation.run()` 与默认 `Agent.step()` 的真实调用链走一遍，就能看清事件入账、确认挂起、批次执行与异常收尾的每一处咬合细节。
- send_message() → MessageEvent → _on_event() [先 append_event 落账，再广播订阅者]
- LocalConversation.run() 循环调用 Agent.step()
- ├─ 分支 A：当前分支存在未配对 ActionEvent → 直接 _execute_actions() 清偿待办
