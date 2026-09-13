from bloom_arc.models import LearningRequest, LearningRun, LessonPlan, RunStatus
from bloom_arc.planner import StructuredBloomPlanner


class FakeStructuredModel:
    def __init__(self) -> None:
        self.prompts: list[str] = []

    def invoke(self, prompt: str) -> LessonPlan:
        self.prompts.append(prompt)
        return LessonPlan(
            title="RAG — retrieval experiment",
            outcome="Inspect retrieval quality",
            mastery_items=["Run five queries", "Explain one failure"],
            lesson_markdown="# Task\n\nRun five queries.",
            duration_minutes=35,
        )


def request() -> LearningRequest:
    return LearningRequest(
        user_id="discord:42",
        topic="RAG",
        goal="build a demo",
        availability="Tuesday evening",
        timezone="Asia/Kolkata",
    )


def test_first_lesson_prompt_preserves_bloom_one_lesson_rule() -> None:
    model = FakeStructuredModel()
    planner = StructuredBloomPlanner(model)

    planner.create_first_lesson(request())

    prompt = model.prompts[0].lower()
    assert "exactly one" in prompt
    assert "measurable" in prompt
    assert "rag" in prompt


def test_next_lesson_prompt_includes_learner_evidence() -> None:
    model = FakeStructuredModel()
    planner = StructuredBloomPlanner(model)
    plan = planner.create_first_lesson(request())
    run = LearningRun(
        run_id="run-1",
        idempotency_key="key-1",
        request=request(),
        plan=plan,
        status=RunStatus.SCHEDULED,
    )

    planner.create_next_lesson(run, "The retrieved chunks were too broad")

    prompt = model.prompts[-1]
    assert "The retrieved chunks were too broad" in prompt
    assert "Do not repeat" in prompt
