from dataclasses import dataclass, field
from typing import Any, Literal, Optional, TypedDict, Union
from uuid import uuid4
import ndjson
import numpy as np
from datetime import datetime
import faiss
import openai
import time
from src.database import DB

ExprStr = Union[
    str, tuple[Literal['c', 'n'], "ExprStr"], tuple[Literal['n'], "ExprStr", "ExprStr"]
]

class Arg(TypedDict):
  arg : ExprStr
  implicit : bool

class Result(TypedDict):
    kind : str
    line : int
    name : str
    doc_string : str
    formal_statement : str
    is_meta : bool
    type: ExprStr
    filename : str

    args : list[Arg]
    attributes : list[str]
    constructors : list
    equations : list
    structure_fields : list
    noncomputable_reason : Optional[str]


def url_of_entry(x : Result):
    """ Hackily recover the URL from file and name. """
    try:
        # https://leanprover-community.github.io/mathlib_docs/topology/instances/ennreal.html#metric_space_emetric_ball
        name = x['name'] # metric_space_emetric_ball
        file = x['filename'] # "/data/lily/zaa7/duplicates/doc-gen/_target/deps/mathlib/src/topology/instances/ennreal.lean"
        _, f = file.split('mathlib/src/')
        p, ext = f.split('.')
        return f"https://leanprover-community.github.io/mathlib_docs/{p}.html#{name}"
    except Exception:
        return "#"


@dataclass
class SearchResult:
    query: str
    results: list[Result]
    fake_answer: Optional[str] = field(default =None)

class AppState:
    docs: list
    database: faiss.IndexFlatL2
    K: int
    cache: dict[str, SearchResult]
    """ Number of results to return """

    def __init__(
        self,
        *,
        docs_path="./src/parse_docgen/docgen_export_with_formal_statement.jsonl",
        vecs_path="./src/embed_mathlib/np_embeddings.npy",
        D=1536,  # dimensionality of embedding
        K=10,  # number of results to retrieve
    ):
        self.cache = {}
        self.K = K
        self.db = DB()
        print(f"loading docs from {docs_path}")
        with open(docs_path) as f:
            self.docs = ndjson.load(f)

        print(f"loading embeddings from {vecs_path}")
        embeddings = np.load(vecs_path).astype("float32")

        # sanity checks
        assert D == embeddings.shape[1]
        assert embeddings.shape[0] == len(self.docs)

        print(f"Found {len(self.docs)} mathlib declarations")

        print("creating fast kNN database...")
        self.database = faiss.IndexFlatL2(D)
        self.database.add(embeddings)  # type: ignore

        print("\n" + "#" * 10, "MATHLIB SEMANTIC SEARCH", "#" * 10 + "\n")

    def upvote(self, name : str, query : str):
        self.db.put({
            "kind" : "mathlib-semantic-search/vote",
            "name" : name,
            "timestamp" : datetime.now().isoformat(),
            "id" : uuid4().hex,
            "query" : query,
        })

    def search(self, query: str, K=None, gen_fake_answer : bool = False) -> SearchResult:
        if query in self.cache:
            return self.cache[query]
        fake_ans = None
        if gen_fake_answer:
            few_shot = open('./src/codex_prompt.txt').read().strip()
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

            fake_ans = out["choices"][0]["text"] # type: ignore
            query = f"/-- {query} -/\n" + fake_ans
            print("###QUERY: \n", query)
        K = K or self.K
        start_time = time.time()

        responses: Any = openai.Embedding.create(
            input=[query], model="text-embedding-ada-002"
        )

        query_vec = np.expand_dims(
            np.array(responses["data"][0]["embedding"]).astype("float32"), axis=0
        )

        _, idxs_np = self.database.search(query_vec, K)  # type: ignore

        idxs = np.squeeze(idxs_np).tolist()

        results = [Result(**self.docs[i]) for i in idxs]

        end_time = time.time()

        print(f"Retrieved {K} results in {end_time - start_time} seconds")
        result = SearchResult(
            query = query, results = results, fake_answer = fake_ans
        )
        self.cache[query] = result
        return result


    _cur = None
    @classmethod
    def current(cls):
        if cls._cur is None:
            cls._cur = cls()
        return cls._cur
