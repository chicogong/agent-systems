# Agent 说「已完成」时该查什么：从口头宣告到证据对账

[返回完成与证据](../../docs/comparisons/completion-and-evidence.md) · [图源](scene.excalidraw) · [原尺寸 SVG（手机可放大）](diagram.svg) · [PNG](preview.png)

左侧先摆出两份材料：上方是用户的原始任务约束（把 `timeout` 改成 5 秒、保持 `retries = 3` 不变、跑通测试且不提交推送），下方是 Agent 回合结束时交出的“已修改且测试通过”回复。

如果跳过核对、只看退出码或一句总结，就会掉进上方红色虚线框画出的“假完成陷阱”：测试只测了 5 秒超时，却漏看 `retries` 在同一份 diff 里被顺手改成了 `0`。

正常验收走下方橙色核对框，逐项对齐三类客观记录：① 打开文件 diff 确认目标值改对且原保留配置未受损；② 检查测试命令与断言是否真正覆盖这两项条件；③ 检查改动文件范围与 Git 本地/远端状态。发现缺漏就退回右上角补改；三项证据齐备，才形成右下角分列“已改、已测、待确认”的可信交付报告。

## 生成与核验

`build.py` 生成原生 `scene.excalidraw`，再由 `excalidraw-agent` 原生导出 `diagram.svg` 与 4× `preview.png`。本图服务于读者理解验收（试读题 C）与跨系统交付对照。
