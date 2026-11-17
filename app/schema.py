from typing import Literal
from pydantic import BaseModel, Field

GRADES = [f"Grade {i}" for i in range(5, 13)]
LANGUAGES = ["English", "German", "Swedish", "Spanish", "French"]


class CoachRequest(BaseModel):
    topic: str = Field(min_length=2, max_length=80)
    grade: Literal[tuple(GRADES)] = "Grade 8"           # type: ignore[valid-type]
    language: Literal[tuple(LANGUAGES)] = "English"      # type: ignore[valid-type]


class WorkedExample(BaseModel):
    problem: str
    steps: list[str] = Field(min_length=2)
    answer: str


class Misconception(BaseModel):
    mistake: str
    why_students_think_it: str
    how_to_respond: str


class Differentiation(BaseModel):
    simpler: str
    extension: str


class LessonCard(BaseModel):
    core_idea: str
    why_it_works: str
    worked_example: WorkedExample
    misconceptions: list[Misconception] = Field(min_length=2, max_length=4)
    lesson_ideas: list[str] = Field(min_length=2, max_length=4)
    differentiation: Differentiation
    activity: str


class CoachResponse(BaseModel):
    card: LessonCard
    source: Literal["vetted_lesson", "ai_only"]   # shown to the teacher: honesty about grounding
    source_title: str | None = None
    cached: bool = False
