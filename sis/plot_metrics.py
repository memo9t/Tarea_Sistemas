# plot_metrics.py
from pymongo import MongoClient
import pandas as pd
import matplotlib.pyplot as plt
import os

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
col = client["yahoo_db"]["answers"]

pipeline = [
    {"$project": {
        "ts": {"$toDate": {"$multiply": ["$created_at", 1000]}},
        "hits": "$hits",
        "total": "$total"
    }},
    {"$group": {
        "_id": {"$dateTrunc": {"date": "$ts", "unit": "minute"}},
        "hits": {"$sum": "$hits"},
        "total": {"$sum": "$total"}
    }},
    {"$sort": {"_id": 1}}
]

res = list(col.aggregate(pipeline))

if not res:
    print("⚠️ No se encontraron resultados en la colección.")
else:
    df = pd.DataFrame([
        {"time": r["_id"], "hits": r["hits"], "total": r["total"]}
        for r in res
    ])
    df["hit_rate"] = df["hits"] / df["total"]


    df.to_csv("hit_rate_by_minute.csv", index=False)

    plt.figure(figsize=(8, 4))
    plt.plot(df["time"], df["hit_rate"], marker="o")
    plt.xlabel("Tiempo (minutos)")
    plt.ylabel("Hit rate")
    plt.title("Evolución del Hit Rate por minuto")
    plt.xticks(rotation=45)
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.tight_layout()
    plt.savefig("plot_hitrate.png")
    plt.close()

    print(" Gráfico generado: plot_hitrate.png")
    print(" Datos exportados: hit_rate_by_minute.csv")
