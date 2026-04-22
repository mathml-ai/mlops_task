import pandas as pd

df1 = pd.read_csv("data.csv")

print("Original shape:", df1.shape)

# Case: everything in one column
if len(df1.columns) == 1:
    print("Detected single-column CSV. Fixing...")

    # Extract header from column name
    header = df1.columns[0].split(",")

    # Split all rows
    df = df1.iloc[:, 0].str.split(",", expand=True)

    # Assign correct header
    df.columns = header

    # No need to drop first row now ✅
else:
    df = df1

print("Recovered columns:", list(df.columns))
print("Fixed shape:", df.shape)