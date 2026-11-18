# 快慢思考协同：小模型出有界信号，宿主三段式门控拍板

[返回快思考路由章节](../../docs/concepts/jev-and-system-one.md) · [图源](scene.excalidraw) · [原尺寸 SVG（手机可放大）](diagram.svg) · [PNG](preview.png)

当候选 Skill 或路由分支膨胀到几十项时，把窄域分类交给轻快的 System-1 小模型、把深层推理留给 System-2 主模型，同时由宿主代码（Harness）掌握阈值与授权方向盘：

1. **01 原始输入**：只向路由层传入用户当前请求与候选 Skill 的简短描述字典，不塞入长篇手册，降低首轮判断延迟。
2. **02 System-1 有界判断（如 Jev）**：通过 `Noul`（是非概率）与 `Choice`（多选分布与集中度 `confidence`）返回严格受限的 JSON 信号；模型本身不持有任何工具执行权，且生产环境需锁定精确模型版本号防止阈值漂移。
3. **03 宿主三段式阈值门控**：低分直通区（`need ≤ 0.20`）直接跳过装载节省上下文；灰区刹车区主动向用户确认意图而不硬猜；高确信区才把单个命中 Skill 注入 System-2 主模型，且后续任何写盘与外部动作依然受宿主审批与沙箱约束。底部蓝色虚线标出了路由超时时的无感降级通道。

## 生成与核验

`build.py` 生成原生 `scene.excalidraw`，再由 `excalidraw-agent` 原生导出 `diagram.svg` 与 4× `preview.png`。本图依据 TypeSafe Jev 官方原语文档与宿主三段式门控模式绘制。
