# debug_retrieval.py

from vector_store.retriever import retrieve

results = retrieve(
    query = "Tesla revenue profit income",
    top_k = 3,
)

for i, r in enumerate(results):
    print(f"\n[{i+1}] Score  : {r['score']}")
    print(f"     Source : {r['source']}")
    print(f"     Company: {r['company']}")
    print(f"     Text   :\n{r['text']}")
    print("-" * 60)