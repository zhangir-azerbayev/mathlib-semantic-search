import sys
import json
import ndjson
import numpy as np
import faiss
import openai
import time
from embed_mathlib.embed_mathlib import text_of_entry

GEN_FAKE_ANSWER = True


DOCS_PATH = "parse_docgen/docgen_export_with_formal_statement.jsonl"
VECS_PATH = "embed_mathlib/np_embeddings.npy"
D = 1536  # dimensionality of embedding
K = 10  # number of results to retrieve

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
database.add(embeddings)

print("\n" + "#" * 10, "MATHLIB SEMANTIC SEARCH", "#" * 10 + "\n")

while True:
    query = input("\n\nInput search query: ")

    if GEN_FAKE_ANSWER: 
        few_shot = open('codex_prompt.txt').read().strip()
        codex_prompt = few_shot + " " + query + "\n"

        print("###PROMPT: \n", codex_prompt)

        out = openai.Completion.create(
            engine="code-davinci-002",
            prompt=codex_prompt,
            max_tokens=512,
            n=1,
            temperature=0,
            stop=":=",
        )

        print(out)

        fake_ans = out["choices"][0]["text"]
        query = f"/-- {query} -/\n" + fake_ans
        print("###QUERY: \n", query)

    print("searching...")
    start_time = time.time()

    responses = openai.Embedding.create(input=[query], model="text-embedding-ada-002")

    query_vec = np.expand_dims(
        np.array(responses["data"][0]["embedding"]).astype("float32"), axis=0
    )

    _, idxs_np = database.search(query_vec, K)

    idxs = np.squeeze(idxs_np).tolist()

    results = [docs[i] for i in idxs]

    end_time = time.time()

    print(f"Retrieved {K} results in {end_time-start_time} seconds")
    for i, x in enumerate(results):
        print(f"RESULT {i}: ")
        print(text_of_entry(x))
