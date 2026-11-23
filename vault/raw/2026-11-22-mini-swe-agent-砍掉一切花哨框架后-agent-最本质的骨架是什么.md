---
title: "mini-SWE-agent：砍掉一切花哨框架后，Agent 最本质的骨架是什么"
origin: "/Users/haorangong/Github/chicogong/experiments/agent-systems/docs/systems/mini-swe-agent/README.md"
sha256: "bd36d35e40b214fecd8dc3e75671f0bb198a64d5f38195b4bb603b79c35aa465"
ingested_at: "2026-11-22T13:54:22.907Z"
tags: []
---

# mini-SWE-agent：砍掉一切花哨框架后，Agent 最本质的骨架是什么

# mini-SWE-agent：砍掉一切花哨框架后，Agent 最本质的骨架是什么

[返回系统目录](../README.md) · [关键代码导读](code-walkthrough.md)

读多了动辄几万行代码的重型 Agent 框架——各种有向无环图（DAG）调度器、三十多种自定义改文件工具、层层嵌套的事件总线——开发者很容易产生一种错觉：好像不搭一套庞大的脚手架，大模型就连修个 Bug 都寸步难行。直到你在跑大规模基准测试时被自定义 `search_replace` 解析器折磨到崩溃，或者发现框架里的布尔状态位（`is_finished`、`over_budget`、`error_count`）跟实际对话历史对不上号，才会意识到过度抽象本身的脆弱。

SWE-agent 团队开源的 **mini-SWE-agent** 做了一次酣畅淋漓的减法实验：核心类 `DefaultAgent` 只有**不到两百行 Python 代码**，不造任何专用文件编辑工具（全靠标准 bash），不设独立状态机，整个运行时从头到尾只围绕**一份线性的 `self.messages` 消息列表**旋转——任务是消息、命令输出是消息、格式报错自纠是消息，连最终停机契约也是一条 `role="exit"` 的消息。

![mini-swe-agent 的消息清单与结束流程](../../../figures/mini-swe-loop/diagram.svg)

[文字版](../../../figures/mini-swe-loop/README.md) · [可编辑图源](../../../figures/mini-swe-loop/scene.excalidraw) · [关键代码导读](code-walkthrough.md)

## 核心循环只有两拍：问模型，跑命令

