from langchain.vectorstores import Pinecone
from pinecone import Pinecone,ServerlessSpec
from services.DocumentProcessing import DocumentProcessing 
from services.TextProcessing import TextProcessing 
class VectoreStore:
    def __init__(self, pc : Pinecone,document_processor: DocumentProcessing, text_processor: TextProcessing):
        self.pc = pc
        self.document_processor = document_processor
        self.text_processor = text_processor
    
    def create_store(self, document):
       # Load the document
        self.document_processor.read_document(document)
        # Chunk the text
        chunks = self.text_processor.chunk_text(self.document_processor.text)

        # Create embeddings for each chunk
        vectors = []
        for i, chunk in enumerate(chunks):
            embedding = self.text_processor.embed_text(chunk)
            if not isinstance(embedding, list) or not all(isinstance(v, float) for v in embedding):
                print(f"Skipping chunk {i}: invalid embedding format")
                continue
            vector = {
                "id": f"gyanko_{i}",
                "values": embedding,
                "metadata": {
                    "user_id": "gyanko_user_id",
                    "file_name": "cv",
                    'chunk': chunk,
                }
            }
            vectors.append(vector)

        # Create index if not exists
        index_name = "gyankofirstdraft"
        if not self.pc.has_index(index_name):
            self.pc.create_index(
            name=index_name,
            vector_type="dense",
            dimension=1536,
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws",
                region="us-east-1"
            ),
            deletion_protection="disabled",
            tags={
                "environment": "development"
            }
        )

        # Connect to the index
        index = self.pc.Index(index_name)

        # Upsert vectors
        index.upsert(vectors=vectors, namespace="gyankoSpace")

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