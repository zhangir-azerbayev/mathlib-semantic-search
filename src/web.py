from dotenv import load_dotenv
load_dotenv()

from flask import Flask, request, render_template
from src.app import AppState
from src.embed_mathlib.embed_mathlib import text_of_entry

app = Flask(__name__)

state = AppState()

@app.route("/")
def index():
    query = request.args.get('query', None)
    print(f"query: {query}")
    if query is None:
        return render_template('main.html', query=query or "", results = None)

    results = state.search(query)
    results = [
        dict(text = text_of_entry(r), name = r['name']) for r in results
    ]
    return render_template('main.html', query = query, results = results)


@app.post("/upvote/")
def upvote():
    query = request.args.get('query', None)
    name = request.args.get('name', None)
    assert name is not None
    assert query is not None
    print(f'upvoting {name} for {query}')
    name = request.args['name']
    state.upvote(name, query)

    return "Success."