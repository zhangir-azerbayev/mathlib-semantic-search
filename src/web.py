from dotenv import load_dotenv

load_dotenv()

from flask import Flask, request, render_template, redirect, url_for
from src.app import AppState, ModerationError, url_of_entry
from src.embed_mathlib.embed_mathlib import text_of_entry

app = Flask(__name__)

app.config["TEMPLATES_AUTO_RELOAD"] = True


@app.route("/")
def index():
    query = request.args.get("query", None)
    print(f"query: {query}")
    if query is None:
        return render_template("main.html", query=query or "", results=None)

    try:
        search_result = AppState.current().search(query, gen_fake_answer=True)
        results = [
            dict(text=text_of_entry(r), name=r["name"], url=url_of_entry(r))
            for r in search_result.results
        ]
        suggested = request.args.get("suggested", False)
        include_suggested = not suggested
        print("suggested: ", suggested)
        return render_template(
            "main.html",
            query=query,
            results=results,
            fake_answer=search_result.fake_answer,
            # decl_names=list(AppState.current().decl_names), # [todo] this ends up bloating the html to 3MB
            decl_names=[],
            include_suggested=include_suggested,
        )
    except ModerationError:
        return render_template(
            "main.html",
            query=query,
            error="OpenAI returned a sensitive result!",
            decl_names=AppState.current().decl_names,
        )


@app.post("/upvote/")
def upvote():
    query = request.args.get("query", None)
    name = request.args.get("name", None)
    assert name is not None
    assert query is not None
    print(f"upvoting {name} for {query}")
    AppState.current().upvote(name, query)

    return "Success."


@app.post("/suggest/")
def suggest():
    print(request.form)
    query = request.form.get("query", None)
    suggestion = request.form.get("suggestion", None)
    assert suggestion is not None
    assert query is not None
    print(f"suggestion {suggestion} for {query}")
    AppState.current().suggestion(suggestion, query)
    url = url_for("index", query=query, suggested=True)

    return redirect(url)
