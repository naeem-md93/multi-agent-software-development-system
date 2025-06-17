import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

def retrieve_relevant_data(query_embedding: np.ndarray, db: dict, topk: int = 10) -> list[dict]:

    db_names = []
    db_embeddings = []
    for file_path, file_data in db.items():
        for idx, node in enumerate(file_data["entities"]):
            db_names.append((file_path, idx))
            db_embeddings.append(node["embeddings"])
    db_embeddings = np.stack(db_embeddings, 0)

    sim_scores = cosine_similarity(query_embedding, db_embeddings).squeeze(0)
    score_indexes = [(i, x) for i, x in enumerate(sim_scores)]
    score_indexes = sorted(score_indexes, key=lambda x: x[1], reverse=True)
    score_indexes = score_indexes[:topk]

    result = []
    for (idx, _) in score_indexes:
        (fp, n_idx) = db_names[idx]
        result.append(db[fp]["entities"][n_idx])

    return result
