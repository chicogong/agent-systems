"""Build the Persisted on Disk vs Visible in Context 4-stage funnel diagram."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from diagram_style import Scene, INK, MUTED

BLUE, PURPLE, GREEN, AMBER, RED = "#3478e5", "#7c52e0", "#289e62", "#d97706", "#d94848"


def main() -> None:
    d = Scene()
    d.text("title", "存下来了 ≠ 模型本轮看见了：排查「假性失忆」的四道漏斗", 28, 22, 1080, 31, INK, 6)
    d.text("subtitle", "大模型是无状态函数；磁盘里的字节必须闯过「落盘、命中、编译装入、注意力竞争」四关才真正生效", 28, 64, 1080, 20, MUTED)

    stages = [
        (
            "g1",
            114,
            BLUE,
            "#eef5ff",
            "第 1 关：物理落盘保存（Storage）",
            "真正写进 JSONL / Markdown / 数据库",
            "口头答应「记住了」却未调写工具，\n或底层写入因权限不足返回报错",
        ),
        (
            "g2",
            242,
            PURPLE,
            "#f5f0ff",
            "第 2 关：分支投影与检索命中（Selection）",
            "Pi 沿当前活跃叶子投影；Letta 区分常驻与 recall",
            "切分支把约束甩在旁支；或放进\n按需参考目录却未触发检索命中",
        ),
        (
            "g3",
            370,
            AMBER,
            "#fff8eb",
            "第 3 关：预算装配与提示重编译（Assembly）",
            "Pi 经 transformContext 裁剪；Letta 重编译提示",
            "超窗口预算被截断丢弃；或刚改完\n文件但当前回合仍沿用旧提示快照",
        ),
        (
            "g4",
            498,
            GREEN,
            "#ebfaf2",
            "第 4 关：进入请求 Payload 并赢得注意力",
            "规则出现在 system / messages 且信噪比清晰",
            "字节虽已进请求，但夹在几万字报错\n堆栈中间被稀释（Lost in Middle）",
        ),
    ]

    for idx, (key, y, color, fill, h_txt, pass_txt, drop_txt) in enumerate(stages):
        # Left funnel stage box (x=28..596, w=568)
        d.box(key, 28, y, 568, 104, color, fill)
        d.text(f"{key}-h", h_txt, 48, y + 16, 528, 20, color)
        d.text(f"{key}-p", pass_txt, 48, y + 54, 528, 19, INK)

        # Right failure leak box (x=656..1116, w=460)
        d.box(f"{key}-drop", 656, y, 460, 104, RED, "#fff5f5")
        d.text(f"{key}-dh", f"失忆漏点 {idx + 1}", 676, y + 12, 420, 19, RED)
        d.text(f"{key}-db", drop_txt, 676, y + 42, 420, 19, MUTED)

        # Dashed leak arrow to right
        d.arrow(f"{key}-leak", [(596, y + 52), (656, y + 52)], RED)
        d.elements[-1]["strokeStyle"] = "dashed"

        # Solid downward arrow to next stage
        if idx < len(stages) - 1:
            next_y = stages[idx + 1][1]
            d.arrow(f"{key}-down", [(312, y + 104), (312, next_y)], color)

    d.text(
        "foot",
        "实战三步定责：① 查磁盘原件验第 1 关 → ② 抓本次请求 JSON 验第 2、3 关 → ③ 请求里有仍跑偏再治第 4 关噪音",
        28,
        622,
        1088,
        19,
        INK,
    )

    for element in d.elements:
        if element["type"] in {"rectangle", "arrow"}:
            element["roughness"] = 1
        if element["type"] == "arrow":
            element["strokeWidth"] = 3

    d.save(ROOT / "figures/persisted-vs-visible/scene.excalidraw")


if __name__ == "__main__":
    main()
