# src/main.py
from fastapi import FastAPI

app = FastAPI(title="Senior Python Async CRM API")

@app.get("/ping")
def ping():
    return {"msg": "pong"}
