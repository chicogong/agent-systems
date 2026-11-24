# 生产级 Agent 最小工程脚手架 (Production Starter Harness)

[返回机制目录](../../docs/concepts/README.md) · [前缀缓存与上下文经济学](../../docs/concepts/cache-and-cost-economics.md) · [最小循环实验](../../docs/concepts/agent-loop.md)

本目录提供了一个**纯 Python 3.10+ 标准库实现（零外部依赖）**的生产级 Agent 调度脚手架参考实现。

它将《图解 Agent 系统》全书沉淀的五大核心工程守则整合为一个高内聚、易于阅读和复制的模块化框架：

---

## 五大核心架构守则

```text
┌────────────────────────────────────────────────────────────────────────┐
│  Layer 1: Global Invariable   ──► 系统角色设定 + 严格字典序工具声明       │ (100% 缓存命中)
├────────────────────────────────────────────────────────────────────────┤
│  Layer 2: Session Constant     ──► 仓库施工规范 (AGENTS.md) + 只读记忆     │ (会话级稳定)
├────────────────────────────────────────────────────────────────────────┤
│  Layer 3: Milestone Summary    ──► 水位线分段压缩摘要 (Compaction)        │ (阶段级稳定)
├────────────────────────────────────────────────────────────────────────┤
│  Layer 4: Append-Only History  ──► 纯追加交互历史 (User/Assistant/Tool)  │ (严禁中途修改)
├────────────────────────────────────────────────────────────────────────┤
│  Layer 5: Transient Tail       ──► 动态步数倒计时、临时状态警报            │ (仅影响当步)
└────────────────────────────────────────────────────────────────────────┘
```

1. **五层稳定度递减排版（5-Layer Prefix Caching Layout）**：
   从最左侧全局不变项到最右侧瞬态队尾严格单向排布，保障主流大模型服务端（如 vLLM、Anthropic、OpenAI）的 KV Cache 命中率持续稳定在 **90% 以上**。
2. **宿主执行门禁与提案解耦（Host Approval Gate）**：
   模型吐出的工具调用只是“提案（Proposal）”；修改状态的写操作（如写文件、执行 Shell、调用远程 API）必须经过宿主安全策略的独立校验与放行。
3. **源头首尾截断（Anti Context-Rot Truncation）**：
   测试日志或命令输出动辄上百行，若原样灌入上下文会引发注意力稀释与上下文腐化。宿主拦截器自动保留前 15 行与后 15 行，中间以结构化行数标记替代。
4. **水位线分段压缩（Watermark Compaction）**：
   不采用逐条滑动窗口（避免步步失配），而是在逼近警告水位线时集中将前半段交互压成定态摘要，重置有效信号密度。
5. **逐步账单审计（KV Cache Token Accounting）**：
   对每一步的 `total_tokens`、`cached_tokens`、`uncached_tokens` 以及综合命中率提供实时量化对账。

---

## 快速上手与运行

### 1. 运行自包含演示

```bash
python3 examples/production-starter/demo.py
```

终端将打印 5 轮交互的完整单步 Token 消耗、缓存读取量与命中率账本：

```text
======================================================================
  Illustrated Agent Systems - Production Starter Harness Demo
======================================================================

[Turn 1] Input Tokens: 235 | Cache Read: 0 | Hit Rate: 0.0%
[Turn 2] Input Tokens: 295 | Cache Read: 235 | Hit Rate: 79.66%
[Turn 3] Input Tokens: 432 | Cache Read: 295 | Hit Rate: 68.29%
         (Tool output truncated from 81 lines to 21 lines to prevent Context Rot)
[Turn 4] Input Tokens: 512 | Cache Read: 432 | Hit Rate: 84.38%
[Turn 5] Input Tokens: 540 | Cache Read: 512 | Hit Rate: 94.81%
----------------------------------------------------------------------
Overall Statistics:
  Cumulative Input Tokens:   2014
  Cumulative Cached Tokens:  1474
  Cumulative Uncached Tokens:540
  Overall Cache Hit Rate:    73.19%
  Final Gate Verdict:        candidate_ready
======================================================================
```

### 2. 运行单元测试套件

```bash
python3 -m unittest examples/production-starter/test_starter.py
```

---

## 如何在你的项目中复用

该模板无需安装任何第三方库。只需将 `agent_starter.py` 拷贝至你的工程目录中：

```python
from agent_starter import (
    ContextAssembler,
    HostApprovalGate,
    ToolDefinition,
    ToolRiskLevel,
    Turn,
    truncate_tool_output,
)

# 1. 声明你的业务工具（标明风险等级）
tools = [
    ToolDefinition(
        name="query_database",
        description="Run readonly SQL select query",
        parameters={"sql": {"type": "string"}},
        risk_level=ToolRiskLevel.READ_ONLY,
    ),
    ToolDefinition(
        name="deploy_release",
        description="Deploy commit hash to target cluster",
        parameters={"commit": {"type": "string"}},
        risk_level=ToolRiskLevel.DESTRUCTIVE,
    ),
]

# 2. 初始化上下文组装器
assembler = ContextAssembler(
    system_role="你是一个专业的运维支持 Agent。",
    tools=tools,
    session_rules="遵守生产变更安全红线。",
)

# 3. 每轮请求组装
prompt = assembler.assemble_prompt(transient_tail="[剩余步数: 10]")
```
