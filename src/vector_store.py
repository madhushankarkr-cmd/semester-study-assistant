import faiss
import numpy as np
import pickle
import os

def create_faiss_index(embeddings):
    """
    Embeddings se FAISS index banata hai.
    """
    dimension = embeddings.shape[1]  # 384
    index = faiss.IndexFlatL2(dimension)  # L2 distance use karenge
    
    # Embeddings add karo
    index.add(embeddings.astype('float32'))
    
    print(f"✅ FAISS index created")
    print(f"Total vectors in index: {index.ntotal}")
    return index


def save_faiss_index(index, save_folder="processed_data"):
    """
    FAISS index ko save karta hai.
    """
    os.makedirs(save_folder, exist_ok=True)
    faiss.write_index(index, f"{save_folder}/faiss_index.index")
    print(f"✅ FAISS index saved in '{save_folder}'")


def load_faiss_index(save_folder="processed_data"):
    """
    Saved FAISS index ko load karta hai.
    """
    index = faiss.read_index(f"{save_folder}/faiss_index.index")
    return index


def search_similar_chunks(query, model, index, chunks, top_k=4):
    """
    User ke sawal se sabse similar chunks nikaalta hai.
    """
    # Sawal ka embedding banao
    query_embedding = model.encode([query])
    
    # FAISS se similar vectors dhoondho
    distances, indices = index.search(query_embedding.astype('float32'), top_k)
    
    results = []
    for i, idx in enumerate(indices[0]):
        results.append({
            "chunk": chunks[idx],
            "distance": float(distances[0][i])
        })
    
    return results


# ------------------- TEST -------------------
if __name__ == "__main__":
    from sentence_transformers import SentenceTransformer

    print("Loading saved data...")
    embeddings = np.load("processed_data/embeddings.npy")
    
    with open("processed_data/chunks.pkl", "rb") as f:
        chunks = pickle.load(f)

    print(f"Loaded {len(chunks)} chunks")
    print(f"Embeddings shape: {embeddings.shape}")

    print("\nCreating FAISS index...")
    index = create_faiss_index(embeddings)
    save_faiss_index(index)

    print("\nLoading embedding model...")
    model = SentenceTransformer("all-MiniLM-L6-v2")

    # Test search
    query = "What is CSMA/CD?"
    print(f"\n🔍 Query: {query}")
    print("-" * 50)

    results = search_similar_chunks(query, model, index, chunks, top_k=3)

    for i, res in enumerate(results):
        chunk = res["chunk"]
        print(f"\nResult {i+1}:")
        print(f"Subject  : {chunk['subject']}")
        print(f"File     : {chunk['filename']}")
        print(f"Distance : {res['distance']:.4f}")
        print(f"Text     : {chunk['text'][:250]}...")
        print("-" * 40)