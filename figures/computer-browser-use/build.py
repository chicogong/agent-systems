"""Build a teaching diagram of hybrid UI observation and host-controlled actions."""

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
elements = []


def base(kind, name, x, y, width, height, stroke="#233246", fill="transparent", weight=2):
    item = {
        "id": name, "type": kind, "x": x, "y": y, "width": width, "height": height,
        "angle": 0, "strokeColor": stroke, "backgroundColor": fill,
        "fillStyle": "solid", "strokeWidth": weight, "strokeStyle": "solid",
        "roughness": 1, "opacity": 100, "groupIds": [], "frameId": None,
        "index": f"a{len(elements):04d}", "roundness": {"type": 3} if kind == "rectangle" else None,
        "seed": 6500 + len(elements), "version": 1, "versionNonce": 8500 + len(elements),
        "isDeleted": False, "boundElements": [], "updated": 1, "link": None, "locked": False,
    }
    elements.append(item)
    return item


def box(name, x, y, width, height, stroke, fill, dashed=False):
    item = base("rectangle", name, x, y, width, height, stroke, fill)
    if dashed:
        item["strokeStyle"] = "dashed"


def text(name, value, x, y, width, height, size=24, color="#233246", code=False):
    item = base("text", name, x, y, width, height, color, weight=1)
    item.update(text=value, originalText=value, fontSize=size, fontFamily=8 if code else 6,
                textAlign="left", verticalAlign="middle", containerId=None,
                autoResize=False, lineHeight=1.25)


def arrow(name, x, y, points, color="#56768c", dashed=False):
    xs, ys = zip(*points)
    item = base("arrow", name, x, y, max(xs) - min(xs), max(ys) - min(ys), color, weight=3)
    item.update(points=[list(point) for point in points], lastCommittedPoint=None,
                startBinding=None, endBinding=None, startArrowhead=None,
                endArrowhead="arrow", elbowed=False)
    if dashed:
        item["strokeStyle"] = "dashed"


text("main-conclusion", "两种观察通道可混用，动作仍须授权与验收", 34, 28, 1050, 44, 29)
box("observation-group", 24, 100, 340, 450, "#bdd8df", "#f3f9fa", dashed=True)
text("observation-title", "本轮观察 · 按任务组合", 44, 113, 300, 36, 24, "#426c7c")

box("pixels", 46, 172, 294, 132, "#4aa1dd", "#c4e6ff")
text("pixels-title", "截图 → 坐标", 66, 190, 254, 42, 28, code=True)
text("pixels-sub", "像素 · 缩放 · 时效", 66, 249, 254, 34)

box("structure", 46, 355, 294, 139, "#8b65d9", "#e5d6ff")
text("structure-title", "DOM / AX tree", 66, 372, 254, 42, 28, code=True)
text("structure-sub", "元素 · 角色 · 当前引用", 66, 438, 254, 34, 23)
text("group-note", "不是互斥产品分类", 63, 510, 260, 32, 24, "#426c7c")

box("proposal", 452, 285, 233, 140, "#9270d1", "#e7dcfb")
text("proposal-title", "动作提案", 477, 306, 186, 42, 28)
text("proposal-sub", "点哪里 / 填什么", 475, 370, 192, 35, 24, code=True)

box("host", 790, 285, 278, 140, "#e59930", "#ffe0a8")
text("host-title", "宿主校验与执行", 814, 308, 236, 39, 27)
text("host-sub", "范围 · 权限 · 前置状态", 811, 373, 240, 33, 23)

box("stop", 790, 167, 278, 61, "#cc7770", "#ffdfda")
text("stop-title", "越界 / 未获准 → 停止", 811, 181, 243, 34, 23)

box("verification", 790, 525, 278, 120, "#52a171", "#c7edd3")
text("verification-title", "重新观察 / 读回", 813, 539, 240, 38, 26)
text("verification-sub", "结果符合任务吗？", 813, 594, 240, 34, 24)

arrow("pixels-proposal", 340, 238, [(0, 0), (56, 0), (112, 83)], "#4aa1dd")
arrow("structure-proposal", 340, 425, [(0, 0), (56, 0), (112, -35)], "#8b65d9")
arrow("proposal-host", 685, 355, [(0, 0), (105, 0)], "#9270d1")
text("request-label", "调用请求", 695, 310, 93, 32, 23, "#7557ad")
arrow("host-stop", 929, 285, [(0, 0), (0, -57)], "#cc7770")
text("stop-label", "校验不通过", 951, 242, 137, 30, 22, "#9b564d")
arrow("host-verification", 929, 425, [(0, 0), (0, 100)], "#e59930")
text("receipt-label", "回执 ≠ 完成", 949, 461, 143, 32, 22, "#a57022")
arrow("refresh-loop", 790, 585, [(0, 0), (-77, 0), (-77, 118), (-596, 118), (-596, -35)], "#52a171", dashed=True)
text("refresh-label", "未满足停止条件：刷新后再提案", 278, 659, 450, 34, 24, "#47745a")
text("done-label", "满足合同 → 停止并报告", 790, 680, 295, 34, 24, "#47745a")
arrow("verified-end", 1015, 645, [(0, 0), (0, 30)], "#52a171")

scene = {
    "type": "excalidraw", "version": 2, "source": "https://excalidraw.com",
    "elements": elements, "appState": {"viewBackgroundColor": "#ffffff", "gridSize": None}, "files": {},
}
(HERE / "scene.excalidraw").write_text(json.dumps(scene, ensure_ascii=False, indent=2) + "\n")
