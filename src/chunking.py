def create_chunks(documents, chunk_size=800, chunk_overlap=100):
    """
    Documents ko chhote chunks mein todta hai.
    
    Parameters:
    - documents: list of dicts (document_loader se aaya hua)
    - chunk_size: har chunk mein max characters
    - chunk_overlap: do chunks ke beech overlap
    """
    chunks = []

    for doc in documents:
        text = doc["text"]
        subject = doc["subject"]
        filename = doc["filename"]

        start = 0
        chunk_num = 1

        while start < len(text):
            end = start + chunk_size
            chunk_text = text[start:end]

            # Agar chunk bahut chhota hai toh skip (last wala)
            if len(chunk_text.strip()) < 50:
                break

            chunks.append({
                "subject": subject,
                "filename": filename,
                "chunk_number": chunk_num,
                "text": chunk_text.strip(),
                "char_count": len(chunk_text)
            })

            # Next chunk start (overlap ke saath)
            start += chunk_size - chunk_overlap
            chunk_num += 1

    return chunks


# ------------------- TEST -------------------
if __name__ == "__main__":
    from document_loader import load_documents

    data_path = r"C:\Users\Hari Shankar Kumar\OneDrive\Desktop\semester-study-assistant\data"
    
    print("Loading documents...")
    documents = load_documents(data_path)
    
    print("\nCreating chunks...")
    chunks = create_chunks(documents, chunk_size=800, chunk_overlap=100)
    
    print("\n" + "="*50)
    print(f"Total Documents : {len(documents)}")
    print(f"Total Chunks    : {len(chunks)}")
    print("="*50)
    
    # Pehle 3 chunks dikhao
    print("\n--- Sample Chunks ---\n")
    for chunk in chunks[:3]:
        print(f"Subject : {chunk['subject']}")
        print(f"File    : {chunk['filename']}")
        print(f"Chunk   : {chunk['chunk_number']}")
        print(f"Text    : {chunk['text'][:200]}...")
        print("-" * 40)