import uvicorn
import requests
import os
from typing import Optional
from fastapi import FastAPI
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

DEFAULT_AGENT_URL = f"https://bey.chat/{AGENT_ID}" if AGENT_ID else "https://bey.chat/"

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
            session.add(Tutor(name="Kimi (AI Mentor)", avatar_id=str(AGENT_ID), preview_url=None))
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
    if not qm.join():
        return {"status": "queued", "pos": 1}

    generated_url = None
    if API_KEY and AGENT_ID:
        try:            
            endpoints = ["https://api.bey.dev/v1/chats", "https://api.bey.dev/v1/conversations"]
            
            headers = {"x-api-key": API_KEY, "Content-Type": "application/json"}
            payload = {"agentId": AGENT_ID}
            
            for url in endpoints:
                try:
                    print(f"📡 Trying API: {url}")
                    resp = requests.post(url, headers=headers, json=payload, timeout=5)
                    if resp.status_code in [200, 201]:
                        data = resp.json()
                        generated_url = data.get('url') or data.get('chatUrl') or data.get('webUrl')
                        if generated_url:
                            print("✅ Secure Session Created")
                            break
                except:
                    continue
                
        except Exception as e:
            print(f"⚠️ Error: {e}")

    if generated_url:
        return {"status": "active", "url": generated_url}
    else:
        print("⚠️ Keys missing or API fail. Using Fallback.")
        return {"status": "active", "url": DEFAULT_AGENT_URL}

@app.post("/session/end")
def end_session():
    qm.leave()
    return {"status": "ok"}