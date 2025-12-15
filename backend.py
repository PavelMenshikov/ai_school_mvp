import uvicorn
import requests
import os
import logging
from typing import Optional
from fastapi import FastAPI
from sqlmodel import SQLModel, Field, Session, create_engine, select
from dotenv import load_dotenv


load_dotenv() 

API_KEY = os.getenv("BP_API_KEY")
AGENT_ID = os.getenv("BP_AGENT_ID")

DEFAULT_AGENT_URL = f"https://bey.chat/{AGENT_ID}"


if not API_KEY:
    print("⚠️ ВНИМАНИЕ: Не найден BP_API_KEY в файле .env!")

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
            url = "https://api.bey.dev/v1/chats"
            headers = {
                "x-api-key": API_KEY,
                "Content-Type": "application/json"
            }
            payload = {"agentId": AGENT_ID}
            
            print(f"📡 API Request to Beyond Presence...")
            resp = requests.post(url, headers=headers, json=payload, timeout=8)
            
            if resp.status_code in [200, 201]:
                data = resp.json()
                generated_url = data.get('url') or data.get('chatUrl') or data.get('webUrl')
                if generated_url:
                    print("✅ Secure Session Created")
            else:
                print(f"⚠️ API Error: {resp.status_code} - {resp.text}")
        except Exception as e:
            print(f"⚠️ Connection Error: {e}")

    if generated_url:
        return {"status": "active", "url": generated_url}
    else:
        print("⚠️ Fallback to public URL (Login might be required)")
        return {"status": "active", "url": DEFAULT_AGENT_URL}

@app.post("/session/end")
def end_session():
    qm.leave()
    return {"status": "ok"}