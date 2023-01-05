import sys 
import json
import ndjson 
import numpy as np 
import faiss 
import openai
import time

def text_of_entry(x): 
    return (
        "/-- " + x["doc_string"] + " -/" + "\n" + x["formal_statement"]
        if x["doc_string"]
        else x["formal_statement"]
    )

IN_PATH = "docgen_with_embeddings.jsonl"
D = "1536" # dimensionality of embedding
K = 5 # number of results to retrieve

print("loading docs...")
with open(IN_PATH) as f: 
    data = ndjson.load(f)

print("loading embeddings...")
embeddings = []
for i in tqdm(range(len(data))): 
    embeddings.append(data[i].pop('embedding'))

embeddings = numpy.stack(embeddings, axis=0)

print("creating fast kNN database...")
database = faiss.IndexFlatL2(D)
database.add(embeddings)

print("\n" + "#"*10, "MATHLIB SEMANTIC SEARCH", "#"*10 + "\n")

while True: 
    query = input("Input search query: ")

    print("searching...")
    start_time = time.time()

    responses = openai.Embedding.create(
        input=[query], 
        model="text-embedding-ada-002", 
        )
    
    query_vec = np.expand_dims(responses['data'][0]['embedding'].astype('float32'), axis=0)

    _, idxs_np = database.search(query_vec, K)

    idxs = np.squeeze(idxs_np).tolist()

    results = [data[i] for i in idxs]

    end_time = time.time()

    print(f"Retrieved {K} results in {end_time-start_time} seconds")
    for i, x in enumerate(results): 
        print("RESULT {i}: ")
        print(text_of_entry(x))
