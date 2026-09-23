# 贡献指南

欢迎帮助改正源码定位、图解、文字和打印问题。请先读[编辑计划](docs/editorial-plan.md)及[来源规则](sources/README.md)。本仓库欢迎具体反例和可复核的修正，不接受无来源的项目排名或把静态源码解读写成运行事实。

提交文章时说明研究问题、上游仓库与固定 commit、核对日期、范围、关键源码链接、事实/推断/未知。图稿修改需要一并更新 `.excalidraw`、SVG、PNG 和图的文字版；生成图要同步修改对应 `build.py` 或仓库级构建脚本。不要上传私人笔记、访问令牌、整段第三方文档或未经许可的图片。

本地至少运行：

```bash
python3 scripts/check_repo.py
python3 scripts/rebuild_scenes.py
git diff --exit-code -- 'figures/**/scene.excalidraw'
```

最后两步会重建生成图源；请先检查自己的工作区改动，不要在有未保存的手工图稿编辑时执行。书稿改动还应按[构建说明](book/README.md)生成 PDF 并目视检查受影响页面。CI 是结构检查，不是源码审稿、视觉验收或许可批准。

原创文字与图采用 [CC BY 4.0](LICENSE-CONTENT.md)，脚本与工作流采用 [MIT](LICENSE-CODE)。贡献时请确认自己有权按相应许可提交材料。涉及上游项目的链接和短引文保持原始署名，不把它们重新许可为本仓库作品。
