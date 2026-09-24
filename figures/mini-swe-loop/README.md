# mini-swe-agent 最小循环：文字版

[返回剖面](../../docs/systems/mini-swe-agent/README.md) · [图源](scene.excalidraw) · [SVG](diagram.svg) · [PNG](preview.png)

图从左侧消息账本读到中间的调用循环，再沿底部的“是 / 否”箭头判断去向。`messages` 是不断追加的账本，而非泛化的“模型—工具—观察”流水线。开头写入 system 和 user 任务。循环中，`query()` 读取当前账本，检查限制，向模型取得 assistant 消息并追加；`execute_actions()` 将动作交给环境，追加观察消息。格式错误可添加反馈并继续；提交或限额等中断异常携带消息。每轮调用 `save()`，然后检查最后消息：只有 `role="exit"` 才跳出循环并返回该消息的 `extra`。一般未捕获异常会重新抛出，不能算正常的 exit 返回。

右侧列表说明不同的 `exit` 来源：本地环境命令输出首行的提交哨兵、查询前限制、达到阈值的连续格式错误。这些是可能的分支，不是必经顺序；图也不是运行轨迹。`mini` CLI 默认使用交互子类，这张图仅解释其基类循环，不覆盖确认模式。[源码与边界](../../docs/systems/mini-swe-agent/README.md)

固定官方源码版本：`SWE-agent/mini-swe-agent@04d809ceab9df28f9adaed044884180159172930`。
