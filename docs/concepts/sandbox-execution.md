# 沙箱执行环境：给代码一块合适的工作空间

[返回机制目录](README.md) · [审批与隔离](approval-vs-sandbox.md) · [外部动作与恢复](../comparisons/permission-and-recovery.md)

你让助手修复一个 CSV 转换脚本。它需要读取样例、写入结果、运行测试。可以给它一个专门的执行环境，只放这次任务需要的文件，设置运行时间和资源限制。这个环境通常叫作**沙箱**。

这样安排以后，私人目录、工作账号和生产密钥可以留在任务之外。具体限制要由运行环境和配置落实。

![资源合同、隔离执行、结果账本与远端副作用](../../figures/sandbox-execution/diagram.svg)

[可编辑图源](../../figures/sandbox-execution/scene.excalidraw) · [PNG 预览](../../figures/sandbox-execution/preview.png) · [图的文字版](../../figures/sandbox-execution/README.md)

图中实线是示例流程，外圈虚线标出执行环境，橙色虚线表示任务获得许可后访问网络的路径。

## 先列出任务需要的资源

对 CSV 任务，可以先写一张短清单：输入目录只读，输出目录可写；运行测试有时限；不放真实密钥；默认不访问外网。这是本书的示例设置，实际平台的默认值需要另行检查。

主要安排五项：

- **文件。** 指定输入、输出和临时目录，检查哪些文件可以读写。工作目录用于解析相对路径，访问限制另由权限处理。
- **网络。** 指定是否联网，以及允许的服务。下载依赖与上传数据都会产生网络请求。
- **进程和资源。** 指定运行用户、时间、CPU 和内存限制，安排超时后的终止方式。
- **密钥。** 只提供任务需要的凭据，限制使用范围和有效期，避免写入日志。
- **浏览器身份。** 使用浏览器时，确认有没有加载个人登录状态。

E2B 文档说明沙箱默认允许出网；Daytona 的网络限制还受组织配置影响。实际使用时，检查创建参数和账户设置。[E2B 网络配置](https://docs.e2b.dev/network/internet-access) · [Daytona 网络限制](https://www.daytona.io/docs/en/network-limits/)

浏览器认证文件可能包含可用于登录的 cookies 和 headers，需要保护，避免提交到仓库。[Playwright 认证说明](https://playwright.dev/docs/auth)

## 常见执行环境怎样区分

这些技术工作在不同层次，可以配合使用。

| 选择 | 主要作用 | 使用时关注 |
| --- | --- | --- |
| 本地进程策略 | 用操作系统机制限制文件、进程或网络访问 | 限制是否作用于实际进程及其子进程 |
| Linux 容器 | 划分资源视图，管理资源使用 | 文件挂载、权限和宿主内核 |
| gVisor | 用应用内核处理工作负载的系统调用 | 隔离方式和程序兼容性 |
| Firecracker microVM | 用轻量虚拟机运行独立客体环境 | 虚拟机管理进程的权限和网络配置 |
| E2B、Daytona 等平台 | 用服务 API 创建和管理执行环境 | 账户权限、数据位置和生命周期 |

### 容器：划分资源视图，限制用量

Linux 的 namespaces 让进程看到各自的资源视图；cgroups 管理资源用量和限制。这两项机制还需要配合挂载和权限设置。

例如只挂入样例目录，比挂入整个个人目录更符合 CSV 任务。Docker 控制接口也要谨慎开放：能控制 daemon 的程序可能创建强大的挂载，影响宿主文件系统。

[Docker 安全说明](https://docs.docker.com/engine/security/) · [系统调用过滤](https://docs.docker.com/engine/security/seccomp/) · [daemon 的权限风险](https://docs.docker.com/engine/security/#docker-daemon-attack-surface)

### gVisor：在系统调用之间增加一层处理

gVisor 用用户态的应用内核 Sentry 处理工作负载的系统调用，再通过受限接口与宿主交互。这里的系统调用，是程序请求操作系统提供文件、进程等服务的接口。

增加这一层也会带来兼容性取舍。准备使用前，测试任务所需的程序和依赖。

[架构说明](https://gvisor.dev/docs/architecture_guide/intro/) · [兼容性说明](https://gvisor.dev/docs/user_guide/compatibility/)

### Firecracker：用轻量虚拟机执行

Firecracker 是 microVM 的虚拟机管理器，利用 Linux KVM 运行客体环境。官方设计建议在生产中用 `jailer` 降低管理进程权限。

出网过滤由宿主集成来安排，Firecracker 本身不做网络流量过滤。[固定版本设计文档](https://github.com/firecracker-microvm/firecracker/blob/edb60617c31ebd610c530f67706ec5c79d4c2725/docs/design.md)

### OpenShell：把资源策略接入运行环境

NVIDIA OpenShell 的资料介绍了文件、进程、出网和推理路由等控制。文件与进程策略在创建时锁定，网络与推理配置可以运行时更新。

它适合用来理解“执行环境怎样接上资源策略”，而内核隔离方式需要结合其实际运行环境查看。[官方项目](https://github.com/NVIDIA/OpenShell) · [配置建议](https://docs.nvidia.com/openshell/security/best-practices.md)

## 从创建到结束，把结果带出来

运行 CSV 任务的程序，可以按以下顺序安排：

1. 选择环境，设置资源，记下环境 ID。
2. 放入需要的样例和代码。
3. 运行脚本，保存退出状态、日志和输出。
4. 在环境外按任务要求检查 CSV 内容。
5. 保存需要的产物，再按计划停止或删除环境。

这是一种应用编排示例。检查输出时，也把返回文件当作待检查材料处理，避免直接在宿主执行陌生脚本。

环境结束后的保留方式要单独看。Daytona 的停止操作保留文件系统、清除内存；Linux VM 和 Windows 环境另外支持保留内存的暂停，容器不支持这种暂停。E2B 暂停可以保存文件和内存，也能选择只保存文件、恢复时重新启动；`kill` 是终止操作。

[Daytona 停止与暂停](https://www.daytona.io/docs/en/sandboxes/#stop-sandboxes) · [E2B 持久化](https://docs.e2b.dev/sandbox/persistence)

保存执行环境之后，模型下次需要哪些消息和资料，仍由 Agent 的运行程序安排。[会话与记忆](session-compaction-and-memory.md)讨论了这部分。

## 远端操作需要另外检查

如果任务允许登录后台并发布内容，发布发生在远端服务。结束本地执行环境以后，仍需查询发布状态。遇到返回消息丢失时，先查原操作，再考虑重试。

[回执丢失小实验](../labs/remote-effect.md)可以帮助理解这一过程，它使用模拟服务，不测试真实沙箱的隔离能力。

## 可选深入：用假数据检查配置

在专门的测试环境放入假数据，检查范围外文件能否读取、子进程是否受到限制、超时后进程是否结束、输出能否取回。若需要测试网络或密钥访问，使用专门的测试凭据，避免接入个人账号和生产数据。

本章依据官方文档解释机制，没有安装这些运行时，也没有测试隔离逃逸。选择方案时还需要结合自己的任务验证兼容性和配置，不据此对安全强度或速度排名。
