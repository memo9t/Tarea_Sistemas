# cache/app.py 
from flask import Flask, request, jsonify
from cachetools import LRUCache, FIFOCache
import requests, hashlib, time, os

app = Flask(__name__)

CACHE_SIZE = int(os.getenv("CACHE_SIZE", "500"))
CACHE_POLICY = os.getenv("CACHE_POLICY", "LRU")
TTL = int(os.getenv("CACHE_TTL", "0"))

if CACHE_POLICY.upper() == "FIFO":
    cache = FIFOCache(maxsize=CACHE_SIZE)
else:
    cache = LRUCache(maxsize=CACHE_SIZE)

LLM_URL = os.getenv("LLM_URL", "http://llm:5002/answer")
SCORE_URL = os.getenv("SCORE_URL", "http://score:5003/score")
STORE_SAVE_URL = os.getenv("STORE_SAVE_URL", "http://storage:5004/save_or_update")
STORE_INC_HIT_URL = os.getenv("STORE_INC_HIT_URL", "http://storage:5004/increment_hit")

def qid(text: str) -> str:
    return hashlib.sha256(text.strip().lower().encode()).hexdigest()

def get_cached(qid_):
    item = cache.get(qid_)
    if not item: return None
    if TTL > 0 and time.time() - item["ts"] > TTL:
        del cache[qid_]
        return None
    return item["value"]

def set_cached(qid_, value):
    cache[qid_] = {"value": value, "ts": time.time()}

@app.post("/query")
def query():
    data = request.get_json()
    question = data["question"]
    dataset_answer = data.get("dataset_answer", "")
    qidh = qid(question)

    cached = get_cached(qidh)
    if cached:
        try:
            requests.post(STORE_INC_HIT_URL, json={"question_id": qidh}, timeout=5)
        except:
            pass
        return jsonify({"from_cache": True, **cached})

    llm_resp = requests.post(LLM_URL, json={"question": question}, timeout=60).json()
    llm_answer = llm_resp["llm_answer"]

    score_resp = requests.post(SCORE_URL, json={
        "llm_answer": llm_answer,
        "dataset_answer": dataset_answer
    }, timeout=60).json()
    score = score_resp["score"]

    record = {
        "question_id": qidh,
        "question": question,
        "dataset_answer": dataset_answer,
        "llm_answer": llm_answer,
        "score": float(score)
    }

    try:
        requests.post(STORE_SAVE_URL, json=record, timeout=30)
    except:
        pass

    result = {"from_cache": False, "llm_answer": llm_answer, "dataset_answer": dataset_answer, "score": score}
    set_cached(qidh, result)
    return jsonify(result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
