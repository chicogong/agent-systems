# DSH 代码导读：深挖工具批次的并发池、顺序提交与缺省拒绝

> Synthesized concept page maintained by Aimake LLM Wiki.

## Key Evidence & Provenance

### Source Snapshot (2026-11-22)
- **Origin**: `/Users/haorangong/Github/chicogong/experiments/agent-systems/docs/systems/dsh/code-walkthrough.md`
- **SHA-256**: `348ca23773972267` · Raw: [[../raw/2026-11-22-dsh-代码导读-深挖工具批次的并发池-顺序提交与缺省拒绝.md|2026-11-22-dsh-代码导读-深挖工具批次的并发池-顺序提交与缺省拒绝.md]]
- 模型一轮吐出一串工具调用时，如果简单写个 `for...of` 串行 `await`，I/O 密集型搜索会慢如蜗牛；如果粗暴包一层 `Promise.all`，模型一口气生成 30 个命令就能瞬间打爆本地子进程句柄，而且谁快谁先写日志会导致调用与回执错位，遇到半途取消还会留下没人收尸的孤儿任务。
- 这一篇我们直接钻进 DSH 的 `agent-loop`、`tools` 与 `bash-sandbox` 三个核心包，沿着 `A`、`B`、`C` 三次调用的真实流转，看它怎样用六个环环相扣的函数管住并发、顺序、审批与收尾。
- 入口函数 `executeToolCalls()` 拿到模型开出的一批调用后，先定位发起调用的 Agent 与会话上下文，随后检查每个工具声明的执行模式。
- 它不会把所有调用一锅炖：允许并行的连续调用会被归入同一个并发组；一旦遇到要求独占执行的工具（例如可能引发状态冲突的写操作），就会单独切组串行执行。更细腻的一点是，程序在推进后续组时还会**重新读取执行模式**——因为前一组工具的执行完全可能改变环境状态或工具可用配置，动态重查避免了拿过期的静态假设去跑后面的步骤。
- 进入同一个并发组后，`runGroup()` 用一个有界并发池限制同时在跑的任务上限，防止模型突发海量调用冲垮宿主资源。
