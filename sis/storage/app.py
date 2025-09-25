# storage/app.py
from flask import Flask, request, jsonify
from pymongo import MongoClient, UpdateOne
import os, time

app = Flask(__name__)
MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongo:27017/")
client = MongoClient(MONGO_URI)
db = client["yahoo_db"]
col = db["answers"]

col.create_index("question_id", unique=True)

@app.post("/save_or_update")
def save_or_update():
    d = request.get_json()
    now = int(time.time())
    qid = d["question_id"]
    update = {
        "$set": {
            "question": d.get("question", ""),
            "dataset_answer": d.get("dataset_answer", ""),
            "llm_answer": d.get("llm_answer", ""),
            "score": float(d.get("score", 0.0)),
            "updated_at": now
        },
        "$setOnInsert": {"created_at": now, "hits": 0, "misses": 0, "total": 0}
    }
    col.update_one({"question_id": qid}, update, upsert=True)
    col.update_one({"question_id": qid}, {"$inc": {"misses": 1, "total": 1}})
    return jsonify({"ok": True})

@app.post("/increment_hit")
def increment_hit():
    d = request.get_json()
    qid = d["question_id"]
    col.update_one({"question_id": qid}, {"$inc": {"hits": 1, "total": 1}})
    return jsonify({"ok": True})

@app.get("/stats")
def stats():
    total_docs = col.estimated_document_count()
    pipeline = [
        {"$group": {"_id": None, "hits": {"$sum": "$hits"}, "misses": {"$sum": "$misses"}, "total": {"$sum": "$total"}}}
    ]
    agg = list(col.aggregate(pipeline))
    sums = agg[0] if agg else {"hits": 0, "misses": 0, "total": 0}
    sample = list(col.find({}, {"_id":0}).limit(5))
    return jsonify({
        "total_docs": total_docs,
        "hits": int(sums["hits"]),
        "misses": int(sums["misses"]),
        "total_accesses": int(sums["total"]),
        "sample": sample
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5004)
