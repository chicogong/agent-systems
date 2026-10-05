# 读 `DefaultAgent`：消息怎样带着任务继续往下走

[返回首页](README.md) · 固定源码 [`04d809ce`](https://github.com/SWE-agent/mini-swe-agent/tree/04d809ceab9df28f9adaed044884180159172930)

假设模型先要求读一个文件，再根据文件内容决定下一条命令。mini-swe-agent 让执行结果回到同一份 `messages` 清单；下一次请求模型时，就把更新后的清单发过去。先沿这条正常路径看四个函数，再看程序如何结束。

下面的伪代码只概括阅读顺序，具体实现见固定源码链接。

```text
messages = [system, user(task)]
while True:
    try:
        query(): 检查限额 → model.query(messages) → 追加 assistant
        execute_actions(): env.execute(actions) → 追加观察消息
    except FormatError: 追加反馈；达到连续阈值则追加 exit
    except InterruptAgentFlow: 追加异常携带的消息（如 Submitted / LimitsExceeded）
    except Exception: 追加 exit，然后重新抛出
    finally: save(output_path)
    if messages[-1].role == "exit": break
return messages[-1].extra
```

## 先看四个函数如何合作

`run()` 放入系统指导和用户任务，循环调用 `step()`，每轮末尾看最后一条消息是否要求退出。[启动循环](https://github.com/SWE-agent/mini-swe-agent/blob/04d809ceab9df28f9adaed044884180159172930/src/minisweagent/agents/default.py#L88-L124)

`step()` 把 `query()` 和 `execute_actions()` 接起来。`query()` 先检查轮数、成本和已用时间，再请求模型，把模型回复加入清单。[请求模型](https://github.com/SWE-agent/mini-swe-agent/blob/04d809ceab9df28f9adaed044884180159172930/src/minisweagent/agents/default.py#L126-L152)

模型接口的具体实现之一是 `LitellmModel`：它提供 bash 工具，把模型的工具调用解析成 `extra.actions`。缺少调用，或工具名、参数有误时，会产生 `FormatError`，告诉外层程序模型回复格式出了问题。[模型接口](https://github.com/SWE-agent/mini-swe-agent/blob/04d809ceab9df28f9adaed044884180159172930/src/minisweagent/models/litellm_model.py#L64-L105) · [解析动作](https://github.com/SWE-agent/mini-swe-agent/blob/04d809ceab9df28f9adaed044884180159172930/src/minisweagent/models/utils/actions_toolcall.py#L30-L76)

`execute_actions()` 逐个把动作交给 `env.execute`。以本地环境为例，命令在子进程里执行，输出或异常整理成结果字典。随后 `format_observation_messages()` 用模板把结果变成工具消息，加入 `messages`；下一轮 `query()` 才把它们交给模型。[执行动作](https://github.com/SWE-agent/mini-swe-agent/blob/04d809ceab9df28f9adaed044884180159172930/src/minisweagent/agents/default.py#L154-L157) · [整理结果消息](https://github.com/SWE-agent/mini-swe-agent/blob/04d809ceab9df28f9adaed044884180159172930/src/minisweagent/models/litellm_model.py#L140-L151) · [本地执行命令](https://github.com/SWE-agent/mini-swe-agent/blob/04d809ceab9df28f9adaed044884180159172930/src/minisweagent/environments/local.py#L24-L56)

## 再看哪些消息让它停下

普通命令结果进入下一轮。符合指定完成输出的命令则触发 `Submitted`，带回一条 `exit` 消息，告诉循环提交并结束。

`FormatError` 先带回错误反馈，让模型有机会修正；程序也会累计连续错误次数。`InterruptAgentFlow` 是携带控制消息的一类异常，例如 `Submitted`（提交）和 `LimitsExceeded`（超过限额），程序会直接把其中的消息加入清单。末尾为 `exit` 就结束。其他未处理异常则记录后重新抛给调用方。[反馈、控制消息和错误](https://github.com/SWE-agent/mini-swe-agent/blob/04d809ceab9df28f9adaed044884180159172930/src/minisweagent/agents/default.py#L100-L124)

## 工作记录怎样保存

`save()` 每轮都会调用。有 `output_path` 时写入轨迹文件；没有时只返回整理好的数据。想在运行后回看过程，需要先设置输出路径。[保存记录](https://github.com/SWE-agent/mini-swe-agent/blob/04d809ceab9df28f9adaed044884180159172930/src/minisweagent/agents/default.py#L159-L190)

本篇依据固定源码，尚未运行模型或命令。其他模型适配器可以使用不同工具，命令行的交互确认也在另一层处理；实际恢复和限额效果仍需运行检查。
