import time, json, os
from services.DocumentProcessing import DocumentProcessing
from services.TextProcessing import TextProcessing

# ensure OPENAI key available
with open('settings.json','r') as f:
    settings = json.load(f)
    os.environ['OPENAI_API_KEY'] = settings.get('openai_api_key','')

if __name__ == '__main__':
    dp = DocumentProcessing()
    tp = TextProcessing()
    file_to_ingest = 'Copyofgyanko_msc_CV.txt'
    dp.read_document(file_to_ingest)
    chunks = tp.chunk_text(dp.text)
    print(f'Chunks: {len(chunks)}')
    start = time.time()
    try:
        embeddings = tp.embed_texts(chunks)
        print('Got', len(embeddings), 'embeddings')
    except Exception as e:
        print('Embedding failed:', e)
        embeddings = []
    elapsed = time.time() - start
    print('Embedding elapsed:', elapsed)
