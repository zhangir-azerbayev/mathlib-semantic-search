import numpy as np
import json, ndjson
from tqdm import tqdm


print("loading docs...")
with open("../parse_docgen/docgen_export_with_formal_statement.jsonl") as f: 
    docs = ndjson.load(f)

print("loading embeddings...")
embeddings = []
with open("embeddings.jsonl") as f: 
    for i, line in tqdm(enumerate(f)): 
        entry = json.loads(line)

        # check for alignment
        assert entry["name"] == docs[i]["name"]

        embeddings.append(np.array(entry["embedding"]).astype('float32'))

embeddings = np.stack(embeddings, axis=0).astype('float32')

print("saving array...")
np.save("np_embeddings.npy", embeddings)


        



