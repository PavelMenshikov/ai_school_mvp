import uvicorn
import requests
import os
import uuid 
from typing import Optional
from fastapi import FastAPI, HTTPException
from sqlmodel import SQLModel, Field, Session, create_engine, select
from pathlib import Path


def get_secure_key(key_name):    
    val = os.getenv(key_name)
    if val: return val.strip('"').strip("'")   
    
    try:
        paths = [Path(".streamlit/secrets.toml"), Path.home() / ".streamlit/secrets.toml"]
        for p in paths:
            if p.exists():
                with open(p, "r", encoding="utf-8") as f:
                    for line in f:
                        if key_name in line and "=" in line:
                            return line.split("=", 1)[1].strip().strip('"').strip("'")
    except:
        pass
    return None

API_KEY = get_secure_key("BP_API_KEY")
AGENT_ID = get_secure_key("BP_AGENT_ID")


DATABASE_URL = "sqlite:///./school.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str

class Tutor(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    avatar_id: str 
    preview_url: Optional[str] = None 

def init_db():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        if not session.exec(select(User)).first():
            session.add(User(username="demo_client"))
            session.add(Tutor(name="AI Mentor", avatar_id=str(AGENT_ID), preview_url=None))
            session.commit()

class QueueManager:
    def __init__(self):
        self.active = 0
    def join(self):
        if self.active < 10:
            self.active += 1
            return True
        return False
    def leave(self):
        if self.active > 0: self.active -= 1

qm = QueueManager()
init_db()
app = FastAPI()


@app.get("/tutors")
def get_tutors():
    with Session(engine) as session:
        return session.exec(select(Tutor)).all()

@app.post("/session/start")
def start_session():
   
    if not API_KEY or not AGENT_ID:
        print("❌ ОШИБКА: Нет ключей API_KEY или AGENT_ID")
        raise HTTPException(status_code=500, detail="Server misconfigured: No API Keys")

  
    if not qm.join():
        return {"status": "queued", "pos": 1}

    
    try:
        url = "https://api.bey.dev/v1/chats"
        
        headers = {
            "x-api-key": API_KEY,
            "Content-Type": "application/json"
        }
        
        
        guest_id = f"guest_{uuid.uuid4().hex[:8]}"
        
        
        payload = {
            "agentId": AGENT_ID,
            "externalUserId": guest_id, 
            "metadata": {"source": "api_mvp"} 
        }
        
        print(f"📡 Запрос к API: {url} | User: {guest_id}")
        resp = requests.post(url, headers=headers, json=payload, timeout=10)
        
        print(f"📩 Статус ответа: {resp.status_code}")
        
        if resp.status_code in [200, 201]:
            data = resp.json()
            print(f"📦 Ответ API: {data}") 
            link = data.get('url') or data.get('chatUrl') or data.get('webUrl')
            
            if link:
                return {"status": "active", "url": link}
            else:
                print("❌ В ответе нет ссылки!")
                raise HTTPException(status_code=502, detail="API returned no URL")
        else:
            print(f"❌ Ошибка API: {resp.text}")
        
            raise HTTPException(status_code=resp.status_code, detail=f"BP API Error: {resp.text}")

    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/session/end")
def end_session():
    qm.leave()
    return {"status": "ok"}