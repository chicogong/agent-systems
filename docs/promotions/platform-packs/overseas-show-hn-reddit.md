# Overseas Developer Communities Launch Pack (Show HN & Reddit)

[Back to Launch Pack](../launch-pack.md) · [Back to Repository Root](../../../README.md) · [Read Book Online](https://books.aimake.cc/)

> **Usage Guidelines**:
> This document provides ready-to-publish, copy-pasteable English launch drafts for two premier overseas technical communities:
> 1. **Hacker News (Show HN)**: Focused on systems architecture, deterministic state machines, and real-world failure postmortems.
> 2. **Reddit (r/LocalLLaMA & r/MachineLearning)**: Focused on inference engine KV cache mechanics (vLLM, SGLang, llama.cpp), local LLM memory economics, and reproducible Python stdlib labs.

---

## 📑 Table of Contents

1. [Part 1: Hacker News (Show HN) Launch Draft](#part-1-hacker-news-show-hn-launch-draft)
   - [Submission Metadata](#submission-metadata)
   - [Show HN Text / First Comment](#show-hn-text--first-comment)
   - [Anticipated HN Q&A Playbook](#anticipated-hn-qa-playbook)
2. [Part 2: Reddit (r/LocalLLaMA & r/MachineLearning) Launch Draft](#part-2-reddit-rlocalllama--rmachinelearning-launch-draft)
   - [Post Metadata & Flairs](#post-metadata--flairs)
   - [Reddit Post Body](#reddit-post-body)
   - [Anticipated Reddit Discussion Seeds](#anticipated-reddit-discussion-seeds)

---

## Part 1: Hacker News (Show HN) Launch Draft

### Submission Metadata

- **Target URL**: `https://books.aimake.cc/` (or repository link: `https://github.com/chicogong/agent-systems`)
- **Title Options**:
  - **Option 1 (Architecture & Visualization, Recommended)**:  
    `Show HN: Illustrated Agent Systems – Visual architecture guide with 40 interactive traces`
  - **Option 2 (Concrete Source Dissections)**:  
    `Show HN: Illustrated Agent Systems – Dissecting 16 open-source agent frameworks with pinned commits`
  - **Option 3 (Pain-Point & Mechanics)**:  
    `Show HN: Why prefix cache busting costs you 10x tokens in production agents (and a visual guide)`

---

### Show HN Text / First Comment

```markdown
Hi HN,

Over the past year, while deploying multi-step coding and automation agents to production, our team repeatedly ran into the same baffling and expensive failures:

- **The 100:1 Token Inversion & Prefix Cache Thrashing**: Running a 30-step task would quietly consume nearly 1,000,000 input tokens despite the model generating only a few dozen tokens of tool calls per step. The culprit? A single harmless-looking line at the top of the System Prompt: `Current Time: 2026-11-26 15:30:00`. Because causal attention prefix caching matches strictly byte-for-byte from left to right, that dynamic timestamp evicted tens of thousands of cached KV tokens on every single step, destroying a 90% hardware discount.
- **The "I'm Done" Illusion**: A file-writing tool returned `{"status": 200, "ok": true}`, so the LLM declared the task complete. In reality, the written code contained syntax errors and deleted the core unit tests. Trusting model self-reporting without an independent host verification gate is a recipe for silent failure.
- **Context Rot & Attention Dispersion**: Packing a 1,000,000-token window with raw compiler dumps quickly pushed the decision-relevant signal density below 10%, causing the agent to lose its safety guardrails in the middle of long sessions.

Most online tutorials reduce Agents to "20 lines of LangChain or LlamaIndex prompt chaining." In production, however, an Agent is fundamentally a **deterministic distributed state machine with strict approval gates, sandbox isolation, and physical hardware constraints**.

To bridge this gap, we created **Illustrated Agent Systems** (*图解 Agent 系统*), a completely open-source visual guide inspired by the philosophy of *Grokking Algorithms*:

1. **40 Hand-Drawn Architectural Diagrams**: Handcrafted Excalidraw vector diagrams breaking down the agent loop, prefix cache economics, memory funnels, and sandbox blast radius. Every diagram is open-sourced and can be edited online with one click.
2. **Dissecting 16 Open-Source Frameworks with Pinned Commits**: Rather than using toy examples, we dissect real-world production harnesses—including **Pi, Codex, Letta, Qwen-Code, OpenHands, Browser-Use, and Hermes**. All 109 code references are anchored to immutable 40-character Git commit hashes with automated CI drift detection.
3. **Zero-Dependency Python Labs + In-Browser TracePlayer**: Six deterministic, pure Python 3.10+ standard library experiments (zero pip installs, no API key, no GPU required). You can verify a 96.1% prefix cache hit rate vs. 0% thrashing in 3 seconds locally. The online book also features an interactive browser-based TracePlayer to inspect step-by-step state machine payloads.

- 🌐 **Free Online Book & TracePlayer**: https://books.aimake.cc/
- 💻 **GitHub Repository (MIT / CC BY 4.0)**: https://github.com/chicogong/agent-systems
- 📊 **Vector Architecture Diagrams**: https://github.com/chicogong/agent-systems/tree/main/figures

### The 5-Layer Prompt Hierarchy Rule
For anyone building multi-turn agent harnesses today, here is the core layout principle to ensure 90%+ prefix cache reuse across Anthropic, OpenAI, vLLM, and SGLang:

1. **Level 1 (Global Invariable)**: Role definition + Alphabetically sorted tool schemas (95%+ cache hit rate).
2. **Level 2 (Session Constant)**: Workspace guidelines (`AGENTS.md`) + immutable constraints.
3. **Level 3 (Milestone Summary)**: Deterministic state compaction triggered at 80% watermark (avoid naive sliding-window `pop(0)`).
4. **Level 4 (Append-Only History)**: Strictly sequential interaction turns. Never edit previous steps.
5. **Level 5 (Transient Tail)**: Seconds-level clocks, step budgets, or volatile observations appended at the very end.

*Note on language*: The narrative is currently in Chinese, but all 40 SVG architecture diagrams include English event models and dataflow labels, and all 6 runnable Python lab scripts are fully bilingual and self-contained. An official English translation is actively underway.

We would love your critical feedback on our architectural breakdown, state machine abstractions, and lab designs!
```

---

### Anticipated HN Q&A Playbook

#### Q1: "Is the book only in Chinese? When will an English version be available?"
> **Suggested Response**:  
> Yes, the prose is currently in Chinese, but we designed it to be highly visual from day one. All 40 SVG diagrams feature English event names, states, and dataflow labels, and the 6 reproducible Python labs (`examples/`) have bilingual comments and CLI outputs.  
> If you browse with Chrome or Edge built-in translation, the markdown translates remarkably well because the concepts are grounded in standard systems terminology (Harness, KV Cache, TracePlayer, Sandbox).  
> A native English edition is in active development on our roadmap ([Issue #4](https://github.com/chicogong/agent-systems/issues/4)). Community PRs and reviewers are very welcome!

#### Q2: "Isn't an Agent just prompt engineering? Why do we need distributed systems thinking here?"
> **Suggested Response**:  
> Prompt engineering affects the model's single-turn likelihood distribution, but the host harness determines whether the system actually converges, remains safe, and stays affordable.  
> In a 30-step loop:  
> 1. **Idempotency & Failure Recovery**: If a tool call to restart a Docker container times out, the harness must query external state rather than blindly retrying, which could duplicate state mutation.  
> 2. **Cache Economics**: Prompt ordering directly dictates whether your inference costs $0.05 or $0.50 per task.  
> 3. **Host Verification Gates**: A model cannot be its own referee. Independent file inspection and test execution must reside outside the LLM context.  
> We treat the LLM as an untrusted, stochastic CPU, and the Harness as the operating system kernel managing memory, I/O, and permissions.

#### Q3: "How does this compare to reading the documentation of LangGraph, AutoGen, or CrewAI?"
> **Suggested Response**:  
> Framework documentation naturally focuses on *how to use their proprietary APIs*. Our guide focuses on the *underlying physical invariants* that every framework must grapple with:  
> - Why Qwen-Code uses a lazy `tool_search` endpoint instead of stuffing 100 MCP tools into the prompt.  
> - Why Codex enforces a separation between intent approval (user consent) and blast radius containment (sandbox execution).  
> - Why Letta splits persistent memory into tiered blocks with a recompilation boundary.  
> By anchoring each case study to fixed 40-character Git commit hashes across 16 frameworks, you see the actual engineering trade-offs without the framework sales pitch.

---

## Part 2: Reddit (r/LocalLLaMA & r/MachineLearning) Launch Draft

### Post Metadata & Flairs

- **Target Subreddits**:
  - Primary: `r/LocalLLaMA` (Flair: `[Project]` or `[Discussion]`)
  - Secondary: `r/MachineLearning` (Flair: `[P] Project`)
- **Title Options**:
  - **Option 1 (Local LLM / KV Cache focus)**:  
    `[Project] Illustrated Agent Systems: Why dynamic timestamps destroy your local KV cache (vLLM/llama.cpp) & 40 visual architecture diagrams`
  - **Option 2 (Engineering deep-dive)**:  
    `Why your local Agent setup costs 10x more KV cache than expected: Prefix caching mechanics, host verification gates, and an open-source visual guide`

---

### Reddit Post Body

```markdown
Hey everyone on r/LocalLLaMA,

If you run multi-turn tool-calling agents on top of local inference engines (like **vLLM, SGLang, Aphrodite, or llama.cpp server**), you've probably noticed that memory usage and time-to-first-token (TTFT) can degrade drastically after just 10–15 steps.

We recently spent months analyzing why this happens, dissecting 16 open-source production agent harnesses, and we put together an open-source architectural guide called **Illustrated Agent Systems** (*图解 Agent 系统*). 

Here is the technical postmortem of the biggest memory killer we found in local agent pipelines, along with a zero-dependency script to benchmark it on your own machine.

---

### 1. The Math of Multi-Step Agent Loops: 100:1 Token Inversion

In normal conversational LLMs, input vs. output is typically 2:1 or 5:1. But multi-step autonomous agents operate in an observation-action loop:
On every single turn $k$, the host must resend:
`[System Prompt] + [Tool Definitions] + [All Historic Turns 1..k-1] + [Latest Tool Output]`

If your system prompt + tools consume 6,000 tokens, and each tool step adds 1,000 tokens of output/observation:
Across 25 steps, the model generates only ~4,000 tokens of actions, but the inference engine processes:
$$\sum_{k=1}^{25} (6000 + 1000k) = 475,000 \text{ input tokens}$$

In local hosting, **recomputing attention for 475,000 tokens will saturate your GPU compute and cause massive TTFT delays**. Modern engines rely on **PagedAttention prefix caching** (storing KV blocks keyed by token hashes from left to right).

---

### 2. The Four Anti-Patterns That Thrash Local KV Cache

Because block-level hash matching is strictly left-to-right:

1. **Dynamic Timestamps in System Prompt**: Putting `Current time: 2026-11-26 15:30:00` in row 1 alters the token sequence at index 0. **Result: 0% prefix cache hit rate on every step.** All 475,000 tokens must be recomputed from scratch.
2. **Unsorted Tool Schemas**: Passing Python dicts without `sort_keys=True` causes keys to serialize in non-deterministic order across process restarts, invalidating cached prefixes.
3. **Naive Sliding-Window History (`messages.pop(0)`)**: Popping the oldest message shifts all subsequent tokens forward by $N$ positions, changing their relative positional embeddings and invalidating the entire cached block table.
4. **Dynamic Tool Injection**: Adding or removing tools mid-session breaks the prefix right after the system prompt.

---

### 3. The 5-Tier Stability Rule for Agent Harnesses

To keep local KV cache reuse at **90%–96%**, organize your prompt memory strictly by volatility:

```
[Level 1: Global Invariable]   ── System role + Sorted Tool Schemas (Never changes)
           ↓
[Level 2: Session Constant]    ── AGENTS.md + immutable repo rules
           ↓
[Level 3: Milestone Summary]   ── Watermark compaction at 80% limit (summarize in-place)
           ↓
[Level 4: Append-Only History] ── Turns 1..N strictly appended, never modified
           ↓
[Level 5: Transient Tail]      ── Clocks, step budget reminders, volatile tool results
```

---

### 4. Reproduce It in 3 Seconds (Zero Dependencies)

We wrote a zero-external-dependency Python benchmark that simulates this exact memory and token billing flow using standard library code:

```bash
# Clone the repository
git clone https://github.com/chicogong/agent-systems.git
cd agent-systems

# Run the prefix cache demonstration (0 dependencies, pure Python 3.10+)
python3 examples/prefix-cache/demo.py --mode layered_hit
```
You'll see real-time output demonstrating how layered prompt ordering saves 96.1% of input computation compared to cache thrashing.

---

### 5. What Else Is in the Project?

- **40 Hand-Drawn Excalidraw Diagrams**: Visualizing the agent loop, sandbox blast radius, and memory funnels ([Browse Diagrams](https://github.com/chicogong/agent-systems/tree/main/figures)).
- **16 Open-Source Framework Case Studies**: Dissecting Pi, Codex, Letta, Qwen-Code, OpenHands, and more, all anchored to pinned 40-character commit hashes.
- **Interactive TracePlayer**: A web-based single-step state machine player to inspect payload frames without setting up an environment.

- 📖 **Online Book & Interactive TracePlayer**: https://books.aimake.cc/
- 🐙 **GitHub Repository**: https://github.com/chicogong/agent-systems

*Note*: The book text is in Chinese, but all 40 architectural diagrams have English dataflow labels, the lab scripts are bilingual, and browser translation handles the technical markdown cleanly.

What caching or context strategies have you found most effective when running local agents on vLLM or llama.cpp? Would love to hear your thoughts and war stories!
```

---

### Anticipated Reddit Discussion Seeds

#### Seed 1: How does vLLM's Chunked Prefill interact with Prefix Caching?
> **Answer**:  
> With `--enable-chunked-prefill` enabled in vLLM, long context prompts are broken into chunks (e.g. 512 tokens) and co-scheduled with decode tokens. When combined with `--enable-prefix-caching`, chunked prefill still hashes blocks sequentially. If your Level 1 and Level 2 prefixes match existing blocks, vLLM bypasses prefill for those chunks completely, dramatically reducing TTFT and preventing decode bubbles.

#### Seed 2: Why not just use sliding-window attention with llama.cpp `--cont-batching`?
> **Answer**:  
> Sliding-window KV cache truncation works well for unstructured conversational chat where older history can be dropped. But in multi-step agents, early turns often contain crucial system permissions, user goals, and API schemas. Dropping the first message causes severe safety regressions and goal drift. Watermark compaction (summarizing intermediate state at 80% context window and appending a clean summary) preserves semantic constraints while keeping prefix blocks stable.
