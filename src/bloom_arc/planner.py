from __future__ import annotations

from typing import Protocol

from .models import LearningRequest, LearningRun, LessonPlan


class StructuredModel(Protocol):
    def invoke(self, prompt: str) -> LessonPlan: ...


class StructuredBloomPlanner:
    """Uses an LLM only for lesson judgment; app writes remain deterministic."""

    def __init__(self, model: StructuredModel) -> None:
        self.model = model

    def create_first_lesson(self, request: LearningRequest) -> LessonPlan:
        return self.model.invoke(
            f"""You are the English adaptation of the Bloom Tutor skill.
Create exactly one first lesson for this learner. Do not generate later lessons.
Use 3-5 measurable mastery items, not vague verbs such as understand or know.
The task must produce a small observable artifact and fit 15-45 minutes.

Topic: {request.topic}
Goal: {request.goal}
Availability: {request.availability}
Timezone: {request.timezone}

Return the required LessonPlan fields. Keep lesson_markdown concise and include:
1. a concrete task,
2. success criteria,
3. two reflection questions.
"""
        )

    def create_next_lesson(self, run: LearningRun, reflection: str) -> LessonPlan:
        return self.model.invoke(
            f"""You are the English adaptation of the Bloom Tutor skill.
Create exactly one adaptive next lesson. Do not repeat the prior task and do not
claim mastery. Use the learner's evidence to choose one controlled next step.
Keep it achievable in 15-45 minutes.

Topic: {run.request.topic}
Goal: {run.request.goal}
Prior lesson: {run.plan.lesson_markdown}
Learner evidence: {reflection}
Current lesson number: {run.current_lesson}

Return the required LessonPlan fields. Include a measurable task, success criteria,
and two reflection questions.
"""
        )


def create_openai_planner(model_name: str) -> StructuredBloomPlanner:
    """Create the optional LangChain/OpenAI structured planner in live mode."""
    from langchain_openai import ChatOpenAI

    model = ChatOpenAI(model=model_name, temperature=0).with_structured_output(LessonPlan)
    return StructuredBloomPlanner(model)
