import kagglehub
import pandas as pd

path = kagglehub.dataset_download("jarupula/yahoo-answers-dataset")

print("Path to dataset files:", path)

csv_file = f"{path}/train.csv"

df = pd.read_csv(csv_file, nrows=10000)

df.to_csv("train_10k.csv", index=False)

print("Subset guardado en train_10k.csv con", len(df), "filas")

