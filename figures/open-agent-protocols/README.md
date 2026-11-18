# 开放协作三层标准：仓库约定、纵向工具协议与横向代理委托

[返回开放协议栈章节](../../docs/concepts/open-agent-protocols.md) · [图源](scene.excalidraw) · [原尺寸 SVG（手机可放大）](diagram.svg) · [PNG](preview.png)

现代 Agent 工程把“读项目规矩”、“调确定性工具”与“请另一个独立 Agent 协作”拆进三层正交的开放标准，避免拿同一把协议锤子硬敲所有场景：

1. **静态仓库约定层（`AGENTS.md` / `CLAUDE.md`）**：位于顶部琥珀色区域。由代码库维护者编写纯文本开发规范（根目录写全局边界，子目录写局部构建与测试命令），宿主进入对应目录时按就近原则装入上下文，但它只是提示层指导，不自动授予执行特权。
2. **纵向工具与资源连接层（MCP `2025-11-25`）**：位于底部绿色区域。负责单个宿主向本地或远端服务调取工具与数据：用 **Streamable HTTP** 统一流式与普通请求传输，用 **OAuth 2.1** 把远端 MCP Server 纳入标准资源服务器鉴权（杜绝令牌盲目透传），并通过 **Tool Annotations**（只读、破坏性、幂等提示）与 **Elicitation**（中途补齐参数或带外敏感操作确认）精细化人机协同。
3. **横向跨代理协作层（A2A Protocol）**：位于右侧紫色区域。当协作对象本身是另一个拥有独立推理循环、不愿暴露内部提示词与私有工具的黑盒 Agent 时，主宿主先读取其 `/.well-known/agent-card.json` 名片，再派发异步 **Task**，沿 `submitted → working → input-required / auth-required → completed` 状态机流式跟进直至收回产物。

## 生成与核验

`build.py` 生成原生 `scene.excalidraw`，再由 `excalidraw-agent` 原生导出 `diagram.svg` 与 4× `preview.png`。本图为协议职责分层架构图，具体报文格式与安全要求以正文引用的官方规范版本为准。
