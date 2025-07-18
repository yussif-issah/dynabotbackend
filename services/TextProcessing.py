from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

class TextProcessing:
    def __init__(self):
        self.text = ""

    def embed_text(self,text: str):
        # Example processing: convert text to lowercase
        return OpenAIEmbeddings().embed_query(text)

    def chunk_text(self,text : str, chunk_size: int = 1000, chunk_overlap: int = 200):
        # Count words in the text
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        return text_splitter.split_text(text)