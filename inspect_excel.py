import pandas as pd

try:
    df = pd.read_excel('题库.xlsx')
    print("Columns:", df.columns.tolist())
    print("First 3 rows:")
    print(df.head(3))
except Exception as e:
    print(f"Error reading excel: {e}")
