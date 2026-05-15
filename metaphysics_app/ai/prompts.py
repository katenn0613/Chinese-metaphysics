"""Prompt builders for AI consultation."""

from __future__ import annotations

from metaphysics_app.domain.models import BaziChart, InterpretationResult


SYSTEM_PROMPT = """
你是一个面向个人研究的中国玄学解释助手。
你不能重新排盘，不能声称自己完成了规则计算。
你只能基于传入的结构化排盘、基础解释和用户问题做自然语言说明。
表达应克制、专业、避免绝对化判断，并提示内容仅供研究参考。
""".strip()


def build_bazi_context(chart: BaziChart, interpretation: InterpretationResult | None) -> str:
    pillars = " / ".join(
        f"{pillar.name}:{pillar.label}({pillar.ten_god})" for pillar in chart.pillars
    )
    sections = ""
    if interpretation:
        sections = "\n".join(
            f"- {section.title}: {section.content}" for section in interpretation.sections
        )

    return f"""
排盘ID: {chart.id}
算法版本: {chart.algorithm_version}
出生时间修正后: {chart.normalized_birth_datetime}
四柱: {pillars}
日主: {chart.day_master}
五行分布: {chart.five_element_scores}
计算备注: {"; ".join(chart.calculation_notes)}
基础解释:
{sections}
""".strip()
