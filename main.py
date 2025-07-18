from openai import OpenAI
import os
from pinecone import Pinecone
from services.VectoreStore import VectoreStore
from services.DocumentProcessing import DocumentProcessing
from services.TextProcessing import TextProcessing
from services.AnswerQuestions import AnswerQuestions




os.environ['OPENAI_API_KEY'] = "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"
pc = Pinecone(api_key="pcsk_2Ertsy_GHUwZEidUrQGJ6zBEEwVedQW7Vu4ttE3UBZtP6ZJkWifgw6AnaDXCWhkSfsvPfS")
client = OpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get("OPENAI_API_KEY"),
)

def create_vector_store():
    vector_store = VectoreStore(pc, DocumentProcessing(), TextProcessing())
    vector_store.create_store("Copyofgyanko_msc_CV.txt")
    print("Vector store created successfully.")

def query_vector_store(query_text):
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    answerQuestions = AnswerQuestions(vector_store=VectoreStore(pc, DocumentProcessing(), TextProcessing()), client=client) 
    answerQuestions.answer_query(query_text)

if __name__ == "__main__":
    # Example usage
   query_vector_store("What is the primary industry that Gyanko has worked in?")
    

