# score/app.py
from flask import Flask, request, jsonify
from sentence_transformers import SentenceTransformer, util

app = Flask(__name__)
model = SentenceTransformer("all-MiniLM-L6-v2")

@app.post("/score")
def score():
    data = request.get_json()
    a1 = data.get("llm_answer", "") or ""
    a2 = data.get("dataset_answer", "") or ""
    e1 = model.encode(a1, convert_to_tensor=True, normalize_embeddings=True)
    e2 = model.encode(a2, convert_to_tensor=True, normalize_embeddings=True)
    sim = util.cos_sim(e1, e2).item()
    return jsonify({"score": float(sim)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003)
