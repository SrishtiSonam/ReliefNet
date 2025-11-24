from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

class RagExplainer:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.documents = [
            "The allocation logic prioritizes districts with high vulnerability scores.",
            "UAVs are used for light loads and hard-to-reach areas.",
            "Trucks handle bulk inventory but are restricted by road damage.",
            "Approximate Dynamic Programming (ADP) is used to balance immediate needs vs future uncertainty.",
            "Fairness is ensured by penalizing long-term deprivation in any single district."
        ]
        self.index = None
        self._build_index()

    def _build_index(self):
        embeddings = self.model.encode(self.documents)
        d = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(d)
        self.index.add(embeddings)

    def query(self, question, k=2):
        q_emb = self.model.encode([question])
        D, I = self.index.search(q_emb, k)
        results = [self.documents[i] for i in I[0]]
        return results

if __name__ == "__main__":
    rag = RagExplainer()
    print(rag.query("How are drones used?"))
