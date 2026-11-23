---
title: "读懂 `DefaultAgent`：不到两百行代码如何把消息列表变成状态机"
origin: "/Users/haorangong/Github/chicogong/experiments/agent-systems/docs/systems/mini-swe-agent/code-walkthrough.md"
sha256: "22f5048bf4ef478fc398b7ea3e4c5319e3ccea244bef143279c89d9a48a6684a"
ingested_at: "2026-11-22T13:54:22.913Z"
tags: []
---

# 读懂 `DefaultAgent`：不到两百行代码如何把消息列表变成状态机

# 读懂 `DefaultAgent`：不到两百行代码如何把消息列表变成状态机

[返回首页](README.md) · 固定源码 [`04d809ce`](https://github.com/SWE-agent/mini-swe-agent/tree/04d809ceab9df28f9adaed044884180159172930)

在很多工程代码里，跨层传递停止原因是一件很啰嗦的事：`env.execute()` 得返回 `(output, is_submitted)`，`step()` 得返回 `(continue_flag, stop_reason)`，外层再写一串 `if/elif` 更新一堆实例属性，稍有疏漏就会出现「内存标志说停了，落盘日志却少记了最后一步」的分裂现场。

`mini-swe-agent` 的 `DefaultAgent` 之所以读起来像水晶一样通透，是因为它立下了两条极简铁律：**第一，所有运行状态只往 `self.messages` 里追加，绝不另设平行账本；第二，用携带消息字典的自定义异常跨越调用栈，把「预算超限」「交卷停机」和「格式报错」全部统一成「往列表末尾塞消息」这同一个动作**。

先把整台机器的浓缩骨架摊在桌面上：

```text
self.messages = [system, user(task)]
while True:
    try:
        step():
          ├─ query()           ──► 核查步数/成本/时长限额 → model.query(messages) → 追加 assistant 消息
          └─ execute_actions() ──► 逐条调 env.execute(action) → 渲染并追加观察消息
    except FormatError as e:
        未达连续错误阈值 ──► 追加格式纠错反馈消息（下一轮给模型自纠机会）
        达到连续错误阈值 ──► 追加 role="exit" (RepeatedFormatError)
    except InterruptAgentFlow as e:
        直接追加异常自带的控制消息（如 Submitted 或 LimitsExceeded 的 role="exit" 消息）
    except Exception as e:
        追加 role="exit" 崩溃记录，随后 raise 原样重抛
    finally:
        save()  ──► 若配置了 output_path，每轮雷打不动将最新轨迹写入磁盘

    if self.messages[-1]["role"] == "exit":
        return self.messages[-1]["extra"]
```

## 1. 正常推进闭环：四个函数如何接力

顺着正常干活的主干往下摸，四个核心函数各司其职、毫无赘肉：

- **外层驱动**（`run`）：初始化放入系统提示与用户任务后，循环调用 `step()`，每轮只在末尾盯住一件事——`self.messages[-1]` 的角色是不是 `"exit"`（见[启动循环](https://github.com/SWE-agent/mini-swe-agent/blob/04d809ceab9df28f9adaed044884180159172930/src/minisweagent/agents/default.py#L88-L124)）。
- **预算卡口与模型请求**（`query`）：`step()` 先调 `query()`。注意限额检查（总步数、累计 API 花费、已运行秒数）严格卡在**发起网络请求之前**，超标当场抛 `LimitsExceeded`，绝不多花一分冤枉钱；通过后才调用模型并把回复追加进列表（见[请求模型](https://github.com/SWE-agent/mini-swe-agent/blob/04d809ceab9df28f9adaed044884180159172930/src/minisweagent/agents/default.py#L126-L152)）。
- **单一工具约束与动作解析**（`LitellmModel`）：在常用实现 `LitellmModel` 中，系统只向大模型暴露一个 `bash` 工具，并把模型返回的工具调用解析成挂在助手消息 `extra.actions` 下的命令字典；只要模型没调工具、调了不存在的工具名或参数缺斤少两，解析器立即抛出 `FormatError`（见[模型接口](https://github.com/SWE-agent/mini-swe-agent/blob/04d809ceab9df28f9adaed044884180159172930/src/minisweagent/models/litellm_model.py#L64-L105)与[解析动作](https://github.com/SWE-agent/mini-swe-agent/blob/04d809ceab9df28f9adaed044884180159172930/src/minisweagent/models/utils/actions_toolcall.py#L30-L76)）。
- **子进程执行与观察回填**（`execute_actions`）：拿到动作列表后，`execute_actions()` 逐条交给 `env.execute` 在子进程中运行，收集输出与返回码（或超时异常），再由模型适配器的 `format_observation_messages()` 套上模板格式化成标准工具结果消息塞回 `self.messages`，供下一轮 `query()` 连同历史一并发给模型（见[执行动作](https://github.com/SWE-agent/mini-swe-agent/blob/04d809ceab9df28f9adaed044884180159172930/src/minisweagent/agents/default.py#L154-L157)、[整理结果消息](https://github.com/SWE-agent/mini-swe-agent/blob/04d809ceab9df28f9adaed044884180159172930/src/minisweagent/models/litellm_model.py#L140-L151)与[本地执行命令](https://github.com/SWE-agent/mini-swe-agent/blob/04d809ceab9df28f9adaed044884180159172930/src/minisweagent/environments/local.py#L24-L56)）。

看看一轮正常执行加一轮交卷停机后，`self.messages` 里流转的真实数据结构有多干净：

```json
[
  { "role": "system", "content": "You are a helpful assistant that can interact with a computer shell..." },
  { "role": "user", "content": "Fix the off-by-one bug in parse_range()..." },
  {
    "role": "assistant",
    "content": "Let's run pytest first.",
    "extra": { "actions": [{ "command": "pytest -q", "tool_call_id": "call_1" }] }
  },
  { "role": "tool", "tool_call_id": "call_1", "content": "returncode: 1\noutput: 1 failed, 12 passed in 0.14s" },
  {
    "role": "exit",
    "content": "patch内容...",
    "extra": { "exit_status": "Submitted", "submission": "patch内容..." }
  }
]
```

## 2. 为什么用 `InterruptAgentFlow` 异常做控制流

读[反馈、控制消息和错误](https://github.com/SWE-agent/mini-swe-agent/blob/04d809ceab9df28f9adaed044884180159172930/src/minisweagent/agents/default.py#L100-L124)那二十几行 `try...except` 时，重点体会它把三类完全不同的打断事件统一映射成消息的手法：

1. **可恢复的犯错**（`FormatError`）：大模型偶发漏掉工具调用时，异常对象本身就装着要训诫模型的纠错提示消息。外层捕获后往 `self.messages` 里一塞，连 `if` 分支都不用多写，循环自然进入下一轮让模型重答；同时维护连续格式错误计数，防止模型彻底坏死时无限空转。
2. **预期的流程中断**（`InterruptAgentFlow`）：不论是深藏在 `query()` 里的预算超标（`LimitsExceeded`），还是深藏在 `LocalEnvironment.execute()` 里的哨兵交卷（`Submitted`），它们都继承自 `InterruptAgentFlow` 并在抛出时直接揣好了构造完备的 `role="exit"` 消息。异常一抛，直接穿透中间层落到 `run()` 的捕获块里追加进 `self.messages`，瞬间触发停机。
3. **非预期的硬崩溃**（兜底 `Exception`）：哪怕碰上未知的底层 Bug，捕获块也会先把异常类型与堆栈记成一条 `role="exit"` 消息塞进账本，随后 `raise` 原样抛出——既不掩盖真实故障，又保证了崩溃前一刻的完整现场留在列表里。

## 3. 放在 `finally` 里的轨迹持久化：`save()`

最后看一眼收尾处的 [`save()`](https://github.com/SWE-agent/mini-swe-agent/blob/04d809ceab9df28f9adaed044884180159172930/src/minisweagent/agents/default.py#L159-L190)。为什么它没有放在 `while` 循环体外，而是塞在每一轮的 `finally` 块里？

因为跑复杂仓库修复任务动辄十几分钟，随时可能遇到进程被外部超时强杀、网络崩断或未捕获异常。每轮 `finally` 都调一次 `save()`，意味着只要你配置了非空的 `output_path`，磁盘上的轨迹文件就永远跟最新一轮的 `self.messages`（包括刚刚塞进去的那条崩溃或超限 `exit` 消息）保持同步；若未配置 `output_path`，`save()` 则只构造并返回内存字典而不写磁盘，方便纯内存单元测试直接断言。

## 来源与边界

本文基于官方仓库固定提交 [`SWE-agent/mini-swe-agent@04d809ceab9df28f9adaed044884180159172930`](https://github.com/SWE-agent/mini-swe-agent/tree/04d809ceab9df28f9adaed044884180159172930) 的静态源码分析整理。除本文剖析的 `LitellmModel` 工具调用适配器与 `LocalEnvironment` 外，仓库还支持基于纯文本正则解析的模型适配器与远程/容器执行环境，具体行为需按所选配置模块分别对照。