打开 `DefaultAgent.run()`，你会惊讶于它的直白：先把系统提示词和用户任务塞进 `self.messages`，然后跑一个 `while` 循环，每一轮 `step()` 只做两件事（见[循环](https://github.com/SWE-agent/mini-swe-agent/blob/04d809ceab9df28f9adaed044884180159172930/src/minisweagent/agents/default.py#L88-L128)与[请求模型与执行动作](https://github.com/SWE-agent/mini-swe-agent/blob/04d809ceab9df28f9adaed044884180159172930/src/minisweagent/agents/default.py#L130-L157)）：

1. **问模型**（`query`）：检查预算未超标后，把整份 `self.messages` 发给模型，把模型返回的 `assistant` 回复追加到列表末尾。
2. **跑动作**（`execute_actions`）：从回复的 `extra.actions` 里取出要执行的 bash 命令交给环境运行，把标准输出与退出码渲染成观察消息，同样追加到 `self.messages` 末尾。

每轮不论成败，收尾都会调一次 `save()` 刷新轨迹记录。没有隐藏的外部上下文缓存，下一轮模型看到的，完完全全就是上一轮追加后的同一份列表。

## 输出哨兵与 `role="exit"`：不造专用提交工具怎么停机

既然连「提交任务」都不单独定义一个结构化工具，程序怎么知道模型干完活了？

mini-SWE-agent 用了一个极简却极其稳健的**标准输出哨兵协议**：在本地执行环境 `LocalEnvironment` 中，每跑完一条命令，程序就检查返回码是否为 `0`，并提取命令输出去掉首尾空白后的**第一行**；一旦这一行精确等于约定口令 `COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT`，环境层立刻抛出携带退出消息的 `Submitted` 信号，`run()` 捕获后把这条 `role="exit"` 的消息塞进 `self.messages` 末尾，外层循环看到 `messages[-1]["role"] == "exit"` 当场停机返回（见[识别提交信号](https://github.com/SWE-agent/mini-swe-agent/blob/04d809ceab9df28f9adaed044884180159172930/src/minisweagent/environments/local.py#L24-L56)与[把信号加入清单](https://github.com/SWE-agent/mini-swe-agent/blob/04d809ceab9df28f9adaed044884180159172930/src/minisweagent/agents/default.py#L100-L124)）。

```text
模型执行: echo COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT && git diff
  └─► LocalEnvironment 检测到 returncode == 0 且首行命中哨兵
        └─► 抛出 Submitted(message={"role": "exit", "content": ..., "extra": {"exit_status": "Submitted", ...}})
              └─► DefaultAgent.run() 将其追加至 self.messages ──► 命中 role == "exit"，干净停机！
```

这里也藏着评测工程里的一条清醒认知：`exit_status == "Submitted"` 只代表模型**主动走完了交卷仪式**，绝不代表它改出来的补丁真能跑通测试——代码对不对，永远要靠外部测试集真刀真枪去验。

## 把格式报错喂回下一轮：允许犯错，但拒绝死缠烂打

极简并不意味着脆弱。跑真实任务时，模型难免会漏写工具调用、写错工具名，或者一路跑飞烧光预算。`DefaultAgent` 把所有异常出口全都收敛进了同一套消息账本机制里：

- **格式错误带内自纠**：当模型回复解析不出合法的 bash 调用时，底层抛出 `FormatError`（见[解析调用](https://github.com/SWE-agent/mini-swe-agent/blob/04d809ceab9df28f9adaed044884180159172930/src/minisweagent/models/utils/actions_toolcall.py#L30-L76)）。直接炸掉整个任务太可惜——前面可能已经跑了十五轮有效探索！于是程序把报错提示作为反馈消息直接塞进 `self.messages`，让模型下一轮自己看错改错；只有连续犯错次数撞上阈值时，才写入 `RepeatedFormatError` 的 `exit` 消息强制收摊（见[加入反馈](https://github.com/SWE-agent/mini-swe-agent/blob/04d809ceab9df28f9adaed044884180159172930/src/minisweagent/agents/default.py#L100-L115)）。
- **请求前硬限额熔断**：每次调模型前先卡步数、累计美元花费与已耗时长；任一指标超限立刻通过 `LimitsExceeded` 塞入说明原因的 `exit` 消息停机（见[限额检查](https://github.com/SWE-agent/mini-swe-agent/blob/04d809ceab9df28f9adaed044884180159172930/src/minisweagent/agents/default.py#L130-L152)）。
- **未知崩溃留痕重抛**：遇到意料之外的运行时异常，也先往消息清单末尾记一笔 `exit` 现场，再原样向上抛出，绝不吞掉堆栈（见[异常处理](https://github.com/SWE-agent/mini-swe-agent/blob/04d809ceab9df28f9adaed044884180159172930/src/minisweagent/agents/default.py#L117-L124)）。

## 核心保持纯粹，人类交互靠子类叠上去

为什么 `DefaultAgent` 里连一句「请按回车确认执行」都没有？因为批量跑几百道 SWE-bench 评测题时，核心越纯粹越好。当真人在终端里敲 `mini` 命令日常使用时，CLI 默认实例化的是继承自 `DefaultAgent` 的子类 `InteractiveAgent`——由子类在核心骨架外层叠加上人工输入、逐条命令确认、自动运行模式切换以及交卷前的二次确认（见[命令行选择](https://github.com/SWE-agent/mini-swe-agent/blob/04d809ceab9df28f9adaed044884180159172930/src/minisweagent/run/mini.py#L94-L102)、[交互类](https://github.com/SWE-agent/mini-swe-agent/blob/04d809ceab9df28f9adaed044884180159172930/src/minisweagent/agents/interactive.py#L24-L36)与[交互处理](https://github.com/SWE-agent/mini-swe-agent/blob/04d809ceab9df28f9adaed044884180159172930/src/minisweagent/agents/interactive.py#L58-L94)；注意若需把完整轨迹落盘成文件，还必须显式传入非空的 `output_path`，见[保存条件](https://github.com/SWE-agent/mini-swe-agent/blob/04d809ceab9df28f9adaed044884180159172930/src/minisweagent/agents/default.py#L182-L190)）。

想亲眼看看这不到两百行代码是如何把异常当成优雅的单向控制流来用的，直接翻开下一篇[关键代码导读](code-walkthrough.md)。

## 来源与边界

本文基于官方仓库固定提交 [`SWE-agent/mini-swe-agent@04d809ceab9df28f9adaed044884180159172930`](https://github.com/SWE-agent/mini-swe-agent/tree/04d809ceab9df28f9adaed044884180159172930) 编写。全文聚焦 `DefaultAgent` 与 `LocalEnvironment` 的静态核心源码路径；容器化执行环境（如 Docker / Singularity 后端）与具体评测集得分表现不在本篇讨论范围内。
