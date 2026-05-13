# -------------------------------
# STEP 7: VALIDATE SQL
# -------------------------------
def validate_sql(sql):

    forbidden_keywords = [
        "DROP",
        "DELETE",
        "UPDATE",
        "INSERT",
        "ALTER",
        "TRUNCATE",
        "CREATE"
    ]

    sql_upper = sql.upper()

    # Allow only SELECT queries
    if not sql_upper.strip().startswith("SELECT"):
        raise ValueError("Only SELECT queries are allowed.")

    # Block dangerous keywords
    for keyword in forbidden_keywords:
        if keyword in sql_upper:
            raise ValueError(f"Dangerous SQL detected: {keyword}")

    return True
def is_dangerous_question(question):

    dangerous_words = [
        "drop",
        "delete",
        "remove",
        "truncate",
        "alter",
        "update",
        "insert",
        "create table"
    ]

    question_lower = question.lower()

    for word in dangerous_words:
        if word in question_lower:
            return True

    return False