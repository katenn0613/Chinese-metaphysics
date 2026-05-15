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

如需启用真实 AI 对话，设置以下环境变量后再启动应用：

```bash
export OPENAI_API_KEY="..."
export OPENAI_MODEL="..."
# 可选：OpenAI-compatible 服务地址
export OPENAI_BASE_URL="https://example.com/v1"
```

如果只做规则层和数据层开发，可先不安装桌面依赖：

```bash
pip install -e ".[dev]"
python -m compileall metaphysics_app
python -m metaphysics_app --smoke
```

## 当前状态

这是初版可运行骨架。八字排盘已经具备干支年、近似节气月、儒略日干支日、日干起时和十神基础关系；历法精确节气、农历转换、旺衰格局和大运流年仍需后续接入校验。AI 适配接口、历史记录、设置持久化、Markdown 导出和黄历择日启发式筛选已经拆分。

目前桌面端已支持：

- 八字结果保存到历史记录，并从历史记录重新打开结果页。
- AI 问命离线降级、显式环境变量启用 OpenAI-compatible adapter、AI 对话保存和重新打开。
- 黄历择日结果保存、重新打开和 Markdown 候选日期表导出。
- 用户资料本地保存、载入编辑、列表和删除。
- 八字 Markdown 报告导出，包含四柱表、五行分布、双模式解读和结构化 JSON。
