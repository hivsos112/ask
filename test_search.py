from rapidfuzz import process, fuzz
import pandas as pd

df = pd.read_excel('题库.xlsx', header=1)
df = df.fillna('')
questions = df['题目'].astype(str).tolist()

query = "跨境"
matches = process.extract(query, questions, limit=5, scorer=fuzz.partial_ratio)
print(f"Query: {query}")
for match in matches:
    print(match)
