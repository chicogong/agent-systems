"""Build the KV Prefix Cache hit vs bust diagram."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from diagram_style import Scene, INK, MUTED

BLUE, RED, GREEN = "#3478e5", "#d94848", "#289e62"


def main() -> None:
    d = Scene()
    d.text("title", "前缀缓存（KV Cache）经济学：前段稳如磐石，变化留在队尾", 28, 22, 1080, 31, INK, 6)
    d.text("subtitle", "多步循环输入远大于输出；前缀改一个字符就会让后续全部历史缓存作废，成本与首字延迟飙升", 28, 64, 1080, 20, MUTED)

    # Top Lane: Bad Pattern - Prefix Mutation
    d.box("bad-lane", 28, 114, 1088, 210, RED, "#fff5f5")
    d.text("bad-title", "反模式：动了开头的字节，整条长历史每轮全量重算（0% 缓存复用）", 48, 130, 1040, 21, RED)

    d.box("bad-b1", 48, 170, 254, 92, RED, "#ffe3e3")
    d.text("bad-b1-t", "首行塞秒级动态时间戳\n或每轮增删工具列表", 64, 190, 222, 19, INK)

    d.box("bad-b2", 326, 170, 246, 92, RED, "#ffe3e3")
    d.text("bad-b2-t", "滑动窗口逐轮踢第 1 条\n导致整队消息位置左移", 342, 190, 216, 19, INK)

    d.box("bad-b3", 596, 170, 240, 92, RED, "#ffe3e3")
    d.text("bad-b3-t", "第 2–29 轮对话与日志\n被迫全部重新算 KV", 612, 190, 210, 19, INK)

    d.box("bad-res", 860, 170, 234, 92, RED, "#ffd1d1")
    d.text("bad-res-t", "全额计费 + 高延迟\n步数越多越昂贵", 878, 190, 200, 19, RED)

    d.arrow("bad-a1", [(302, 216), (326, 216)], RED)
    d.arrow("bad-a2", [(572, 216), (596, 216)], RED)
    d.arrow("bad-a3", [(836, 216), (860, 216)], RED)
    d.text("bad-note", "连锁失效点：推理引擎按精确前缀匹配复用 KV 状态，开头一变，后面几万 Token 全部失配", 48, 282, 1040, 19, MUTED)

    # Bottom Lane: Good Pattern - Cache-Aware Append-Only Harness
    d.box("good-lane", 28, 356, 1088, 248, GREEN, "#eefaf3")
    d.text("good-title", "工程正道：固定前缀顺序 + 纯追加消息流 + 满水位分段压缩（90%+ 前缀命中）", 48, 372, 1040, 21, GREEN)

    d.box("good-b1", 48, 414, 248, 106, GREEN, "#d8f5e5")
    d.text("good-b1-h", "① 静态指令与工具表", 64, 430, 216, 19, GREEN)
    d.text("good-b1-b", "工具排序稳定；禁工具走\n宿主门禁而非删声明", 64, 462, 216, 19, INK)

    d.box("good-b2", 320, 414, 240, 106, GREEN, "#d8f5e5")
    d.text("good-b2-h", "② 项目约定与阶段摘要", 336, 430, 210, 19, GREEN)
    d.text("good-b2-b", "AGENTS.md 与压缩块\n在数十步内保持不动", 336, 462, 210, 19, INK)

    d.box("good-b3", 584, 414, 246, 106, GREEN, "#d8f5e5")
    d.text("good-b3-h", "③ 纯追加历史消息流", 600, 430, 216, 19, GREEN)
    d.text("good-b3-b", "已发消息绝不原地改写\n直接命中上轮缓存前缀", 600, 462, 216, 19, INK)

    d.box("good-b4", 854, 414, 240, 106, BLUE, "#e6f0ff")
    d.text("good-b4-h", "④ 队尾新观察（增量）", 870, 430, 210, 19, BLUE)
    d.text("good-b4-b", "本轮新工具输出与动态\n提醒一律追加在最末尾", 870, 462, 210, 19, INK)

    d.arrow("good-a1", [(296, 467), (320, 467)], GREEN)
    d.arrow("good-a2", [(560, 467), (584, 467)], GREEN)
    d.arrow("good-a3", [(830, 467), (854, 467)], BLUE)

    d.text(
        "good-note",
        "缓存命中：① + ② + ③ 直接读缓存（省约 90% 输入单价与首字耗时）｜逼近窗口水位线时才触发一次分段压缩",
        48,
        548,
        1040,
        19,
        MUTED,
    )

    for element in d.elements:
        if element["type"] in {"rectangle", "arrow"}:
            element["roughness"] = 1
        if element["type"] == "arrow":
            element["strokeWidth"] = 3

    d.save(ROOT / "figures/prefix-cache-mechanics/scene.excalidraw")


if __name__ == "__main__":
    main()
