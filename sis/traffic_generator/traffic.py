# traffic_generator/traffic.py
import os, time, random
import pandas as pd
import numpy as np
import requests

DATASET_PATH = os.getenv("DATASET_PATH", "/app/dataset/train_10k.csv")
CACHE_URL = os.getenv("CACHE_URL", "http://cache:5001/query")
RATE = float(os.getenv("RATE", "0.2")) 
DIST = os.getenv("DIST", "exponential")

COL_Q = os.getenv("COL_Q", "question_content")
COL_A = os.getenv("COL_A", "best_answer")

def inter_arrival():
    """Devuelve el tiempo de espera según la distribución seleccionada."""
    if DIST == "exponential":
        return np.random.exponential(1.0 / RATE)

    elif DIST == "poisson":
        return max(0.1, np.random.poisson(1.0 / RATE))

    elif DIST == "uniform":
        return np.random.uniform(0, 2.0 / RATE)

    elif DIST == "normal":
        return max(0.1, np.random.normal(1.0 / RATE, 0.5 / RATE))

    else:
        return 1.0 / RATE

def main():
    df = pd.read_csv(DATASET_PATH, header=None, names=["class", "question_title", "question_content", "best_answer"])
    assert len(df) >= 10000, "El dataset debe tener al menos 10.000 elementos"

    while True:
        row = df.sample(1).iloc[0]
        q = str(row[COL_Q])
        a = str(row[COL_A])

        q_title = str(row["question_title"]) if pd.notna(row["question_title"]) else ""
        q_content = str(row["question_content"]) if pd.notna(row["question_content"]) else ""
        q = (q_title + " " + q_content).strip()
        
        payload = {"question": q, "dataset_answer": a}
        try:
            r = requests.post(CACHE_URL, json=payload, timeout=30)
            print(r.json())
        except Exception as e:
            print("Error:", e)

        time.sleep(inter_arrival())

if __name__ == "__main__":
    main()
