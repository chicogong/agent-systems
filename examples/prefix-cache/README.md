# 动手：KV 前缀缓存与缓存失效对比 (Prefix Cache Hit vs Bust)

[返回机制目录](../../docs/concepts/README.md) · [前缀缓存与上下文经济学](../../docs/concepts/cache-and-cost-economics.md) · [上下文预算与可见性](../context-budget/README.md)

## 3 分钟显微镜：跑完这几行，你会亲眼看到什么？

在多步 Agent 循环中，输入与输出 Token 量的比例常常高达 `100:1`。现代大模型底座依靠 Transformer 因果注意力的前缀缓存（KV Cache）将多轮输入的计费单价降低 50%~90%，并大幅降低首字延迟（TTFT）。

然而，前缀匹配是**逐字节从左向右严格比对**的：如果第 1 块 Token 发生哪怕 1 个字符的变动，整段几万 Token 的历史缓存就会全盘击穿。

在这个零依赖的 3 分钟小实验里，跑完下面三行命令，你会在终端 JSON 中亲眼观察到三种典型装配策略下的 Token 账单与状态流转差异：

```bash
# 1. 严格分层与纯追加：96.1% 高缓存命中
python3 examples/prefix-cache/demo.py --mode layered_hit

# 2. 系统提示注入动态时间戳：0% 命中，全盘击穿
python3 examples/prefix-cache/demo.py --mode dynamic_timestamp

# 3. 工具定义乱序注入：前缀分叉，历史无法复用
python3 examples/prefix-cache/demo.py --mode shuffled_tools
```

## 三种运行模式核心数据对比

| 运行模式 | 状态标识 `status` | 5 轮累计输入 | 缓存读取 Token | 最终缓存命中率 | 账单与延迟表现 |
| --- | --- | --- | --- | --- | --- |
| `layered_hit` | `high_cache_hit` | 38,100 | 36,600 | **96.06%** | 算力成本节省 86.5%，TTFT 稳定在 95ms |
| `dynamic_timestamp` | `cache_bust_timestamp` | 38,100 | 0 | **0.00%** | 步步全额重算输入，TTFT 高达 850ms |
| `shuffled_tools` | `cache_bust_shuffled` | 38,100 | 24,000 | **62.99%** | 仅系统提示命中，后方对话前缀全灭 |

## 关键机制与排版律

1. **越稳定越靠前**：系统指令与工具 Schema 必须严格固定在最前排（固定字典序 `sort_keys=True`）；
2. **历史纯追加（Append-Only）**：新轮次消息只在队尾追加，绝不回头篡改历史措辞或逐条滑动窗口裁剪；
3. **动态状态挂队尾**：确需秒级时钟或单步瞬态标记时，作为增量观察挂在 `messages` 最末端。

## 来源与边界

本实验使用确定性数值模拟 Transformer 自回归前缀缓存命中机制与 Token 账单核验，无需外部 API Key 与真实 GPU 推理。真实服务商（vLLM、Anthropic、OpenAI）的最小起缓粒度（如 1024 Token 块对齐）与折扣比率需参照具体官方文档。
