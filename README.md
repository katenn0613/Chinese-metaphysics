# Chinese Metaphysics Desktop App

面向电脑端的中国玄学工具应用，第一版聚焦：

- 八字排盘
- 基础解读
- AI 深度分析
- 黄历择日
- 本地历史记录
- 报告导出

主技术方案：`Python + PySide6 + SQLite`。规则计算、AI 解读、数据持久化和 UI 层独立分层，后续可替换 LLM 或增加紫微斗数、六爻、梅花易数、奇门遁甲模块。

## 文档

- [PRD](docs/PRD.md)
- [技术与架构方案](docs/TECHNICAL_PLAN.md)
- [页面与信息架构](docs/IA_AND_PAGES.md)
- [数据模型](docs/DATA_MODELS.md)

## 本地运行

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[desktop,export,ai,dev]"
python -m metaphysics_app
```

如果只做规则层和数据层开发，可先不安装桌面依赖：

```bash
pip install -e ".[dev]"
python -m compileall metaphysics_app
```

## 当前状态

这是初版项目骨架。八字排盘计算接口、历法转换接口、AI 适配接口、历史记录和导出服务已经拆分；具体玄学算法在后续阶段逐步替换占位实现。
