from sentence_transformers import SentenceTransformer
import numpy as np
import pickle
import os

def create_embeddings(chunks, model_name="all-MiniLM-L6-v2"):
    """
    Har chunk ka embedding banata hai.
    """
    print(f"Loading embedding model: {model_name} ...")
    model = SentenceTransformer(model_name)

    texts = [chunk["text"] for chunk in chunks]
    
    print(f"Creating embeddings for {len(texts)} chunks...")
    embeddings = model.encode(texts, show_progress_bar=True)

    print(f"Embeddings shape: {embeddings.shape}")
    return embeddings, model


def save_data(chunks, embeddings, save_folder="processed_data"):
    """
    Chunks aur embeddings ko save karta hai.
    """
    os.makedirs(save_folder, exist_ok=True)

    with open(f"{save_folder}/chunks.pkl", "wb") as f:
        pickle.dump(chunks, f)

    np.save(f"{save_folder}/embeddings.npy", embeddings)

    print(f"\n✅ Saved successfully in '{save_folder}' folder")


# ------------------- TEST -------------------
if __name__ == "__main__":
    from document_loader import load_documents
    from chunking import create_chunks

    data_path = r"C:\Users\Hari Shankar Kumar\OneDrive\Desktop\semester-study-assistant\data"

    print("Step 1: Loading documents...")
    documents = load_documents(data_path)

    print("\nStep 2: Creating chunks...")
    chunks = create_chunks(documents)

    print("\nStep 3: Creating embeddings...")
    embeddings, model = create_embeddings(chunks)

    print("\nStep 4: Saving data...")
    save_data(chunks, embeddings)

    print("\n" + "="*50)
    print(f"Total Chunks     : {len(chunks)}")
    print(f"Embedding Shape  : {embeddings.shape}")
    print("="*50)