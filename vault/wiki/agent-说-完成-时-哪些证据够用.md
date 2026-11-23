# Agent 说“完成”时，哪些证据够用？

> Synthesized concept page maintained by Aimake LLM Wiki.

## Key Evidence & Provenance

### Source Snapshot (2026-11-22)
- **Origin**: `/Users/haorangong/Github/chicogong/experiments/agent-systems/docs/comparisons/completion-and-evidence.md`
- **SHA-256**: `6cea0fce25f0db85` · Raw: [[../raw/2026-11-22-agent-说-完成-时-哪些证据够用.md|2026-11-22-agent-说-完成-时-哪些证据够用.md]]
- 在日常协作里，Agent 最具迷惑性的时刻，往往就是它语气笃定地吐出最后一段总结的那一刻：“已完成全部修改！服务超时已按要求调为 5 秒，相关单元测试全部运行通过，未执行任何远端推送。”
- 如果你只看这句漂亮的自然语言汇报就点下合并，线上事故往往已经在路上了：打开 `git diff` 一看，它在把 `timeout: 30` 改成 `timeout: 5` 的同时，顺手把下一行的 `retries: 3` 覆盖成了 `retries: 0`；而跑绿的那条单测只写了 `assert config.timeout == 5`，压根没检查重试次数，
- 在《一轮工具调用后，谁决定下一步？》里我们看清了程序怎样停下来；本篇专门解决停下来之后的灵魂追问：**为什么“循环正常结束”和“工具返回成功”都不等于“任务真做对了”？到底拿到哪几样硬证据，才能放心签收 Agent 的交付物**？
- 来看一条再常见不过的配置修改需求：
- 把服务请求超时从 30 秒改成 5 秒，保持现有的重试规则（retries=3）不变；
