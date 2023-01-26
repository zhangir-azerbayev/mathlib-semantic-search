from app import AppState
from embed_mathlib.embed_mathlib import text_of_entry

if __name__ == "__main__":
    app = AppState(GEN_FAKE_ANSWER = True)

    while True:
        query = input("\n\nInput search query: ")

        print("searching...")

        results = app.search(query)

        for i, x in enumerate(results):
            print(f"RESULT {i}: ")
            print(text_of_entry(x))
