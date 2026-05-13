# -------------------------------
# STEP 6: NL → SQL
# -------------------------------
def generate_sql_query(
    llm,
    question,
    schema
):

    print("HYBRID SQL FUNCTION RUNNING")

    question_lower = question.lower()

    # -------------------------
    # Extract columns from schema
    # -------------------------
    columns = []
    numeric_columns = []
    date_columns = []

    for line in schema.split("\n"):

        line = line.strip()

        if not line:
            continue

        # Example:
        # sales_amount (float64)
        parts = line.split("(")

        col_name = parts[0].strip()

        dtype = ""

        if len(parts) > 1:
            dtype = (
                parts[1]
                .replace(")", "")
                .lower()
            )

        columns.append(col_name)

        # -------------------------
        # Detect numeric columns
        # -------------------------
        if any(
            x in dtype
            for x in [
                "int",
                "float",
                "double",
                "decimal"
            ]
        ):
            numeric_columns.append(
                col_name
            )

        # -------------------------
        # Detect date columns
        # -------------------------
        if any(
            x in col_name.lower()
            for x in [
                "date",
                "time",
                "year"
            ]
        ):
            date_columns.append(
                col_name
            )

    # -------------------------
    # TREND QUERY
    # Example:
    # Trend of sales_amount over sale_date
    # -------------------------
    if "trend" in question_lower:

        numeric_col = None
        date_col = None

        for col in columns:

            if col.lower() in question_lower:

                if col in date_columns:
                    date_col = col

                elif col in numeric_columns:
                    numeric_col = col

        if numeric_col and date_col:

            return f"""
SELECT
    strftime('%Y-%m', {date_col}) AS month,
    AVG({numeric_col}) AS avg_{numeric_col}
FROM sales_data
GROUP BY month
ORDER BY month
""".strip()

    # -------------------------
    # COUNT QUERY
    # Example:
    # Count by region
    # -------------------------
    if "count by" in question_lower:

        category_col = None

        for col in columns:

            if col.lower() in question_lower:

                category_col = col
                break

        if category_col:

            return f"""
SELECT
    {category_col},
    COUNT(*) AS total_count
FROM sales_data
GROUP BY {category_col}
ORDER BY total_count DESC
""".strip()

    # -------------------------
    # AVERAGE QUERY
    # Example:
    # Average sales_amount by region
    # -------------------------
    if "average" in question_lower:

        numeric_col = None
        category_col = None

        for col in columns:

            if col.lower() in question_lower:

                if col in numeric_columns:
                    numeric_col = col

                else:
                    category_col = col

        if numeric_col and category_col:

            # If category is date/year
            if any(
                x in category_col.lower()
                for x in [
                    "date",
                    "time",
                    "year"
                ]
            ):

                return f"""
SELECT
    {category_col},
    AVG({numeric_col}) AS avg_{numeric_col}
FROM sales_data
GROUP BY {category_col}
ORDER BY {category_col}
""".strip()

            # Normal category averages
            return f"""
SELECT
    {category_col},
    AVG({numeric_col}) AS avg_{numeric_col}
FROM sales_data
GROUP BY {category_col}
ORDER BY avg_{numeric_col} DESC
""".strip()

    # -------------------------
    # RELATIONSHIP QUERY
    # Example:
    # Relationship between X and Y
    # -------------------------
    if "relationship" in question_lower:

        selected_columns = []

        for col in columns:

            if col.lower() in question_lower:

                selected_columns.append(col)

        if len(selected_columns) >= 2:

            return f"""
SELECT
    {selected_columns[0]},
    {selected_columns[1]}
FROM sales_data
LIMIT 1000
""".strip()

    # -------------------------
    # TOP QUERY
    # Example:
    # Top region
    # -------------------------
    if "top" in question_lower:

        category_col = None

        for col in columns:

            if col.lower() in question_lower:

                category_col = col
                break

        if category_col:

            return f"""
SELECT
    {category_col},
    COUNT(*) AS total_count
FROM sales_data
GROUP BY {category_col}
ORDER BY total_count DESC
LIMIT 10
""".strip()

    # -------------------------
    # HIGHEST QUERY
    # Example:
    # Highest sales_amount
    # -------------------------
    if "highest" in question_lower:

        numeric_col = None

        for col in columns:

            if (
                col.lower()
                in question_lower
            ):

                if col in numeric_columns:
                    numeric_col = col
                    break

        if numeric_col:

            return f"""
SELECT
    MAX({numeric_col}) AS highest_{numeric_col}
FROM sales_data
""".strip()

    # -------------------------
    # FALLBACK TO LLM
    # -------------------------
    prompt = f"""
You are an expert SQLite SQL generator.

DATABASE SCHEMA:
{schema}

USER QUESTION:
{question}

IMPORTANT RULES:
- Use ONLY schema columns
- Never invent columns
- Use SQLite syntax
- Return ONLY SQL
- No markdown
- Table name = sales_data
- Only SELECT queries
- Prefer visualization-friendly queries
- Use GROUP BY when appropriate
- Use aliases

Return SQL only.
"""

    response = llm.invoke(prompt)

    sql = response.content.strip()

    sql = (
        sql
        .replace("```sql", "")
        .replace("```", "")
        .strip()
    )

    return sql


# -------------------------------
# STEP 8: FIX FAILED SQL
# -------------------------------
def fix_sql_query(
    llm,
    question,
    bad_sql,
    error_message,
    schema
):

    prompt = f"""
You are an expert SQLite SQL fixer.

USER QUESTION:
{question}

FAILED SQL:
{bad_sql}

ERROR:
{error_message}

DATABASE SCHEMA:
{schema}

IMPORTANT RULES:
- Use ONLY schema columns
- Never invent columns
- Use SQLite syntax
- Return ONLY corrected SQL
- Only SELECT queries allowed
- Prefer visualization-friendly SQL

Return ONLY corrected SQL.
"""

    response = llm.invoke(prompt)

    fixed_sql = response.content.strip()

    fixed_sql = (
        fixed_sql
        .replace("```sql", "")
        .replace("```", "")
        .strip()
    )

    return fixed_sql