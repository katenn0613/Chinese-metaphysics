"""Report export service."""

from __future__ import annotations

import json
import re
from pathlib import Path

from metaphysics_app.domain.models import (
    ExportFormat,
    ExportTask,
    HistoryRecord,
    HistoryRecordType,
    ReportTemplate,
)


DEFAULT_REPORT_TEMPLATE = ReportTemplate(
    id="bazi-basic-v1",
    name="八字基础报告",
    description="包含基础排盘、简要解释、详细分析和计算备注。",
    supported_formats=[ExportFormat.MARKDOWN],
)

_UNSAFE_FILENAME_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')


class ExportService:
    def export_history_record(
        self,
        record: HistoryRecord,
        output_path: Path,
        export_format: ExportFormat = ExportFormat.MARKDOWN,
        template: ReportTemplate = DEFAULT_REPORT_TEMPLATE,
    ) -> ExportTask:
        if isinstance(export_format, str):
            export_format = ExportFormat(export_format)
        if export_format not in template.supported_formats:
            raise NotImplementedError(f"{export_format.value} 导出接口尚未实现。")

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
        payload_json = json.dumps(record.payload, ensure_ascii=False, indent=2)
        tags = "、".join(record.tags) if record.tags else "无"
        sections = [
            f"# {record.title}",
            "## 摘要",
            record.subtitle,
            record.preview_text,
            "## 标签",
            tags,
        ]
        if record.record_type == HistoryRecordType.BAZI and "chart" in record.payload:
            sections.append(self._render_bazi_report(record.payload))
        if record.record_type == HistoryRecordType.ALMANAC and "candidate_dates" in record.payload:
            sections.append(self._render_almanac_report(record.payload))
        if record.record_type == HistoryRecordType.AI_SESSION and "messages" in record.payload:
            sections.append(self._render_ai_session(record.payload))
        sections.extend(
            [
                "## 结构化数据",
                f"```json\n{payload_json}\n```",
            ]
        )
        return "\n\n".join(section for section in sections if section)

    def _render_bazi_report(self, payload: dict) -> str:
        chart = payload["chart"]
        lines = [
            "## 四柱",
            "| 柱 | 天干 | 地支 | 藏干 | 五行 | 十神 |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
        for pillar in chart["pillars"]:
            lines.append(
                "| {name} | {stem} | {branch} | {hidden} | {element} | {ten_god} |".format(
                    name=pillar["name"],
                    stem=pillar["heavenly_stem"],
                    branch=pillar["earthly_branch"],
                    hidden=" ".join(pillar.get("hidden_stems", [])),
                    element=pillar.get("five_element", ""),
                    ten_god=pillar.get("ten_god", ""),
                )
            )

        lines.extend(
            [
                "",
                "## 五行分布",
                "、".join(f"{name}{score}" for name, score in chart["five_element_scores"].items()),
                "",
                self._render_interpretation("初学者解读", payload["beginner_interpretation"]),
                "",
                self._render_interpretation("专业解读", payload["professional_interpretation"]),
                "",
                "## 计算备注",
                "\n".join(f"- {note}" for note in chart.get("calculation_notes", [])),
            ]
        )
        return "\n".join(lines)

    def _render_almanac_report(self, payload: dict) -> str:
        lines = [
            "## 候选日期",
            "| 日期 | 等级 | 评分 | 原因 | 注意事项 |",
            "| --- | --- | --- | --- | --- |",
        ]
        for candidate in payload.get("candidate_dates", []):
            lines.append(
                "| {day} | {level} | {score} | {reasons} | {warnings} |".format(
                    day=candidate["day"],
                    level=candidate["level"],
                    score=candidate["score"],
                    reasons="；".join(candidate.get("reasons", [])),
                    warnings="；".join(candidate.get("warnings", [])),
                )
            )
        if not payload.get("candidate_dates"):
            lines.append("| 无 | 无 | 0 | 未筛选到候选日期 |  |")
        return "\n".join(lines)

    def _render_ai_session(self, payload: dict) -> str:
        lines = ["## 对话记录"]
        for message in payload.get("messages", []):
            role = "用户" if message.get("role") == "user" else "助手"
            lines.extend(["", f"### {role}", message.get("content", "")])
        return "\n".join(lines)

    def _render_interpretation(self, title: str, payload: dict) -> str:
        lines = [f"## {title}", payload["summary"]]
        for section in payload.get("sections", []):
            lines.extend(["", f"### {section['title']}", section["content"]])
        if payload.get("confidence_notes"):
            lines.extend(["", "### 可信度备注"])
            lines.extend(f"- {note}" for note in payload["confidence_notes"])
        return "\n".join(lines)


def safe_report_filename(title: str, suffix: str = ".md", max_length: int = 120) -> str:
    cleaned = _UNSAFE_FILENAME_CHARS.sub("_", title).strip().strip(".")
    cleaned = re.sub(r"\s+", " ", cleaned)
    cleaned = cleaned[: max(1, max_length - len(suffix))].rstrip()
    return f"{cleaned or 'report'}{suffix}"
