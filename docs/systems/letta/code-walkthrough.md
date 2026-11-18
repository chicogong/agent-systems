# 代码导读：追踪 Letta Code local MemFS v1 的记忆生效链路

[返回 Letta Code 首页](README.md) · 固定源码 [`1f55d3dc`](https://github.com/letta-ai/letta-code/tree/1f55d3dc66e238d203757fae288bb53f3adc7cd3)

你在对话里嘱咐编码助手：“以后汇报排查结果时，先给三行结论，再贴文件路径。”助手调用记忆工具把这条规则写进了 `system/style.md`，但在当前回合接下来的几步工具调用里，它的系统提示并没有立刻刷新——直到同步与提示重编译完成，后续请求才真正带上这条新规矩。

为什么一条新记忆从“写进磁盘”到“出现在系统提示”要跨越多步？下面沿着 `letta-code` 的源码调用链，按**目录契约判定 → 容量预算 → 落盘与 Git 留痕 → 同步与重编译**的顺序走一遍。

## 1. 目录位置如何决定上下文命运

打开 [`detectMemoryFormat`](https://github.com/letta-ai/letta-code/blob/1f55d3dc66e238d203757fae288bb53f3adc7cd3/src/agent/memory-format.ts#L6-L15) 可以看到第一道分流：只要 `localMemfs` 为真，代码直接返回 `"v1"`；只有非本地模式且根目录下存在 `MEMORY.md` 时，才会返回 `"v2"`。

紧接着，[`isCoreMemoryPath`](https://github.com/letta-ai/letta-code/blob/1f55d3dc66e238d203757fae288bb53f3adc7cd3/src/agent/memory-format.ts#L21-L29) 把目录结构翻译成“是否常驻系统提示”的布尔判断：在 `v1` 模式下，只有位于 `system/` 目录下的 `.md` 文件才返回 `true`。这意味着在 local MemFS v1 中，路径本身就是架构指令——放进 `system/style.md` 就会参与系统提示组装，而放进 `docs/runbook.md` 则留在磁盘上等待按需读取。

## 2. 防止核心记忆撑爆窗口的粗算器

既然 `system/` 下的所有 Markdown 都会常驻系统提示，一旦失控堆积就会挤压任务正文的上下文空间。[`estimateSystemPromptSize`](https://github.com/letta-ai/letta-code/blob/1f55d3dc66e238d203757fae288bb53f3adc7cd3/src/agent/system-prompt-size.ts#L1-L106) 复用同一套 `v1 / v2` 路径规则，递归扫描 `system/` 目录下的核心文件字节数，并按 `bytes / 4` 粗略折算 token 消耗：

```text
system/persona.md       (1,200 bytes)
system/style.md         (  400 bytes)
system/repo-index.md    (2,400 bytes)
─────────────────────────────────────
核心记忆合计 4,000 bytes  ──► 粗算约 1,000 tokens 常驻系统提示开销
```

这里故意不用重量级分词器，是为了在本地高频检查时以近似零开销给出容量水位；若要核对发给模型的精确 token 账单，则需要去模型请求出口查看。

## 3. 内置提示如何教模型使用三层存储

光靠宿主分目录还不够，模型自己必须知道去哪里找材料、往哪里写经验。[内置 local MemFS 提示](https://github.com/letta-ai/letta-code/blob/1f55d3dc66e238d203757fae288bb53f3adc7cd3/src/agent/prompts/letta_local_memfs.md#L8-L55) 明确向 Agent 交代了三层分工：

- **Core memory**（`system/`）：只放精炼的身份、用户偏好与资料索引；
- **External files / Skills**：遇到具体技术模块或复杂工作流时，先看索引，再用读取工具按路径加载正文；
- **Conversation history / recall**：近期上下文之外的早期讨论细节，通过历史检索工具回溯，不要把流水账硬塞进 `system/`。

## 4. 写入落盘与 Git 版本化

当模型决定把“先给三行结论，再贴文件路径”写进 `system/style.md` 时，调用进入 [`memory()` 工具](https://github.com/letta-ai/letta-code/blob/1f55d3dc66e238d203757fae288bb53f3adc7cd3/src/tools/impl/memory.ts#L99-L157)。工具先校验路径边界，防止越权修改记忆目录之外的工作区文件；完成文件写入后，紧接着调用 [`commitMemoryWrite`](https://github.com/letta-ai/letta-code/blob/1f55d3dc66e238d203757fae288bb53f3adc7cd3/src/agent/memory-git.ts#L1319-L1358)，将受影响的文件提交为本地记忆仓库的一个 Git revision。

注意此时的状态切面：

```json
{
  "target_file": "system/style.md",
  "disk_updated": true,
  "git_committed": true,
  "active_turn_system_prompt": "仍为回合启动时编译的旧版本"
}
```

文件落盘与 Git 留痕已经完成，但当前正在运行的对话回合并没有在半途抽换系统提示。

## 5. 同步合并与系统提示重编译

新写入的核心记忆真正进入系统提示，要看后续的同步与重编译链路。以 [memory worker 合并路径](https://github.com/letta-ai/letta-code/blob/1f55d3dc66e238d203757fae288bb53f3adc7cd3/src/agent/subagents/memory-worker.ts#L95-L139) 为例：worker 完成记忆整理与文件同步之后，才会在条件允许时调用 [`recompileAgentSystemPrompt`](https://github.com/letta-ai/letta-code/blob/1f55d3dc66e238d203757fae288bb53f3adc7cd3/src/agent/modify.ts#L683-L729)，触发 Agent 系统提示的重新组装。

把第 4 步和第 5 步连起来看，就能理解 Letta Code 的时序取舍：**写文件负责持久化与版本留痕，重编译负责切换模型视角**。正在执行中的回合继续使用启动时锁定的旧提示，既避免了同一回合内前后指令自相矛盾，又保住了上下文前缀的稳定性；等 `recompileAgentSystemPrompt` 完成后，下一次模型请求就会读到包含新版 `system/style.md` 的系统提示。

## 来源与边界

本导读固定核对 [`letta-ai/letta-code@1f55d3dc66e238d203757fae288bb53f3adc7cd3`](https://github.com/letta-ai/letta-code/tree/1f55d3dc66e238d203757fae288bb53f3adc7cd3) 中的 local MemFS v1 与 memory worker 重编译链路。其他工具编辑入口、API-backed MemFS v2 及远端服务端的同步时序各有分支，本文仅做静态源码走读，未执行运行期请求抓包验证。
