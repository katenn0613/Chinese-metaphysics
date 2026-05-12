"""Report export service."""

from __future__ import annotations

from pathlib import Path

from metaphysics_app.domain.models import ExportFormat, ExportTask, HistoryRecord, ReportTemplate


DEFAULT_REPORT_TEMPLATE = ReportTemplate(
    id="bazi-basic-v1",
    name="八字基础报告",
    description="包含基础排盘、简要解释、详细分析和计算备注。",
    supported_formats=[ExportFormat.MARKDOWN, ExportFormat.PDF, ExportFormat.PNG],
)


class ExportService:
    def export_history_record(
        self,
        record: HistoryRecord,
        output_path: Path,
        export_format: ExportFormat = ExportFormat.MARKDOWN,
        template: ReportTemplate = DEFAULT_REPORT_TEMPLATE,
    ) -> ExportTask:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        task = ExportTask(
            record_id=record.id,
            template_id=template.id,
            export_format=export_format,
            output_path=str(output_path),
            status="running",
        )

        if export_format == ExportFormat.MARKDOWN:
            output_path.write_text(self._render_markdown(record), encoding="utf-8")
            task.status = "finished"
            return task

        task.status = "blocked"
        raise NotImplementedError("PDF/PNG 导出接口已预留，后续接入 reportlab 或 Qt 截图。")

    def _render_markdown(self, record: HistoryRecord) -> str:
        return f"""# {record.title}

{record.subtitle}

{record.preview_text}

```json
{record.payload}
```
"""
