# 不可信观察与假完成：教学夹具

[完整练习](../../docs/labs/evidence-contract.md)。Python 3.10+，标准库；没有模型、网络、磁盘写入或真正的隔离沙箱。`state` 只是当前进程的内存字典，引用检查只验证固定结构和逐字片段，不证明自然语言摘要忠实。

```bash
python3 examples/evidence-contract/demo.py --case valid
python3 examples/evidence-contract/demo.py --case forged
python3 examples/evidence-contract/demo.py --case injection
python3 -m unittest discover -s examples/evidence-contract -p 'test_*.py'
```

`forged` 与 `injection` 退出码为 2 是预期验收拒绝；不是程序崩溃。`valid` 与测试命令正常退出码为 0。不要用这个固定 marker 规则当作真实提示注入检测器，也不要在本机改成实际读取、导出凭据。
