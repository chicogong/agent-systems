"""Generate Hermes' durable knowledge vs current-input teaching diagram."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from diagram_style import Scene  # noqa: E402

INK = "#172033"
MUTED = "#4b5b70"
BLUE = "#3478e5"
PURPLE = "#7653d8"
GREEN = "#23845a"
ORANGE = "#b96a10"


def card(scene, name, title, detail, x, y, w, h, stroke, fill):
    scene.box(name, x, y, w, h, stroke, fill)
    scene.text(name + "-title", title, x + 18, y + 14, w - 36, 26, INK, 8)
    scene.text(name + "-detail", detail, x + 18, y + 55, w - 36, 23, MUTED, 8)


def main():
    d = Scene()
    d.text("title", "Hermes：记忆怎样进入回答", 40, 24, 860, 34, INK, 8)
    d.text("intro", "先保存到文件，再在加载时放进模型输入。", 42, 76, 850, 24, MUTED, 8)
    card(d, "memory-file", "短记忆文件", "MEMORY.md / USER.md\n跨任务事实与约束", 40, 145, 280, 132, GREEN, "#c3fae8")
    d.arrow("reload", [(320, 211), (550, 211)], GREEN)
    d.text("reload-label", "加载 / 压缩后\n重建快照", 334, 146, 205, 23, GREEN, 8)
    card(d, "snapshot", "system prompt 快照", "普通写入不即时替换", 550, 145, 350, 132, PURPLE, "#d0bfff")
    d.arrow("assemble", [(725, 277), (725, 365)], PURPLE)
    d.text("assemble-label", "组装", 742, 307, 85, 23, PURPLE, 8)

    card(d, "input", "模型这轮读到什么", "输入：快照 + 当前消息\n输出：建议更新知识", 550, 365, 350, 160, BLUE, "#a5d8ff")
    d.arrow("propose", [(550, 433), (320, 433)], BLUE)
    d.text("propose-label", "提出知识修改", 351, 389, 180, 23, BLUE, 8)
    card(d, "write-gate", "检查知识写入", "获准后保存\n待批准先暂存\n审批拒绝：不提交\n执行报错：读回核对", 40, 365, 280, 188, ORANGE, "#ffd8a8")
    d.arrow("save-memory", [(180, 365), (180, 277)], GREEN)
    d.text("save-memory-label", "短事实", 199, 305, 115, 23, GREEN, 8)
    d.arrow("stage", [(180, 553), (180, 619)], ORANGE)
    d.text("stage-label", "需批准", 199, 567, 115, 23, ORANGE, 8)
    card(d, "pending", "pending", "先暂存，批准后提交", 40, 619, 280, 111, ORANGE, "#fff3bf")

    d.arrow("save-skill", [(320, 489), (432, 489), (432, 674), (550, 674)], GREEN)
    d.text("save-skill-label", "流程知识", 439, 610, 105, 23, GREEN, 8)
    card(d, "skill-files", "Skill 文件", "SKILL.md / references", 550, 619, 350, 111, GREEN, "#c3fae8")
    d.arrow("skill-view", [(725, 619), (725, 525)], GREEN)
    d.text("skill-view-label", "skill_view\n按需读取", 746, 551, 150, 23, GREEN, 8)

    d.text("boundary", "后台复盘按条件触发；无人值守时先暂存删除提议。", 42, 770, 855, 23, MUTED, 8)
    d.text("not-training", "保存的是资料，模型权重未更新；后续还要检查怎么使用。", 42, 807, 855, 23, MUTED, 8)
    for element in d.elements:
        if element["type"] == "rectangle":
            element["roughness"] = 1
        elif element["type"] == "arrow":
            element.update(roughness=1, strokeWidth=3)
            if element["id"] in {"reload", "stage"}:
                element["strokeStyle"] = "dashed"
    d.save(Path(__file__).with_name("scene.excalidraw"))


if __name__ == "__main__":
    main()
