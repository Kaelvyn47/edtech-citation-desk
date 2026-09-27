from citation_desk.citation_collector import collect_citations
from citation_desk.research_models import ResearchNote


def make_note(note_id: str, course_id: str, deadline: str) -> ResearchNote:
    return ResearchNote.model_validate(
        {
            "note_id": note_id,
            "course_id": course_id,
            "title": f"Source {note_id}",
            "source_url": f"https://example.edu/{note_id}",
            "excerpt": "Evidence about retrieval practice.",
            "learner_deadline": deadline,
        }
    )


def test_dedupes_within_course_and_keeps_earliest_deadline() -> None:
    notes = [
        make_note("late-copy", "EDU-204", "2026-10-20"),
        make_note("early-copy", "EDU-204", "2026-10-12"),
        make_note("other-course", "EDU-310", "2026-10-08"),
    ]
    embeddings = [[1.0, 0.0], [0.99, 0.01], [1.0, 0.0]]

    report = collect_citations(notes, embeddings, threshold=0.95)

    assert report.submitted_count == 3
    assert report.unique_count == 2
    assert report.citations[0].citation_id == "early-copy"
    assert report.citations[0].merged_note_ids == ["late-copy", "early-copy"]
    assert {course.course_id: course.citation_count for course in report.courses} == {
        "EDU-204": 1,
        "EDU-310": 1,
    }

