# llm_service/app.py
from flask import Flask, request, jsonify
import os, requests, json

app = Flask(__name__)
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_KEY:
    raise ValueError("Debes definir la variable de entorno GEMINI_API_KEY con tu API key de Google AI Studio")

def ask_gemini(prompt: str) -> str:
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
    headers = {"Content-Type": "application/json"}
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    r = requests.post(url, params={"key": GEMINI_KEY}, headers=headers, json=payload, timeout=60)
    j = r.json()
    try:
        return j["candidates"][0]["content"]["parts"][0]["text"].strip()
    except Exception:
        return json.dumps(j)

@app.post("/answer")
def answer():
    data = request.get_json()
    question = data["question"]
    prompt = f"Pregunta: {question}\nResponde de forma breve y precisa:"
    ans = ask_gemini(prompt)
    return jsonify({"llm_answer": ans})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)
