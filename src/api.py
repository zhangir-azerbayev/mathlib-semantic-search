from typing import Optional, Union
from fastapi import FastAPI
from dataclasses import dataclass

from src.app import AppState

app = FastAPI()

state = AppState()


@app.get("/")
def read_root(q: str):
    results = state.search(q)
    return results


@app.post("/upvote/{name}")
def post_rating(name : str):
    return {"success": True}
