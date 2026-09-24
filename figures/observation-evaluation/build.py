"""Build the editable evidence-convergence diagram."""

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
elements = []


def base(kind, name, x, y, w, h, stroke="#34485c", fill="transparent", width=2):
    e = {
        "id": name, "type": kind, "x": x, "y": y, "width": w, "height": h,
        "angle": 0, "strokeColor": stroke, "backgroundColor": fill,
        "fillStyle": "solid", "strokeWidth": width, "strokeStyle": "solid",
        "roughness": 1, "opacity": 100, "groupIds": [], "frameId": None,
        "index": f"a{len(elements):04d}", "roundness": {"type": 3} if kind == "rectangle" else None,
        "seed": 3000 + len(elements), "version": 1, "versionNonce": 9000 + len(elements),
        "isDeleted": False, "boundElements": [], "updated": 1, "link": None, "locked": False,
    }
    elements.append(e)
    return e


def box(name, x, y, w, h, stroke, fill, width=2):
    base("rectangle", name, x, y, w, h, stroke, fill, width)


def label(name, value, x, y, w, h, size=24, color="#233246"):
    e = base("text", name, x, y, w, h, color, width=1)
    e.update(text=value, fontSize=size, fontFamily=6, textAlign="left",
             verticalAlign="middle", containerId=None, originalText=value,
             autoResize=False, lineHeight=1.25)


def arrow(name, x, y, points, color="#3c5369"):
    xs, ys = zip(*points)
    e = base("arrow", name, x, y, max(xs) - min(xs), max(ys) - min(ys), color, width=3)
    e.update(points=[list(p) for p in points], lastCommittedPoint=None,
             startBinding=None, endBinding=None, startArrowhead=None,
             endArrowhead="arrow", elbowed=False)


# Source scales are deliberately separate: one execution, many tasks, actual use.
box("single-band", 28, 38, 748, 474, "#d6e5ec", "#f3f8fa", 1)
label("single-heading", "单次运行 · 还原发生了什么", 56, 56, 680, 39, 26, "#2d5b73")
box("run", 58, 191, 228, 163, "#4c7d92", "#e5f1f5")
label("run-title", "一次 Agent 运行", 81, 212, 185, 43, 27, "#244b61")
label("run-sub", "输入 · 工具 · 结果", 81, 274, 185, 37, 22)
for key, y, title, subtitle, stroke, fill in [
    ("log", 100, "日志", "事件与错误", "#3e7790", "#eaf5f7"),
    ("trace", 240, "trace", "步骤与调用关联", "#4c7791", "#edf3fb"),
    ("assert", 380, "断言结果", "仅检验写出的条件", "#9a7040", "#fff5e8"),
]:
    box(key, 455, y, 272, 106, stroke, fill)
    label(f"{key}-title", title, 479, y + 12, 224, 39, 26, stroke)
    label(f"{key}-sub", subtitle, 479, y + 58, 224, 30, 22)
arrow("run-log", 286, 232, [(0, 0), (100, 0), (169, -79)])
label("run-log-label", "产生", 315, 177, 70, 28, 22, "#41586c")
arrow("run-trace", 286, 270, [(0, 0), (169, 23)])
label("run-trace-label", "关联", 334, 229, 70, 29, 22, "#41586c")
arrow("run-assert", 286, 312, [(0, 0), (98, 0), (169, 121)])
label("run-assert-label", "检验", 315, 335, 70, 29, 22, "#705840")

box("multi-band", 28, 548, 748, 182, "#e5dded", "#faf6fc", 1)
label("multi-heading", "跨多次任务 · 看版本表现", 56, 563, 680, 38, 26, "#765983")
box("sample", 58, 626, 228, 73, "#8b6b98", "#f2eaf5")
label("sample-label", "固定任务集", 80, 639, 182, 42, 25, "#664b73")
box("eval", 455, 615, 272, 91, "#8b6b98", "#f2eaf5")
label("eval-title", "离线 eval", 479, 622, 224, 39, 26, "#664b73")
label("eval-sub", "逐例结果与汇总", 479, 664, 224, 30, 22)
arrow("sample-eval", 286, 661, [(0, 0), (169, 0)], "#735a80")
label("sample-eval-label", "汇总评分", 310, 626, 130, 27, 22, "#6d567a")

box("human-band", 28, 758, 748, 160, "#dcebdc", "#f4faf3", 1)
label("human-heading", "实际使用 · 找到盲点", 56, 772, 680, 38, 26, "#4a7158")
box("experience", 58, 834, 228, 62, "#5b8767", "#e9f6e9")
label("experience-label", "失败样例 / 体验", 76, 842, 194, 42, 23, "#3f654d")
box("human", 455, 825, 272, 75, "#5b8767", "#e9f6e9")
label("human-title", "人工反馈", 479, 830, 224, 37, 26, "#3f654d")
label("human-sub", "语义与可接受性", 479, 864, 224, 29, 22)
arrow("experience-human", 286, 866, [(0, 0), (169, 0)], "#53745d")
label("experience-human-label", "复核", 342, 835, 75, 27, 22, "#4b6d55")

box("conclusion", 904, 322, 392, 260, "#46657c", "#eaf2f5", 3)
label("conclusion-title", "有范围的结论", 939, 350, 325, 50, 30, "#2d526a")
label("conclusion-coverage", "版本 · 样本 · 环境 · 判据", 939, 423, 325, 37, 22)
label("conclusion-limit", "写明未覆盖项与失败例", 939, 478, 325, 37, 22, "#485c6c")
box("not-proven", 904, 626, 392, 148, "#a1685c", "#fff2ed")
label("not-proven-title", "不能据此推出", 939, 642, 325, 43, 26, "#925346")
label("not-proven-body", "全面正确 · 产品可用 · 安全", 939, 704, 325, 36, 22, "#6c4945")

# Separate incoming channels avoid implying that one form of evidence causes another.
for key, sy, ey, relation, ly in [
    ("log", 153, 360, "记录范围", 103),
    ("trace", 293, 398, "过程关联", 242),
    ("assert", 433, 436, "条件检验", 385),
    ("eval", 661, 492, "汇总表现", 625),
    ("human", 866, 540, "复核体验", 809),
]:
    arrow(f"{key}-conclusion", 727, sy, [(0, 0), (76, 0), (177, ey - sy)])
    label(f"{key}-relation", relation, 795, ly, 100, 30, 22, "#48596a")

scene = {
    "type": "excalidraw", "version": 2, "source": "https://excalidraw.com",
    "elements": elements, "appState": {"viewBackgroundColor": "#ffffff", "gridSize": None},
    "files": {},
}
(HERE / "scene.excalidraw").write_text(json.dumps(scene, ensure_ascii=False, indent=2) + "\n")
