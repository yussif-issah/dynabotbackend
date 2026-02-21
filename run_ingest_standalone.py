import os, time, json
from pinecone import Pinecone
from services.DocumentProcessing import DocumentProcessing
from services.TextProcessing import TextProcessing
from services.VectoreStore import VectoreStore

# Load settings.json to set API keys for this process
with open('settings.json', 'r') as f:
    settings = json.load(f)
    os.environ['OPENAI_API_KEY'] = settings.get('openai_api_key', '')
    os.environ['PINECONE_API_KEY'] = settings.get('pinecone_api_key', '')

pc = Pinecone(api_key=os.environ.get('PINECONE_API_KEY'))

if __name__ == '__main__':
    file_to_ingest = 'Copyofgyanko_msc_CV.txt'
    dp = DocumentProcessing()
    tp = TextProcessing()
    vs = VectoreStore(pc, dp, tp)
    start = time.time()
    try:
        vs.create_store(file_to_ingest)
        print('Ingest completed')
    except Exception as e:
        print('Ingest failed:', e)
    finally:
        print('Elapsed:', time.time() - start)
