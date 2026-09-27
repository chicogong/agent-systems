"""A local teaching projection of the fixed DSH tool batch scheduler."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
from diagram_style import Scene, BLUE, GREEN, ORANGE, PURPLE, MUTED

s = Scene()
s.text('hint', '同一批次：执行可重叠，结果提交有次序', 25, 15, 940, 30, font=6)
for name, x, title, code, color, fill in [
    ('calls', 25, '先记录请求', 'A → B → C', BLUE, '#a5d8ff'),
    ('dispatch', 355, '有界池执行', 'B 完成 → A → C', PURPLE, '#d0bfff'),
    ('commit', 715, '连续 ready 才提交', 'A → B → C', GREEN, '#b2f2bb'),
]:
    s.box(name, x, 130, 280, 150, color, fill)
    s.text(name+'-title', title, x+18, 151, 245, 25, font=6)
    s.text(name+'-code', code, x+18, 210, 245, 26, font=8)
s.arrow('prepare', [(305, 205), (355, 205)], BLUE)
s.arrow('ready', [(635, 205), (715, 205)], GREEN)
s.text('gate', '准备 / 审批', 278, 90, 140, 21, BLUE, font=6)
s.text('wait', '等 A ready', 647, 298, 250, 24, GREEN, font=8)
s.box('deny', 30, 370, 415, 110, ORANGE, '#ffec99')
s.text('deny-label', '需要 ask，但无审批通道\n拒绝，不进入 dispatch', 48, 393, 382, 24, font=6)
s.arrow('ask', [(150, 280), (150, 370)], ORANGE)
s.box('outside', 565, 370, 430, 110, PURPLE, '#e5dbff')
s.text('outside-label', '远端副作用：B 可能先发生\n有序日志 ≠ 外部世界串行', 585, 393, 392, 24, font=6)
s.arrow('effect', [(505, 280), (505, 420), (565, 420)], PURPLE)
for e in s.elements:
    if e['type'] != 'text':
        e['roughness'] = 1
    if e['type'] == 'arrow':
        e['strokeWidth'] = 3
        if e['id'] in ('ask', 'effect'):
            e['strokeStyle'] = 'dashed'
s.save(Path(__file__).with_name('scene.excalidraw'))
