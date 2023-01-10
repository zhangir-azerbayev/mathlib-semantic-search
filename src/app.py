from typing import Any
import streamlit as st
import pandas as pd
import ndjson
import numpy as np
import faiss
import openai
import time
from embed_mathlib.embed_mathlib import text_of_entry, mk_vote
from database import put

DOCS_PATH = "./src/parse_docgen/docgen_export_with_formal_statement.jsonl"
VECS_PATH = "./src/embed_mathlib/np_embeddings.npy"
D = 1536  # dimensionality of embedding
K = 10  # number of results to retrieve


@st.experimental_singleton
def load():

    print("loading docs...")
    with open(DOCS_PATH) as f:
        docs = ndjson.load(f)

    print("loading embeddings...")
    embeddings = np.load(VECS_PATH).astype("float32")

    # sanity checks
    assert D == embeddings.shape[1]
    assert embeddings.shape[0] == len(docs)

    print(f"Found {len(docs)} mathlib declarations")

    print("creating fast kNN database...")
    database = faiss.IndexFlatL2(D)
    database.add(embeddings)  # type: ignore

    print("\n" + "#" * 10, "MATHLIB SEMANTIC SEARCH", "#" * 10 + "\n")

    return docs, database


docs, database = load()


@st.cache
def grab(query: str):
    print("searching...")
    start_time = time.time()

    responses: Any = openai.Embedding.create(
        input=[query], model="text-embedding-ada-002"
    )

    query_vec = np.expand_dims(
        np.array(responses["data"][0]["embedding"]).astype("float32"), axis=0
    )

    _, idxs_np = database.search(query_vec, K)  # type: ignore

    idxs = np.squeeze(idxs_np).tolist()

    results = [docs[i] for i in idxs]

    end_time = time.time()

    print(f"Retrieved {K} results in {end_time-start_time} seconds")

    return results


input = st.text_input(
    "Search mathlib with natural language:", placeholder="second isomorphism theorem"
)

if input:
    results = grab(input)

    def click(val, i):
        vote = mk_vote(result=results[i], val=val, rank=i, query=input)
        put(vote)
        print("sent vote")

    for i, x in enumerate(results):
        st.write(i)
        up, down = st.button("👍", key=f"thumbup{i}"), st.button("👎", key=f"thumbdn{i}")
        code = text_of_entry(x)
        st.code(code, "haskell")


# run this with `streamlit run src/app.py``
