# 本地 HTTP 回执实验

[教材正文](../../docs/labs/http-receipt.md)

Python 3.10+ 标准库。只绑定 `127.0.0.1` 动态端口，运行完关闭；不访问外网、不写文件、不操作真实账号。HTTP 连接和读超时真实发生，登记账本及故障安排是教学夹具，不是生产 API 或模型驱动 Agent。

```bash
python3 examples/http-receipt/demo.py --mode timeout_then_lookup
python3 examples/http-receipt/demo.py --mode late_commit
python3 -m unittest discover -s examples/http-receipt -p 'test_*.py'
```

`normal`、`timeout_then_lookup`、`same_id_retry` 返回 0；`lookup_lag`、`late_commit`、`unsafe_new_id`、`payload_conflict` 返回 2。2 表示宿主结论未获确认或命中反例，不代表远端一定没登记。遇到无法建立预期的故障夹具，程序抛异常，不能把异常算作成功演示。

原始输出分 `host` 和 `observer_after_cleanup`：宿主只根据 HTTP 证据判断，观察者在释放迟到请求并清理后看内部账本。不要用后者倒推宿主当时知道结果。服务用进程内锁保证同 ID、同 payload 的登记重放；该保证不持久化、不涉及真正部署事务，也不延伸到其他 API。
