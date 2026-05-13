import pandas as pd
import sqlite3
import os
from langchain_community.utilities import SQLDatabase

def load_and_clean_csv(file_path):
    print("Loading CSV...")
    df = pd.read_csv(file_path)

    # Clean column names
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    # Remove empty rows & duplicates
    df.dropna(how='all', inplace=True)
    df.drop_duplicates(inplace=True)

    # Convert date column
    for col in df.columns:

     if "date" in col.lower():

        try:

            df[col] = pd.to_datetime(
                df[col],
                errors="coerce"
            )

        except:
            pass
    
    # Fix floating precision
    numeric_cols = df.select_dtypes(include=['number']).columns
    df[numeric_cols] = df[numeric_cols].round(2)

    return df


# -------------------------------
# STEP 2: CREATE SQLITE DATABASE
# -------------------------------
def create_sqlite_db(df, db_name="database/sales.db", table_name="sales_data"):
    print("Creating database...")
    os.makedirs("database", exist_ok=True)
    conn = sqlite3.connect(db_name)

    df.to_sql(table_name, conn, if_exists='replace', index=False)

    conn.commit()
    conn.close()

    return db_name


# -------------------------------
# STEP 3: TEST DATABASE
# -------------------------------
def test_db(db_path):
    print("Testing database...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM sales_data LIMIT 5")
    rows = cursor.fetchall()

    print("\nSample Data from Database:\n")
    for row in rows:
        print(row)

    conn.close()


# -------------------------------
# STEP 4: CONNECT DATABASE (LangChain)
# -------------------------------
def connect_db(db_path):
    db = SQLDatabase.from_uri(f"sqlite:///{db_path}")
    return db