# 证据合同练习：独立冷读与复跑

日期：2026-09-27。审稿者未编写本练习；核对 `examples/evidence-contract/{demo.py,test_demo.py,README.md}`、`docs/labs/evidence-contract.md` 与学习路径新增导航。只新增本报告，没有修改练习源码或主稿，没有提交、推送、调用真实模型、登录账号或访问外部服务。

## 结论与修订记录

三个固定案例与正文说明一致，8 个测试均通过。没有发现阻断这份教学夹具合稿的事实或运行缺陷。它足以展示「观察、许可、执行、验收」的责任分开，但不能据此声称真实提示注入防护、OS 隔离或摘要语义正确。

| 冷读发现 | 合稿者处理／复验 |
| --- | --- |
| examples README 的代码块原有四条命令，随后“后两条退出码为 2”会把测试命令也算进去 | 已反馈并由合稿者明确改为 forged／injection 为 2，valid／测试为 0；实际复跑确认一致。 |
| 学习路径新导航原写成 `**补一条证据链：**完成`，CommonMark 将这一段显示为裸星号 | 已反馈并由合稿者补空格；读取修订后原文，再用 CommonMark 实际解析，确认产生 `<strong>`，无裸星号。 |

## 实际运行证据

本机 Python **3.14.6**，从仓库根目录运行。未在 Python 3.10 或其他 OS 独立复跑；代码使用的语法和标准库没有发现高于文档所述 3.10 的要求，兼容性判断不替代矩阵测试。

```bash
python3 -m unittest discover -s examples/evidence-contract -p 'test_*.py' -v
python3 examples/evidence-contract/demo.py --case valid
python3 examples/evidence-contract/demo.py --case forged
python3 examples/evidence-contract/demo.py --case injection
```

测试命令实际为 **8 tests，OK，退出码 0**。另用 `subprocess.run()` 分别调用三条 CLI、解析其 stdout 的 JSON，并核对返回码；不是依赖 shell 中最后一条命令的返回码推断前面的结果。

| CLI 案例 | 实际退出码 | 状态与轨迹 | 验收 |
| --- | --- | --- | --- |
| valid | 0 | `state` 有 `summary`；有获准决策和 `tool_result` | `accepted: true`，理由为空 |
| forged | 2 | `state` 同样有 `summary`；模拟工具写入成功 | `accepted: false`，`source_not_verified:s3` |
| injection | 2 | `state` 为空；没有成功 `tool_result` | `not_executed`、`operation_out_of_scope`、缺少 s1／s2 的已验证引文 |

三个 CLI 的 stderr 均为空，预期拒绝不是程序崩溃。正常与 forged 有三个 observation，再依次 proposal、host_decision、tool_result、audit；injection 跳过 tool_result，与正文相符。

## 八个测试是否彼此独立

除一次标准发现运行外，又将每个测试分别放进新的 Python 进程执行，**八次均退出 0**；还将八个测试反序放在同一进程执行，仍为 **8 tests，OK**，执行前后的 `SOURCES` 深拷贝比较相等。

源码上，`run()` 每次新建 observations、proposal、citations、trace 与 state；后三个修改提案的测试修改的是各自本次 `run()` 的结果，不会改写 `SOURCES`。复制同一条引用两次只改变该案例的列表，不能充当 s2 的覆盖证据。

这证明当前八个固定测试不依赖默认测试顺序或前一个案例污染，**不证明**任意输入结构、并发调用或所有异常都已覆盖。CLI 返回码是本次额外手工复跑的证据，不是已有八个单元测试中的断言。

## 教程与代码边界核对

- **marker 不是防注入。** `demo.py:19` 根据固定 marker 让刻意脆弱的提案器改变操作；真正拒绝来自 `host_execute()` 对 `CONTRACT` 的操作名比较，不是模型识别到攻击或某个通用检测器。程序没有 export_credentials 的实现。正文第 39 行和 examples README 均明确限定。
- **内存写不是 OS 隔离。** `demo.py:34` 只把 proposal 放进当前进程的字典。没有文件权限隔离、容器、浏览器、网络出口或凭据测试。解释中的“写入成功”限定为这个模拟工具，不冒充真实环境安全。
- **引用验证不等于语义验证。** `audit()` 检查动作、完成声明、已执行布尔值、所需来源、来源取得标记与逐字片段；只要片段存在，仍可能出现断章取义、来源错误或推论不成立。第 57 行的自测答案正确保留这些缺口。
- **提案不是执行证明。** `status: completed` 是夹具中的自称完成，宿主的执行结果另传；forged 展示执行成功仍可被独立验收拒绝，injection 展示安全拒绝不等于业务成功。
- **独立验收是职责分离，不是隔离进程。** audit 使用可信固定 `SOURCES`，不直接接受 observations 中追加的要求；但它与宿主仍在同一 Python 进程，不是密码学可信边界，也没有被教程描述为此类边界。
- **学习导航范围适当。** 第四层新增入口与 Computer／Browser Use、sandbox 的前置材料呼应，明确练习无模型、无网络且不是完整防注入系统；相对链接目标实际存在。不要求读者先配置账号或运行真实工具。

## 未覆盖的验收

没有运行网页或 PDF 的完整构建，没有确认阅读包分发后的文件打包完整性，也没有评估手机、A4 缩排或真人理解效果。Markdown 导航检查只使用本机 `markdown_it` 的 CommonMark 解析；最终站点由合稿者检查。上游框架、防注入系统或真实 Agent 的行为不在这个夹具的复跑范围内。

## 附加图稿复看：Computer／Browser 的停止出口

合稿者重导出后，实际打开最新的 `figures/computer-browser-use/preview.png`（4,352 × 2,824），重新阅读图说明，没有沿用旧图的校验结论。红色“校验不通过 → 越界／未获准 → 停止”和绿色“满足合同 → 停止并报告”均可见；未满足停止条件的绿色虚线回到本轮观察，保留刷新后再提案的语义。箭头未穿文字，未见新增节点遮挡、字形截断或错误连接。

这张图的初稿由本审稿者撰写，因此本段是**修订后目视复验，不是独立作者交叉审图**。它也没有验证 SVG、MCP 像素一致性、A4 排版或真实 Computer Use 的运行行为。DSH 的独立目视范围另补在 [新系统二审](2026-09-27-new-systems-review.md)。
