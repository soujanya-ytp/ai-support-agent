from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from pathlib import Path
import sqlite3, re

DB_PATH=Path(__file__).resolve().parent.parent / "sample.db"
app=FastAPI(title="AI Customer Support Agent (Mock AI)", version="1.0.0", description="Offline deterministic AI simulation; no API key required.")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173","http://127.0.0.1:5173"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

def db():
    con=sqlite3.connect(DB_PATH); con.row_factory=sqlite3.Row; return con

def init_db():
    with db() as con:
        con.execute("CREATE TABLE IF NOT EXISTS tickets(id INTEGER PRIMARY KEY AUTOINCREMENT,subject TEXT NOT NULL,description TEXT NOT NULL,category TEXT NOT NULL,priority TEXT NOT NULL,status TEXT NOT NULL,escalated INTEGER NOT NULL DEFAULT 0)")
        con.execute("CREATE TABLE IF NOT EXISTS knowledge(id INTEGER PRIMARY KEY AUTOINCREMENT,title TEXT NOT NULL,content TEXT NOT NULL)")
        if con.execute("SELECT COUNT(*) FROM knowledge").fetchone()[0] == 0:
            con.executemany("INSERT INTO knowledge(title,content) VALUES(?,?)", [('Password reset', 'Use Forgot password on the sign-in screen. A reset link is sent to the registered email. Never ask users to share passwords.'), ('Refund policy', 'Refund requests within 30 days of purchase are eligible for review. Agents must verify the order before processing a refund.'), ('Service outage', 'For a confirmed service outage, acknowledge impact, check the status page, and escalate to the incident team. Do not promise an unverified recovery time.')])

@app.on_event("startup")
def startup(): init_db()

@app.get("/api/health")
def health(): return {"status":"ok","mode":"offline-mock-ai"}

class AskIn(BaseModel): question: str = Field(min_length=1,max_length=1000)

class TicketIn(BaseModel):
    subject: str = Field(min_length=1,max_length=160)
    description: str = Field(min_length=1,max_length=4000)

@app.get("/api/tickets")
def list_tickets():
    with db() as con: return [dict(r) for r in con.execute("SELECT * FROM tickets ORDER BY id DESC")]

@app.post("/api/tickets")
def create_ticket(item: TicketIn):
    text=(item.subject+" "+item.description).lower()
    category="account" if any(x in text for x in ["password","login","sign in"]) else "billing" if any(x in text for x in ["refund","payment","invoice","charge"]) else "incident" if any(x in text for x in ["outage","down","unavailable","error"]) else "general"
    priority="high" if any(x in text for x in ["outage","security breach","data leak","urgent"]) else "medium" if any(x in text for x in ["refund","cannot login","blocked"]) else "low"
    escalated=any(x in text for x in ["security breach","data leak","threat","medical emergency"])
    with db() as con:
        cur=con.execute("INSERT INTO tickets(subject,description,category,priority,status,escalated) VALUES(?,?,?,?,?,?)",(item.subject.strip(),item.description.strip(),category,priority,"escalated" if escalated else "open",int(escalated)))
        con.commit(); return dict(con.execute("SELECT * FROM tickets WHERE id=?",(cur.lastrowid,)).fetchone())

@app.get("/api/suggest")
def suggest(q: str = Query(min_length=1)):
    terms=[t.lower() for t in re.findall(r"[a-zA-Z0-9]+",q) if len(t)>2]
    with db() as con: rows=[dict(r) for r in con.execute("SELECT * FROM knowledge")]
    ranked=[]
    for row in rows:
        score=sum((row['title']+' '+row['content']).lower().count(t) for t in terms)
        if score: ranked.append({**row,"score":score})
    ranked.sort(key=lambda x:x['score'],reverse=True)
    return {"suggestions":ranked[:3],"reply":ranked[0]['content'] if ranked else "No matching guidance found. Escalate to a human agent.","needs_human":not bool(ranked),"note":"Rule-based mock AI; confirm policy before acting."}

