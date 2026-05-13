from utils.db import *
from utils.llm import *
from utils.sql_generator import *
from utils.validator import *
import sqlite3
print("STARTING SCRIPT...")


# -------------------------------
# STEP 9: GET DATABASE SCHEMA
# -------------------------------
def get_schema(df):

    schema = []

    for column, dtype in zip(df.columns, df.dtypes):
        schema.append(f"{column} ({dtype})")

    return "\n".join(schema)

# -------------------------------
# MAIN EXECUTION
# -------------------------------
if __name__ == "__main__":

    print("MAIN BLOCK RUNNING...")

    file_path = "data/sales.csv"

    # Load & clean CSV
    df = load_and_clean_csv(file_path)

    print("\nData Preview:\n")
    print(df.head())

    print("\nData Types:\n")
    print(df.dtypes)

    # Create database
    db_path = create_sqlite_db(df)

    # Generate schema
    schema = get_schema(df)

    print("\nDATABASE SCHEMA:\n")
    print(schema)

    print(f"\nDatabase created successfully: {db_path}")

    # Test DB
    test_db(db_path)

    # Load database + LLM
    db = connect_db(db_path)
    llm = load_llm()

    print("\nAI READY ✅")

    # Main AI loop
    while True:

        question = input("\nAsk a question (type 'exit' to stop): ")

        if question.lower() == "exit":
            print("Exiting...")
            break
        # Detect dangerous requests
        if is_dangerous_question(question):

            print("\nBLOCKED ❌")
            print("Dangerous database operations are not allowed.")

            continue
        # Generate SQL
        sql_query = generate_sql_query(
            llm,
            question
        )

        print("\nGenerated SQL:")
        print(sql_query)

        # Connect SQLite
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        try:

            # Validate SQL
            validate_sql(sql_query)

            # Execute query
            cursor.execute(sql_query)

            results = cursor.fetchall()

            print("\nResult:")

            for row in results[:10]:
                print(row)

        except Exception as e:

            print("\nSQL FAILED ❌")
            print("Error:", e)

            # Try auto-fixing SQL
            try:

                fixed_sql = fix_sql_query(
                    llm,
                    question,
                    sql_query,
                    str(e)
                )

                print("\nFIXED SQL ✅")
                print(fixed_sql)

                validate_sql(fixed_sql)

                cursor.execute(fixed_sql)

                fixed_results = cursor.fetchall()

                print("\nFixed Result:")

                for row in fixed_results[:10]:
                    print(row)

            except Exception as fix_error:

                print("\nAUTO FIX FAILED ❌")
                print(fix_error)

        conn.close()