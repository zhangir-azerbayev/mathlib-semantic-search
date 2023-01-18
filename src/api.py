from typing import Optional, Union
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from dataclasses import dataclass
from flask import render_template
from src.embed_mathlib.embed_mathlib import text_of_entry
import os
from src.app import AppState
import modal

app = FastAPI()

image = modal.Image.debian_slim().pip_install_from_requirements(requirements_txt = "requirements.txt")
stub = modal.Stub("mathlib-semantic-search")


@stub.asgi(image=image, secret=modal.Secret.from_name("lean-chat"))
def fastapi_app():
    assert os.environ.get('AWS_REGION') == "us-east-1"
    return app

@app.get("/")
def read_root(query: str = ""):
    assert os.environ.get('AWS_REGION') == "us-east-1"
    if query:
        results = AppState.current().search(query)
        results = [
            dict(text = text_of_entry(r), name = r['name']) for r in results
        ]
        html = render_template('main.html', query = query, results = results)
        return HTMLResponse(html)
    else:
        return HTMLResponse(render_template('main.html', query = "", results = None))


@app.post("/upvote/{name}")
def post_rating(name : str):
    return {"success": True}

if __name__ == "__main__":
    stub.serve()