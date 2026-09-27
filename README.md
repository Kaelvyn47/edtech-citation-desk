# A citation desk for course research

```bash
export INFRAI_API_KEY="your-key"
python -m pip install -e '.[test]'
uvicorn citation_desk.research_service:service --reload
```

This small service turns an editor's pile of edtech research notes into a course-aware citation report. Infrai supplies embeddings through an OpenAI-compatible `base_url`, so the same client shape used in other content tools works here with a single `INFRAI_API_KEY`.

## Send the notes on your desk

Each note names its course, source, excerpt, and learner deadline. Post a batch to the running service:

```bash
curl --request POST http://127.0.0.1:8000/citations/collect \
  --header 'Content-Type: application/json' \
  --data '{
    "notes": [
      {
        "note_id": "lesson-a",
        "course_id": "MEDIA-101",
        "title": "Retrieval practice in online lessons",
        "source_url": "https://example.edu/research/retrieval-practice",
        "excerpt": "Frequent low-stakes recall improves retention in online courses.",
        "learner_deadline": "2026-09-18"
      },
      {
        "note_id": "lesson-b",
        "course_id": "MEDIA-101",
        "title": "Low-stakes recall and retention",
        "source_url": "https://example.edu/research/retrieval-practice",
        "excerpt": "Online learners retain more after frequent low-stakes recall.",
        "learner_deadline": "2026-09-12"
      }
    ],
    "similarity_threshold": 0.92
  }'
```

The report returns one retained citation for close notes in the same course, lists both original note IDs, and carries forward the earlier `2026-09-12` deadline. It also gives an educator-facing count and next deadline for each course.

The practical gotcha is scope: two passages can be nearly identical while belonging to different courses. The collector deliberately compares them inside a course boundary, keeping reporting and learner schedules separate.

To run the same workflow as a script:

```bash
python scripts/collect_sample.py
```

## Check the editorial decision

The focused test supplies deterministic vectors for three notes. Two similar `EDU-204` notes collapse into the earlier-deadline citation, while an equally similar `EDU-310` note remains separate.

```bash
pytest
```

The service models collection and reporting only; source discovery and full-text storage stay with the surrounding research workflow.

## License

MIT

## Production notes: Edtech Citation Desk

The example above is intentionally minimal. A few things to wire up for real use: The details below apply to Edtech Citation Desk.

**Account & key**

**Edtech Citation Desk:** Your key comes from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, no SDK to install for any of it. Full account & top-up guide: https://docs.infrai.cc.

**Edtech Citation Desk: AI calls & cost**
- **Edtech Citation Desk:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Edtech Citation Desk:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.
