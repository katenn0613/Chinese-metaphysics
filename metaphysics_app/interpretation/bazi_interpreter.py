"""Rule-based Bazi interpretation templates."""

from __future__ import annotations

from metaphysics_app.domain.models import (
    BaziChart,
    InterpretationMode,
    InterpretationResult,
    InterpretationSection,
)


class BaziInterpreter:
    generator_version = "bazi-template-v0.1"

    def interpret(self, chart: BaziChart, mode: InterpretationMode) -> InterpretationResult:
        if mode == InterpretationMode.PROFESSIONAL:
            return self._professional(chart)
        return self._beginner(chart)

    def _professional(self, chart: BaziChart) -> InterpretationResult:
        sections = [
            InterpretationSection(
                title="四柱结构",
                content="、".join(
                    f"{pillar.name}:{pillar.label}({pillar.ten_god})" for pillar in chart.pillars
                ),
                tags=["排盘"],
            ),
            InterpretationSection(
                title="十神关系",
                content="、".join(
                    f"{pillar.name}{pillar.heavenly_stem}:{pillar.ten_god}"
                    for pillar in chart.pillars
                    if pillar.ten_god
                ),
                tags=["十神"],
            ),
            InterpretationSection(
                title="五行分布",
                content=self._score_text(chart.five_element_scores),
                tags=["五行"],
            ),
            InterpretationSection(
                title="算法状态",
                content="当前已完成干支、五行、十神的基础结构化输出；旺衰、格局和大运仍待补齐。",
                tags=["校验"],
            ),
        ]
        return InterpretationResult(
            chart_id=chart.id,
            mode=InterpretationMode.PROFESSIONAL,
            summary=f"日主为 {chart.day_master}，五行分布为 {self._score_text(chart.five_element_scores)}。",
            sections=sections,
            generator_version=self.generator_version,
            follow_up_questions=["是否需要分析日主强弱？", "是否需要加入大运流年？"],
            confidence_notes=["月柱仍使用近似节气边界，当前解释不替代正式命理校验。"],
        )

    def _beginner(self, chart: BaziChart) -> InterpretationResult:
        strongest = max(chart.five_element_scores, key=chart.five_element_scores.get)
        sections = [
            InterpretationSection(
                title="你看到的盘是什么",
                content="八字盘把出生时间拆成四组符号，分别对应年、月、日、时。",
                tags=["入门"],
            ),
            InterpretationSection(
                title="五行直观理解",
                content=f"当前骨架计算中，{strongest} 的数量相对更突出。正式版本会进一步解释平衡关系。",
                tags=["五行"],
            ),
            InterpretationSection(
                title="十神关系",
                content="、".join(
                    f"{pillar.name}的天干是{pillar.heavenly_stem}，对应{pillar.ten_god}"
                    for pillar in chart.pillars
                    if pillar.ten_god
                ),
                tags=["十神"],
            ),
            InterpretationSection(
                title="下一步可以问 AI",
                content="你可以围绕性格倾向、阶段选择、学习方向等提出具体问题。",
                tags=["AI"],
            ),
        ]
        return InterpretationResult(
            chart_id=chart.id,
            mode=InterpretationMode.BEGINNER,
            summary=f"这个盘的日主是 {chart.day_master}。先把它理解为整个分析的观察中心。",
            sections=sections,
            generator_version=self.generator_version,
            follow_up_questions=["我适合从哪个角度理解这个盘？", "这个盘的五行分布怎么读？"],
            confidence_notes=["当前为基础规则说明，不能作为正式命理结论。"],
        )

    def _score_text(self, scores: dict[str, int]) -> str:
        return "，".join(f"{name}{score}" for name, score in scores.items())
