from dotenv import load_dotenv
load_dotenv()

from flask import Flask, request, render_template
from src.app import AppState, url_of_entry
from src.embed_mathlib.embed_mathlib import text_of_entry

app = Flask(__name__)

app.config['TEMPLATES_AUTO_RELOAD'] = True

@app.route("/")
def index():
    query = request.args.get('query', None)
    print(f"query: {query}")
    if query is None:
        return render_template('main.html', query=query or "", results = None)

    search_result = AppState.current().search(query, gen_fake_answer = True)
    results = [
        dict(
            text = text_of_entry(r),
            name = r['name'],
            url = url_of_entry(r))
            for r in search_result.results
    ]
    return render_template('main.html', query = query, results = results, fake_answer = search_result.fake_answer)


@app.post("/upvote/")
def upvote():
    query = request.args.get('query', None)
    name = request.args.get('name', None)
    assert name is not None
    assert query is not None
    print(f'upvoting {name} for {query}')
    name = request.args['name']
    AppState.current().upvote(name, query)

    return "Success."