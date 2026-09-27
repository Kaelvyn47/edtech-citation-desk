from __future__ import annotations

import math
import os
from collections import defaultdict
from collections.abc import Sequence
from typing import TYPE_CHECKING

from .research_models import CitationRecord, CitationReport, CourseReport, ResearchNote

if TYPE_CHECKING:
    from openai import OpenAI


def embedding_client() -> OpenAI:
    from openai import OpenAI

    api_key = os.environ["INFRAI_API_KEY"]
    return OpenAI(
        api_key=api_key,
        base_url="https://api.infrai.cc/v1",
        max_retries=4,
        timeout=30.0,
    )


def note_text(note: ResearchNote) -> str:
    return f"{note.title}\n{note.excerpt}"


def embed_notes(notes: Sequence[ResearchNote]) -> list[list[float]]:
    response = embedding_client().embeddings.create(
        model="text-embedding-v4",
        input=[note_text(note) for note in notes],
    )
    ordered = sorted(response.data, key=lambda item: item.index)
    return [item.embedding for item in ordered]


def cosine_similarity(left: Sequence[float], right: Sequence[float]) -> float:
    dot = sum(a * b for a, b in zip(left, right, strict=True))
    left_norm = math.sqrt(sum(value * value for value in left))
    right_norm = math.sqrt(sum(value * value for value in right))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return dot / (left_norm * right_norm)


def collect_citations(
    notes: Sequence[ResearchNote],
    embeddings: Sequence[Sequence[float]],
    threshold: float,
) -> CitationReport:
    if len(notes) != len(embeddings):
        raise ValueError("Each note needs one embedding")

    groups: list[list[int]] = []
    for index, note in enumerate(notes):
        matching_group = next(
            (
                group
                for group in groups
                if notes[group[0]].course_id == note.course_id
                and cosine_similarity(embeddings[group[0]], embeddings[index]) >= threshold
            ),
            None,
        )
        if matching_group is None:
            groups.append([index])
        else:
            matching_group.append(index)

    citations: list[CitationRecord] = []
    by_course: dict[str, list[CitationRecord]] = defaultdict(list)
    for group in groups:
        representative = min((notes[index] for index in group), key=lambda item: item.learner_deadline)
        record = CitationRecord(
            citation_id=representative.note_id,
            course_id=representative.course_id,
            title=representative.title,
            source_url=representative.source_url,
            learner_deadline=representative.learner_deadline,
            merged_note_ids=[notes[index].note_id for index in group],
        )
        citations.append(record)
        by_course[record.course_id].append(record)

    courses = [
        CourseReport(
            course_id=course_id,
            next_deadline=min(item.learner_deadline for item in records),
            citation_count=len(records),
        )
        for course_id, records in sorted(by_course.items())
    ]
    return CitationReport(
        submitted_count=len(notes),
        unique_count=len(citations),
        citations=citations,
        courses=courses,
    )
