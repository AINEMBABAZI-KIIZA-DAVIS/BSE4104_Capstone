import os
import glob
from typing import List, Dict, Any

def chunk_text(text: str, chunk_size: int = 400, overlap: int = 50) -> List[str]:
    """
    Splits text into chunks of roughly `chunk_size` words with `overlap` words.
    Using words as a proxy for tokens for minimal dependencies.
    """
    words = text.split()
    chunks = []
    
    if not words:
        return chunks
        
    i = 0
    while i < len(words):
        chunk_words = words[i:i + chunk_size]
        chunks.append(" ".join(chunk_words))
        step = max(1, chunk_size - overlap)
        i += step
            
    return chunks

def ingest_knowledge_corpus(knowledge_dir: str = "knowledge") -> List[Dict[str, Any]]:
    """Reads all .txt files from knowledge_dir and returns chunk objects."""
    txt_files = glob.glob(os.path.join(knowledge_dir, "*.txt"))
    all_chunks = []
    
    for file_path in txt_files:
        filename = os.path.basename(file_path)
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        text_chunks = chunk_text(content, chunk_size=400, overlap=50)
        
        for idx, text in enumerate(text_chunks):
            chunk_obj = {
                "content": text,
                "metadata": {
                    "source_filename": filename,
                    "chunk_index": idx,
                    "provenance": "team-created/synthetic"
                }
            }
            all_chunks.append(chunk_obj)
            
    return all_chunks

if __name__ == '__main__':
    chunks = ingest_knowledge_corpus()
    
    # Count chunks per file for sanity check
    file_chunk_counts = {}
    for chunk in chunks:
        filename = chunk["metadata"]["source_filename"]
        file_chunk_counts[filename] = file_chunk_counts.get(filename, 0) + 1
        
    print("Chunk count per file:")
    for filename, count in sorted(file_chunk_counts.items()):
        print(f"  {filename}: {count} chunks")
        
    print(f"\nTotal chunks generated: {len(chunks)}")
