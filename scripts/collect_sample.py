import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from citation_desk.citation_collector import collect_citations, embed_notes
from citation_desk.research_models import CitationBatch


def main() -> None:
    batch = CitationBatch.model_validate(
        {
            "notes": [
                {
                    "note_id": "media-101-a",
                    "course_id": "MEDIA-101",
                    "title": "Retrieval practice in online lessons",
                    "source_url": "https://example.edu/research/retrieval-practice",
                    "excerpt": "Frequent low-stakes recall improves retention in online courses.",
                    "learner_deadline": "2026-09-18",
                },
                {
                    "note_id": "media-101-b",
                    "course_id": "MEDIA-101",
                    "title": "Low-stakes recall and retention",
                    "source_url": "https://example.edu/research/retrieval-practice",
                    "excerpt": "Online learners retain more after frequent low-stakes recall.",
                    "learner_deadline": "2026-09-12",
                },
            ],
            "similarity_threshold": 0.92,
        }
    )
    report = collect_citations(batch.notes, embed_notes(batch.notes), batch.similarity_threshold)
    print(json.dumps(report.model_dump(mode="json"), indent=2))


if __name__ == "__main__":
    main()
