# Chat bot API endpoint for /chat_api/{user_id}
from fastapi import File, Request,Form
from openai import OpenAI
import os
from pinecone import Pinecone
from services.VectoreStore import VectoreStore
from services.DocumentProcessing import DocumentProcessing
from services.TextProcessing import TextProcessing
from services.AnswerQuestions import AnswerQuestions
import json
from typing import List
from typing import Union
from fastapi import FastAPI,UploadFile, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from database.database import engine, get_db
from models import models,schema
from auth import auth
from fastapi.responses import HTMLResponse

try:
    models.Base.metadata.create_all(bind=engine)
except Exception as e:
    # If the database isn't available at import time (e.g., missing/incorrect
    # DATABASE_URL), don't crash the app — log and continue so the frontend can
    # still be served. Endpoints that require the DB will fail until connection
    # is fixed.
    print(f"Warning: could not initialize database tables: {e}")

with open('settings.json', 'r') as f:
    settings = json.load(f)
    os.environ['OPENAI_API_KEY'] = settings.get("openai_api_key", "")
    os.environ['PINECONE_API_KEY'] = settings.get("pinecone_api_key", "")

pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))
client = OpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get("OPENAI_API_KEY"),
)

app = FastAPI()


# Serve static files from the `frontend` folder at /static
app.mount("/static", StaticFiles(directory="frontend", html=True), name="static")



@app.post("/chat_api/{user_id}")
async def chat_api(user_id: str, request: Request):
    data = await request.json()
    message = data.get("message")
    if not message:
        return {"reply": "No message provided."}
    # Use AnswerQuestions to generate a reply
    answerQuestions = AnswerQuestions(vector_store=VectoreStore(pc, DocumentProcessing(), TextProcessing()), client=client)
    reply = answerQuestions.answer_query(message,user_id=user_id)
    return {"reply": reply}


# Serve chat page for /chat/{user_id} using chat.html
@app.get("/chat/{user_id}", response_class=HTMLResponse)
async def chat_page(user_id: str):
    print(f"Serving chat page for user_id: {user_id}")
    with open("frontend/chat.html", "r", encoding="utf-8") as f:
        html = f.read()
    # Inject user_id as a JS variable
    inject_script = f'<script>window.CHAT_USER_ID = "{user_id}";</script>'
    safe_user_id = json.dumps(user_id)
    html = html.replace("__USER_ID__", safe_user_id)
    return HTMLResponse(content=html)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.post("/upload")
async def upload_files(files: List[UploadFile] = File(...),token: str = Form(None)):

    if not files:
        return {"message": "No files uploaded."}

    vector_store = VectoreStore(pc, DocumentProcessing(), TextProcessing())

    processed_files = []

    for file in files:
        try:
            # Read file directly from memory
            contents = await file.read()

            if not contents:
                continue

            # Decode safely (assuming text files)
            try:
                text_content = contents.decode("utf-8")
            except UnicodeDecodeError:
                text_content = contents.decode("latin-1", errors="ignore")

            # Send to vector store
            user_name = await get_current_user(token=token, db=Depends(get_db))
            vector_store.create_store(text_content,index_name=user_name.lower(),namespace=user_name.lower())

            processed_files.append(file.filename)

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error processing {file.filename}: {str(e)}"
            )

    return {
        "message": f"{len(processed_files)} file(s) processed successfully.",
        "files": processed_files
    }

@app.get("/test")
async def test_endpoint():
    return {"message": "Test endpoint is working!"}



@app.post("/register", response_model=schema.User)
def register_user(user: schema.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = auth.get_password_hash(user.password)
    new_user = models.User(username=user.username, email=user.email, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/token", response_model=schema.Token)
def login_for_access_token(form_data: schema.Login, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.email).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(data={"sub": user.username})
    print(f"Generated token for {user.username}: {access_token}")
    return {"access_token": access_token, "token_type": "bearer", "username": user.username}

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    username = auth.verify_token(token)
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return username

@app.get("/users/me", response_model=schema.User)
async def read_users_me(current_user: models.User = Depends(get_current_user)):
    return current_user

def create_vector_store():
    vector_store = VectoreStore(pc, DocumentProcessing(), TextProcessing())
    vector_store.create_store("Copyofgyanko_msc_CV.txt")
    print("Vector store created successfully.")


@app.post('/ingest_url')
async def ingest_url(payload: dict):
    url = payload.get('url') if isinstance(payload, dict) else None
    if not url:
        raise HTTPException(status_code=400, detail="Missing 'url' in request body")
    try:
        # Use urllib to avoid adding extra dependencies
        from urllib.request import Request, urlopen
        req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(req) as resp:
            content = resp.read().decode('utf-8', errors='ignore')
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch URL: {e}")

    os.makedirs("uploaded_files", exist_ok=True)
    safe_name = url.replace('://', '_').replace('/', '_')
    file_path = f"uploaded_files/{safe_name}.html"
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    vector_store = VectoreStore(pc, DocumentProcessing(), TextProcessing())
    vector_store.create_store(file_path)
    return {"message": "URL ingested and vector store updated.", "file": file_path}


@app.post('/ingest_text')
async def ingest_text(payload: dict):
    if not isinstance(payload, dict):
        raise HTTPException(status_code=400, detail="Invalid payload")
    text = payload.get('text')
    title = payload.get('title') or 'written_text'
    if not text or not text.strip():
        raise HTTPException(status_code=400, detail="Missing 'text' in request body")

    os.makedirs("uploaded_files", exist_ok=True)
    safe_name = title.replace('://', '_').replace('/', '_').replace(' ', '_')
    file_path = f"uploaded_files/{safe_name}.txt"
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(text)

    vector_store = VectoreStore(pc, DocumentProcessing(), TextProcessing())
    vector_store.create_store(file_path)
    return {"message": "Text ingested and vector store updated.", "file": file_path}

def query_vector_store(query_text):
    answerQuestions = AnswerQuestions(vector_store=VectoreStore(pc, DocumentProcessing(), TextProcessing()), client=client) 
    answerQuestions.answer_query(query_text)

if __name__ == "__main__":
    # Example usage
    create_vector_store()
   #query_vector_store("What is the primary industry that Gyanko has worked in?")
    

