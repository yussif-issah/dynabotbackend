from langchain.vectorstores import Pinecone
from pinecone import Pinecone, ServerlessSpec
from services.DocumentProcessing import DocumentProcessing
from services.TextProcessing import TextProcessing
from typing import List


class VectoreStore:
    def __init__(self, pc: Pinecone, document_processor: DocumentProcessing, text_processor: TextProcessing):
        self.pc = pc
        self.document_processor = document_processor
        self.text_processor = text_processor

    def create_store(self, document, index_name: str = "gyankofirstdraft", namespace: str = "gyankoSpace", upsert_batch: int = 200):
        # Load the document
        self.document_processor.read_document(document)
        # Chunk the text
        chunks = self.text_processor.chunk_text(self.document_processor.text)

        if not chunks:
            print("No chunks produced from document, skipping.")
            return

        # Create embeddings for all chunks in a single/batched call
        embeddings = self.text_processor.embed_texts(chunks)

        vectors: List[dict] = []
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            # Normalize embedding type into list[float]
            try:
                if hasattr(embedding, 'tolist'):
                    emb_list = embedding.tolist()
                else:
                    emb_list = list(map(float, embedding))
            except Exception:
                print(f"Skipping chunk {i}: invalid embedding format")
                continue

            vector = {
                "id": f"gyanko_{i}",
                "values": emb_list,
                "metadata": {
                    "user_id": "gyanko_user_id",
                    "file_name": document,
                    "chunk": chunk,
                }
            }
            vectors.append(vector)

        # Create index if not exists, robust to Pinecone client version
        if not self.pc.has_index(index_name):
            dimension = len(vectors[0]["values"]) if vectors else 1536
            try:
                print("Trying Pinecone index creation with full ServerlessSpec signature...")
                self.pc.create_index(
                    name=index_name,
                    dimension=dimension,
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region="us-east-1"
                    ),
                    deletion_protection="disabled",
                )
                print("Index created with full signature.")
            except Exception as e1:
                print(f"Full signature failed: {e1}\nTrying minimal signature...")
                try:
                    self.pc.create_index(name=index_name, dimension=dimension, metric="cosine")
                    print("Index created with minimal signature.")
                except Exception as e2:
                    print(f"Failed to create index with minimal signature: {e2}")
                    raise RuntimeError(f"Could not create Pinecone index '{index_name}'. Please create it manually in the Pinecone console.")

        # Connect to the index
        index = self.pc.Index(index_name)

        # Upsert vectors in batches to avoid payload/timeout issues
        for i in range(0, len(vectors), upsert_batch):
            batch = vectors[i:i + upsert_batch]
            index.upsert(vectors=batch, namespace=namespace)

    def query(self, query_text):
        """
        Query the vector store with a text query.
        """
        return self.vector_store.query(query_text)

    def delete_document(self, document_id):
        """
        Delete a document from the vector store by its ID.
        """
        self.vector_store.delete_document(document_id)