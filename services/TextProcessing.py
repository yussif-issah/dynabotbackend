from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List


class TextProcessing:
    def __init__(self):
        self.text = ""
        # reuse the embeddings client to avoid repeated instantiation
        self._emb_client = OpenAIEmbeddings()

    def embed_text(self, text: str):
        # single item embedding (kept for compatibility)
        return self._emb_client.embed_query(text)

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Embed a list of texts in a single/batched call via the embeddings client.
        Returns a list of embedding vectors (lists of floats) in the same order.
        """
        if not texts:
            return []
        return self._emb_client.embed_documents(texts)

    def chunk_text(self, text: str, chunk_size: int = 1000, chunk_overlap: int = 200):
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        return text_splitter.split_text(text)