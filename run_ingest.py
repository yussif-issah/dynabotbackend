import time
from main import create_vector_store

if __name__ == '__main__':
    start = time.time()
    try:
        create_vector_store()
    except Exception as e:
        print('Ingest failed:', e)
    finally:
        print('Elapsed:', time.time() - start)
