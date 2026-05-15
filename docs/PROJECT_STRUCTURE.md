# 项目目录结构

```text
Metaphysics/
  README.md
  pyproject.toml
  docs/
    PRD.md
    TECHNICAL_PLAN.md
    IA_AND_PAGES.md
    DATA_MODELS.md
    PROJECT_STRUCTURE.md
    ROADMAP.md
  metaphysics_app/
    main.py
    config.py
    domain/
      models.py
    engines/
      bazi/
        calendar.py
        calculator.py
        constants.py
      almanac/
        selector.py
    interpretation/
      bazi_interpreter.py
    ai/
      client.py
      prompts.py
      service.py
    data/
      database.py
      repositories.py
      schema.py
    services/
      bazi_service.py
      export_service.py
    ui/
      app.py
      main_window.py
      theme.py
      components.py
      pages/
        home_page.py
        bazi_input_page.py
        result_page.py
        ai_page.py
        almanac_page.py
        history_page.py
        profile_page.py
        settings_page.py
  tests/
    test_bazi_workflow.py
    test_almanac_selector.py
    test_ai_service.py
    test_main.py
    test_persistence_and_export.py
```

## 模块职责

- `domain`: 跨层共享的数据模型和枚举，只表达业务结构。
- `engines`: 纯规则计算，禁止依赖 UI 和 AI。
- `interpretation`: 基于规则结果做模板化基础解读。
- `ai`: LLM 客户端、Prompt 和咨询会话，禁止承担排盘计算。
- `data`: SQLite 本地持久化。
- `services`: 应用用例编排，例如生成排盘、保存历史、导出报告。
- `ui`: PySide6 桌面页面和交互。
- `tests`: 规则层、服务层、持久化、导出和 CLI smoke 覆盖。

## 扩展方式

新增玄学模块时按以下结构增加：

```text
engines/ziwei/
interpretation/ziwei_interpreter.py
services/ziwei_service.py
ui/pages/ziwei_page.py
```

历史记录通过 `HistoryRecord.record_type + payload` 存储模块结果，避免每个模块都重写持久化管线。

## 验证入口

```bash
python -m pytest -q
python -m ruff check metaphysics_app tests
python -m ruff format --check metaphysics_app tests
python -m metaphysics_app --smoke
```
