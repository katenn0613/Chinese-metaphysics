# 技术与架构方案

## 1. 主推荐方案

主方案：`Python + PySide6/PyQt6 桌面端优先`，本项目先采用 PySide6。

理由：

- 第一版是个人电脑端工具，本地计算、本地历史、本地导出比多端传播更重要。
- 八字、择日、农历转换等规则计算更适合先用 Python 迭代和测试。
- SQLite、PDF 导出、本地文件管理、AI HTTP 调用都能在 Python 内完成。
- PySide6 能做正式桌面软件，适合侧边栏、多页工作台、表格、图表和本地设置。
- 规则计算可独立成 Python 包，未来无论换 UI 或换 LLM 都能保留。

## 2. 备选方案

备选方案：`Web 前端 + 桌面封装`，推荐 Tauri 或 Electron。

适合条件：

- 更强调复杂视觉、动画、Web 版复用和前端生态。
- 后续需要云同步、多端一致体验或团队中前端开发占主导。

代价：

- 本地规则引擎需要通过 Rust/Node/Python sidecar/API 连接，复杂度更高。
- 桌面端本地数据库、导出、文件权限和打包链路会更分散。
- 如果选 Electron，包体和资源占用明显更高。

## 3. 两种方案对比

| 维度 | Python + PySide6 | Web + 桌面封装 |
| --- | --- | --- |
| 开发成本 | 第一版更低，规则和桌面在同一语言内 | UI 快但桌面封装和本地能力成本更高 |
| UI 灵活性 | 中等，可通过 QSS/自绘/图表增强 | 高，CSS/Canvas/SVG/图表生态成熟 |
| 后续扩展 | 玄学算法扩展容易 | 多端扩展更容易 |
| AI 接入 | Python SDK/HTTP 直接接入 | 前端需经本地后端或安全代理 |
| 导出能力 | reportlab/Qt 打印/图片导出稳定 | 浏览器打印和截图方便 |
| 桌面体验 | 原生窗口、菜单、文件系统体验好 | 体验取决于封装方案 |

结论：第一版选择 PySide6，先把规则、数据、AI 和报告闭环做扎实。后续如视觉复杂度大幅提升，可保留 Python 规则引擎，另起 Web UI。

## 4. 架构分层

- `domain`：纯领域模型和枚举，不依赖 UI/数据库/AI。
- `engines`：玄学规则引擎，如八字、黄历、未来紫微/六爻/奇门。
- `interpretation`：基础解读模板和结构化解释。
- `ai`：LLM 抽象、Prompt 构建、咨询会话。
- `data`：SQLite 连接、schema、repository。
- `services`：应用用例编排，如排盘工作流、历史记录、导出。
- `ui`：PySide6 页面、主题、导航和交互状态。

## 5. AI 接入原则

- AI 不直接排盘，只读取 `BaziChart`、`InterpretationResult` 和用户问题。
- `LLMClient` 使用协议接口，默认 `NullLLMClient` 可离线运行。
- OpenAI、Claude、本地模型等作为 adapter 实现，不影响规则引擎。
- Prompt 输出应要求标注“不确定性”和“仅供研究参考”，避免绝对化判断。

## 6. 导出方案

- V1：Markdown/HTML 报告优先，PDF 使用 `reportlab` 或 Qt 打印管线。
- 图片导出：结果页关键区域可用 Qt `grab()` 保存 PNG。
- 报告模板：`ReportTemplate` 描述模板元数据，渲染由 `ExportService` 统一处理。

## 7. 可视化建议

- 五行分布：横向条形图或雷达图。
- 天干地支关系：结构化表格为主，不做炫技图。
- 大运流年：时间轴/分段列表。
- 黄历择日：日期表格 + 标签筛选 + 候选原因。

## 8. 未来模块扩展

每个玄学模块遵守同一结构：

- `engines/<module>/calculator.py`：规则计算。
- `engines/<module>/models.py`：模块专用结构。
- `interpretation/<module>_interpreter.py`：基础解释。
- `services/<module>_service.py`：用例编排。
- `ui/pages/<module>_page.py`：页面入口。

新增紫微、六爻、梅花、奇门时，不改 AI 和历史记录主架构，只增加模块类型与结构化 payload。
