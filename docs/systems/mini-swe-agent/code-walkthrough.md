# 读 `DefaultAgent` 的 100 行控制流

[返回剖面](README.md) · 固定源码 [`04d809ce`](https://github.com/SWE-agent/mini-swe-agent/tree/04d809ceab9df28f9adaed044884180159172930)

下列伪代码是阅读索引，不是原项目源码复制；`InterruptAgentFlow`、格式错误和其他异常的分支不能简化成一个“失败”。

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

1. `run()` 初始化 system/user 消息，循环调用 `step()`，并在每轮尾部检查最后消息的角色。[循环](https://github.com/SWE-agent/mini-swe-agent/blob/04d809ceab9df28f9adaed044884180159172930/src/minisweagent/agents/default.py#L88-L124)
2. `step()` 直接组合 `query()` 与 `execute_actions()`。`query()` 先检查 step、cost、wall-time，再将整个消息列表送给模型并追加返回的 assistant 消息。[step / query](https://github.com/SWE-agent/mini-swe-agent/blob/04d809ceab9df28f9adaed044884180159172930/src/minisweagent/agents/default.py#L126-L152)
3. 以 `LitellmModel` 为一个具体实现，它向模型提供 bash 工具，解析工具调用成 `extra.actions`；解析缺少调用、工具名或参数错误会抛出 `FormatError`。这是模型实现的证据，不表示所有可替换模型都只支持 bash。[模型调用](https://github.com/SWE-agent/mini-swe-agent/blob/04d809ceab9df28f9adaed044884180159172930/src/minisweagent/models/litellm_model.py#L64-L105) · [解析](https://github.com/SWE-agent/mini-swe-agent/blob/04d809ceab9df28f9adaed044884180159172930/src/minisweagent/models/utils/actions_toolcall.py#L30-L76)
4. `execute_actions()` 将解析出的动作逐个交给 `env.execute`，再让模型格式化观察消息并追加到 `messages`。以本地环境为例，命令通过子进程执行，输出或异常形成结果字典；指定完成哨兵会抛 `Submitted` 而不是返回普通观察。[执行与观察](https://github.com/SWE-agent/mini-swe-agent/blob/04d809ceab9df28f9adaed044884180159172930/src/minisweagent/agents/default.py#L154-L157) · [本地执行](https://github.com/SWE-agent/mini-swe-agent/blob/04d809ceab9df28f9adaed044884180159172930/src/minisweagent/environments/local.py#L24-L56)
5. `FormatError` 会把反馈加入下一轮上下文，并计数；`InterruptAgentFlow` 则直接加入其携带的消息。两者是否结束取决于追加后最后消息是否为 `exit`。普通异常被记录后重新抛出，属于异常终止路径。[分支与停止](https://github.com/SWE-agent/mini-swe-agent/blob/04d809ceab9df28f9adaed044884180159172930/src/minisweagent/agents/default.py#L100-L124)

`save()` 每轮都会被调用，但没有 `output_path` 时只返回序列化数据，不写文件。当前分析没有模型调用记录或命令执行日志，不验证时间、成本计数和格式错误恢复的运行效果。[save](https://github.com/SWE-agent/mini-swe-agent/blob/04d809ceab9df28f9adaed044884180159172930/src/minisweagent/agents/default.py#L159-L190)
