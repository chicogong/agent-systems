# mini-swe-agent 最小循环：文字版

[返回讲解](../../docs/systems/mini-swe-agent/README.md) · [图源](scene.excalidraw) · [SVG](diagram.svg) · [PNG](preview.png)

给助手一个代码任务，它读文件、执行命令，再根据输出继续。图左侧的 `messages[]` 是不断追加的消息清单：开头放入系统指导（system）和用户任务（user），随后加上模型回复（assistant）与命令结果（observation）。

中间的两个函数串起一轮工作：`query()` 先检查限额，再把当前清单交给模型，并追加回复；`execute_actions()` 把回复里的动作交给执行环境，拿到结果后追加观察消息。下一轮模型就能看到上一轮做事的结果。

每轮调用 `save()` 后，程序查看最后一条消息。角色为 `exit`（退出）时，沿“是”箭头结束，返回这条消息的 `extra` 数据；否则沿“否”箭头再工作一轮。图中“不是模型布尔值”的意思是，这里读的是消息的角色字段。要把记录写进文件，还需设置 `output_path`。

右侧列出三种让清单追加 `exit` 的情况：

- **`Submitted`：提交完成。** 本地命令输出首行的完成标记 `COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT` 被识别，且返回码为 0；检查时会忽略开头和行两端的空白。图里的“哨兵”就是这条约定的完成标记。
- **`Limits / Time`：达到限制。** 请求模型前发现轮数、成本或已用时间达到限额。
- **`RepeatedFormatError`：连续格式错误。** 程序先把格式错误反馈给模型；连续错误达到阈值时结束。

这些是不同的结束原因。其他未处理异常会记录后重新抛给调用方，由外层程序处理。[源码与具体条件](../../docs/systems/mini-swe-agent/README.md)

本图只讲基类 `DefaultAgent` 的循环。命令行（CLI）的 `mini` 默认用交互子类，确认模式在那一层处理。图依据固定官方源码 `SWE-agent/mini-swe-agent@04d809ceab9df28f9adaed044884180159172930`，尚未采集真实模型或命令的运行记录。
