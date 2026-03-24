# agents/retrieval_agent.py

from typing import Dict, Any, Optional
from agents.base_agent import BaseAgent
from vector_store.retriever import retrieve
from memory.short_term import ShortTermMemory


class RetrievalAgent(BaseAgent):
    """
    Retrieves relevant financial chunks from Qdrant
    using semantic search + metadata filtering.
    """

    def __init__(self, memory: Optional[ShortTermMemory] = None):
        super().__init__(name="RetrievalAgent", memory=memory)


    def run(self, query: str, context: Dict[str, Any] = {}) -> Dict[str, Any]:
        """
        context keys (all optional):
            company, year, section, doc_type, top_k
        """
        try:
            company  = context.get("company")  or self.get_context("company")
            year     = context.get("year")     or self.get_context("year")
            section  = context.get("section")
            doc_type = context.get("doc_type")
            top_k    = context.get("top_k", 5)

            print(f"[{self.name}] Searching: '{query}' | company={company} year={year}")

            chunks = retrieve(
                query   = query,
                top_k   = top_k,
                company = company,
                year    = year,
                section = section,
                doc_type= doc_type,
            )

            if not chunks:
                return self.failure("No relevant chunks found in vector store.")

            # store context for other agents
            if company:
                self.set_context("company", company)
            if year:
                self.set_context("year", year)

            # build combined context text
            context_text = "\n\n".join(
                f"[{i+1}] (score={c['score']}) {c['text']}"
                for i, c in enumerate(chunks)
            )

            self.remember("user",      query)
            self.remember("assistant", f"Retrieved {len(chunks)} chunks.")

            return self.success({
                "query"       : query,
                "chunks"      : chunks,
                "context_text": context_text,
                "total"       : len(chunks),
            })

        except Exception as e:
            return self.failure(str(e))


# --- Quick test ---
if __name__ == "__main__":
    agent = RetrievalAgent()

    response = agent.run(
        query   = "What is Tesla revenue in 2024?",
        context = {"company": "Tesla", "year": "2024", "top_k": 3}
    )

    print(f"Status : {response['status']}")
    print(f"Total  : {response['result']['total']} chunks")
    print(f"\nContext text preview:")
    print(response['result']['context_text'][:400])