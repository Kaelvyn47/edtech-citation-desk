from fastapi import FastAPI

from .citation_collector import collect_citations, embed_notes
from .research_models import CitationBatch, CitationReport

service = FastAPI(title="Edtech Citation Desk")


@service.post("/citations/collect", response_model=CitationReport)
def collect(batch: CitationBatch) -> CitationReport:
    embeddings = embed_notes(batch.notes)
    return collect_citations(batch.notes, embeddings, batch.similarity_threshold)

