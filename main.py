from openai import OpenAI
import os
from pinecone import Pinecone
from services.VectoreStore import VectoreStore
from services.DocumentProcessing import DocumentProcessing
from services.TextProcessing import TextProcessing
from services.AnswerQuestions import AnswerQuestions
import json



with open('settings.json', 'r') as f:
    settings = json.load(f)
    os.environ['OPENAI_API_KEY'] = settings.get("openai_api_key", "")
    os.environ['PINECONE_API_KEY'] = settings.get("pinecone_api_key", "")

pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))
client = OpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get("OPENAI_API_KEY"),
)

def create_vector_store():
    vector_store = VectoreStore(pc, DocumentProcessing(), TextProcessing())
    vector_store.create_store("Copyofgyanko_msc_CV.txt")
    print("Vector store created successfully.")

def query_vector_store(query_text):
    answerQuestions = AnswerQuestions(vector_store=VectoreStore(pc, DocumentProcessing(), TextProcessing()), client=client) 
    answerQuestions.answer_query(query_text)

if __name__ == "__main__":
    # Example usage
   query_vector_store("What is the primary industry that Gyanko has worked in?")
    

