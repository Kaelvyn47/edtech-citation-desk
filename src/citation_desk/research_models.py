from datetime import date
from dataclasses import MISSING, dataclass

try:
    from pydantic import BaseModel, Field, HttpUrl
    model_record = lambda cls: cls
except ModuleNotFoundError:
    def Field(*, default=MISSING, **_: object):
        return default

    HttpUrl = str

    @dataclass
    class BaseModel:
        @classmethod
        def model_validate(cls, values: dict[str, object]):
            converted = dict(values)
            if "learner_deadline" in converted and isinstance(converted["learner_deadline"], str):
                converted["learner_deadline"] = date.fromisoformat(converted["learner_deadline"])
            return cls(**converted)

    model_record = dataclass


@model_record
class ResearchNote(BaseModel):
    note_id: str = Field(min_length=1)
    course_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    source_url: HttpUrl
    excerpt: str = Field(min_length=1)
    learner_deadline: date


@model_record
class CitationBatch(BaseModel):
    notes: list[ResearchNote] = Field(min_length=1, max_length=100)
    similarity_threshold: float = Field(default=0.92, ge=0.0, le=1.0)


@model_record
class CitationRecord(BaseModel):
    citation_id: str
    course_id: str
    title: str
    source_url: HttpUrl
    learner_deadline: date
    merged_note_ids: list[str]


@model_record
class CourseReport(BaseModel):
    course_id: str
    next_deadline: date
    citation_count: int


@model_record
class CitationReport(BaseModel):
    submitted_count: int
    unique_count: int
    citations: list[CitationRecord]
    courses: list[CourseReport]
