from utils.db import *
from utils.llm import *
from utils.sql_generator import *
from utils.validator import *
import streamlit as st
import pandas as pd
import sqlite3
import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq
import plotly.express as px
from datetime import datetime


# -------------------------------
# LOAD ENV VARIABLES
# -------------------------------
load_dotenv()

# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(
    page_title="AI SQL Data Analyst",
    page_icon="📊",
    layout="wide"
)

# -------------------------------
# SESSION STATE
# -------------------------------
if "query_history" not in st.session_state:
    st.session_state.query_history = []

# -------------------------------
# LOAD LLM
# -------------------------------
def load_llm():

    return ChatGroq(
        temperature=0,
        model_name="llama-3.1-8b-instant",
        api_key=os.getenv("GROQ_API_KEY")
    )

# -------------------------------
# CLEAN COLUMN NAMES
# -------------------------------
def clean_column_names(df):

    df.columns = (
        df.columns
        .str.lower()
        .str.strip()
        .str.replace(" ", "_")
        .str.replace("-", "_")
        .str.replace("/", "_")
    )

    return df

# -------------------------------
# DETECT DATE COLUMNS
# -------------------------------
def detect_date_columns(df):

    for column in df.columns:

        try:

            if "date" in column.lower():

                df[column] = pd.to_datetime(
                    df[column],
                    errors="coerce"
                )

        except:
            pass

    return df

# -------------------------------
# GET DATABASE SCHEMA
# -------------------------------
def get_schema(df):

    schema = []

    for column, dtype in zip(df.columns, df.dtypes):

        schema.append(
            f"{column} ({dtype})"
        )

    return "\n".join(schema)

# -------------------------------
# GENERATE SUGGESTED QUESTIONS
# -------------------------------
def generate_suggested_questions(df):

    questions = []

    columns = df.columns.tolist()

    # Numeric columns
    numeric_cols = df.select_dtypes(
        include=["number"]
    ).columns.tolist()

    # Text/date columns
    categorical_cols = []

    for col in columns:

        if col not in numeric_cols:
            categorical_cols.append(col)

    # Remove weak columns
    ignore_words = [
        "id",
        "index",
        "code",
        "phone",
        "zip"
    ]

    numeric_cols = [
        col for col in numeric_cols
        if not any(
            word in col.lower()
            for word in ignore_words
        )
    ]

    categorical_cols = [
        col for col in categorical_cols
        if not any(
            word in col.lower()
            for word in ignore_words
        )
    ]

    # Detect date-like columns
    date_cols = []

    for col in columns:

        if any(
            word in col.lower()
            for word in [
                "date",
                "time",
                "year"
            ]
        ):
            date_cols.append(col)

    # -------------------------
    # QUESTION 1
    # Average by category
    # -------------------------
    if numeric_cols and categorical_cols:

        questions.append(
            f"Average {numeric_cols[0]} by {categorical_cols[0]}"
        )

    # -------------------------
    # QUESTION 2
    # Trend over date
    # -------------------------
    if numeric_cols:

        if date_cols:

            questions.append(
                f"Trend of {numeric_cols[0]} over {date_cols[0]}"
            )

        else:

            questions.append(
                f"Count by {categorical_cols[0]}"
            )

    # -------------------------
    # QUESTION 3
    # Count by category
    # -------------------------
    if categorical_cols:

        category_col = categorical_cols[0]

        # Avoid using date for count
        for col in categorical_cols:

            if col not in date_cols:

                category_col = col
                break

        questions.append(
            f"Count by {category_col}"
        )

    # Remove duplicates
    questions = list(
        dict.fromkeys(questions)
    )

    # Guarantee 3 questions
    while len(questions) < 3:

        questions.append(
            f"Show {columns[len(questions)]}"
        )

    return questions[:3]



# -------------------------------
# VALIDATE SQL
# -------------------------------
def validate_sql(sql):

    dangerous_keywords = [
        "DROP",
        "DELETE",
        "UPDATE",
        "INSERT",
        "ALTER",
        "TRUNCATE"
    ]

    sql_upper = sql.upper()

    for keyword in dangerous_keywords:

        if keyword in sql_upper:

            raise Exception(
                f"Dangerous SQL detected: {keyword}"
            )

# -------------------------------
# GENERATE SQL QUERY
# -------------------------------

# -------------------------------
# FIX SQL QUERY
# -------------------------------


# -------------------------------
# GENERATE AI INSIGHTS
# -------------------------------
def generate_insights(
    llm,
    question,
    result_df
):

    sample_data = result_df.head(
        20
    ).to_string(index=False)

    prompt = f"""
You are a professional data analyst.

USER QUESTION:
{question}

QUERY RESULT:
{sample_data}

RULES:
- ONLY use provided data
- Never hallucinate
- Keep response concise
- Avoid repetition
- Focus on useful business insights
- Do not say "insufficient evidence" unless absolutely necessary

Return in this format:

Key Findings:
- 2 to 3 short bullet points

Important Observations:
- 2 short bullet points

Insights:
- 2 useful insights from the data
"""

    response = llm.invoke(prompt)

    return response.content
def explain_sql(
    llm,
    sql
):

    prompt = f"""
You are a SQL expert.

Explain this SQL query in simple English.

SQL QUERY:
{sql}

RULES:
- Keep explanation short
- 2–3 sentences only
- Explain what data is being analyzed
- Explain what result user gets
"""

    response = llm.invoke(prompt)

    return response.content
# -------------------------------
# RUN SQL QUERY
# -------------------------------
def run_query(sql):

    conn = sqlite3.connect(
        "database/sales.db"
    )

    result = pd.read_sql_query(
        sql,
        conn
    )

    conn.close()

    return result

# -------------------------------
# GENERATE CHART
# -------------------------------
def generate_chart(result):

    if result.empty:
        return None

    # Must have at least 2 columns
    if result.shape[1] < 2:
        return None

    cols = result.columns.tolist()

    # -------------------------
    # Detect numeric columns
    # -------------------------
    numeric_cols = result.select_dtypes(
        include=["number"]
    ).columns.tolist()

    # -------------------------
    # Detect categorical columns
    # -------------------------
    categorical_cols = result.select_dtypes(
        exclude=["number"]
    ).columns.tolist()

    # No numeric data
    if not numeric_cols:
        return None

    # -------------------------
    # Auto select x and y
    # -------------------------
    x_col = cols[0]
    y_col = numeric_cols[0]

    # Avoid same x and y
    if (
        x_col == y_col
        and len(numeric_cols) > 1
    ):
        y_col = numeric_cols[1]

    # -------------------------
    # CASE 1: DATE/TIME
    # → LINE CHART
    # -------------------------
    if any(
        keyword in x_col.lower()
        for keyword in [
            "date",
            "time",
            "year",
            "month"
        ]
    ):

        fig = px.line(
            result,
            x=x_col,
            y=y_col,
            markers=True,
            title=f"{y_col} over {x_col}"
        )

    # -------------------------
    # CASE 2: NUMERIC VS NUMERIC
    # → SCATTER PLOT
    # -------------------------
    elif (
        len(numeric_cols) >= 2
        and x_col in numeric_cols
    ):

        fig = px.scatter(
            result,
            x=numeric_cols[0],
            y=numeric_cols[1],
            title=f"{numeric_cols[1]} vs {numeric_cols[0]}"
        )

    # -------------------------
    # CASE 3: CATEGORY + NUMBER
    # → PIE OR BAR
    # -------------------------
    elif x_col in categorical_cols:

        unique_values = (
            result[x_col]
            .nunique()
        )

        # 2–3 categories → PIE
        if unique_values <= 3:

            fig = px.pie(
                result,
                names=x_col,
                values=y_col,
                title=f"{y_col} distribution by {x_col}"
            )

        # 4–20 categories → BAR
        elif unique_values <= 20:

            fig = px.bar(
                result,
                x=x_col,
                y=y_col,
                title=f"{y_col} by {x_col}"
            )

        # Too many categories
        # → Horizontal bar
        else:

            top_result = result.head(20)

            fig = px.bar(
                top_result,
                x=y_col,
                y=x_col,
                orientation="h",
                title=f"Top 20 {x_col}"
            )

    # -------------------------
    # FALLBACK
    # -------------------------
    else:

        fig = px.bar(
            result,
            x=x_col,
            y=y_col,
            title="Data Visualization"
        )

    return fig


# -------------------------------
# SIDEBAR
# -------------------------------
st.sidebar.title(
    "📌 AI SQL Data Analyst"
)

st.sidebar.markdown("""
### Features
- Universal CSV Support
- AI SQL Generation
- SQL Validation
- SQL Auto Fix
- Interactive Charts
- AI Insights
- Query History
- CSV Download

### Tech Stack
- Streamlit
- LangChain
- Groq Llama 3
- SQLite
- Plotly
""")

# -------------------------------
# QUERY HISTORY
# -------------------------------
st.sidebar.subheader(
    "🕘 Recent Queries"
)

if st.session_state.query_history:

    for item in reversed(
        st.session_state.query_history[-5:]
    ):

        st.sidebar.markdown(
            f"**Q:** {item['question']}"
        )

else:

    st.sidebar.write(
        "No queries yet."
    )

# -------------------------------
# MAIN TITLE
# -------------------------------
st.title(
    "📊 AI SQL Data Analyst Agent"
)

st.markdown("""
Upload any CSV dataset and ask questions in natural language.

The AI will:
- Understand your dataset
- Generate SQL queries
- Execute queries
- Create visualizations
- Generate insights
""")

# -------------------------------
# FILE UPLOADER
# -------------------------------
uploaded_file = st.file_uploader(
    "📁 Upload CSV File",
    type=["csv"]
)

# -------------------------------
# PROCESS CSV
# -------------------------------
if uploaded_file:

    try:

        # Read CSV
        df = pd.read_csv(
            uploaded_file
        )

        # Clean columns
        df = clean_column_names(df)

        # Detect dates
        df = detect_date_columns(df)

        # Generate schema
        schema = get_schema(df)

        # Save to SQLite
        conn = sqlite3.connect(
            "database/sales.db"
        )

        df.to_sql(
            "sales_data",
            conn,
            if_exists="replace",
            index=False
        )

        conn.close()

        st.success(
            "✅ Data loaded successfully!"
        )

        # -------------------------------
        # DATASET SUMMARY
        # -------------------------------
        st.subheader(
            "📊 Dataset Summary"
        )

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Rows",
                df.shape[0]
            )

        with col2:
            st.metric(
                "Columns",
                df.shape[1]
            )

        with col3:
            st.metric(
                "Missing Values",
                int(df.isnull().sum().sum())
            )

        with col4:
            st.metric(
                "Duplicate Rows",
                int(df.duplicated().sum())
            )

        # -------------------------------
        # DATA PREVIEW
        # -------------------------------
        st.subheader(
            "📄 Data Preview"
        )

        st.dataframe(
            df.head()
        )

        # -------------------------------
        # SCHEMA
        # -------------------------------
        with st.expander(
            "📚 Dataset Schema"
        ):

            st.code(schema)

        # -------------------------------
        # SUGGESTED QUESTIONS
        # -------------------------------
        st.subheader(
             "💡 Suggested Questions"
        )

        suggestions = generate_suggested_questions(df)

        selected_question = None

# Always show all questions
        for i, suggestion in enumerate(suggestions):

           if st.button(
              suggestion,
              key=f"suggestion_{i}"
           ):
              selected_question = suggestion


# Chat input
        manual_question = st.chat_input(
        "Ask questions about your data..."
        )

# Pick selected or manual
        question = (
        selected_question
    if selected_question
    else manual_question
)
        
        # -------------------------------
        # PROCESS QUESTION
        # -------------------------------
        if question:
            with st.chat_message("user"):
                st.write(question)

            with st.spinner(
                "Generating SQL and analyzing data..."
            ):

                try:

                    # Load LLM
                    llm = load_llm()

                    # Generate SQL
                    sql = generate_sql_query(
                        llm,
                        question,
                        schema
                    )

                    # Validate SQL
                    validate_sql(sql)

                    # Save query history
                    st.session_state.query_history.append({
                        "question": question,
                        "sql": sql
                    })

                    # -------------------------------
                    # SHOW SQL
                    # -------------------------------
                    with st.chat_message("assistant"):
                        
                     st.subheader(
                        "🛠 Generated SQL"
                    )

                    st.code(
                        sql,
                        language="sql"
                    )

                    st.subheader(
                       "🧾 Query Explanation"
                    )

                    sql_explanation = explain_sql(
                        llm,
                         sql
                    )

                    st.info(
                       sql_explanation
                    )

                    # -------------------------------
                    # RUN QUERY
                    # -------------------------------
                    try:

                        result = run_query(sql)

                    except Exception as sql_error:

                        st.warning(
                            "⚠ SQL failed. Attempting auto-fix..."
                        )

                        fixed_sql = fix_sql_query(
                            llm,
                            question,
                            sql,
                            str(sql_error),
                            schema
                        )

                        st.subheader(
                            "🔧 Fixed SQL"
                        )

                        st.code(
                            fixed_sql,
                            language="sql"
                        )

                        result = run_query(
                            fixed_sql
                        )

                    # -------------------------------
                    # EMPTY RESULT CHECK
                    # -------------------------------
                    if result.empty:

                        st.warning(
                            "No data found for this query."
                        )

                    else:

                        # -------------------------------
                        # SHOW RESULT
                        # -------------------------------
                        st.subheader(
                            "📊 Query Result"
                        )

                        st.dataframe(
                            result
                        )

                        # -------------------------------
                        # KPI METRICS
                        # -------------------------------
                        if result.shape[1] >= 2:

                            numeric_cols = result.select_dtypes(
                                include=["number"]
                            ).columns.tolist()

                            if numeric_cols:

                                metric_col = numeric_cols[0]

                                col1, col2, col3 = st.columns(3)

                                with col1:
                                    st.metric(
                                        "Rows Returned",
                                        len(result)
                                    )

                                with col2:
                                    st.metric(
                                        "Maximum Value",
                                        round(
                                            result[
                                                metric_col
                                            ].max(),
                                            2
                                        )
                                    )

                                with col3:
                                    st.metric(
                                        "Average Value",
                                        round(
                                            result[
                                                metric_col
                                            ].mean(),
                                            2
                                        )
                                    )

                        # -------------------------------
                        # VISUALIZATION
                        # -------------------------------
                        fig = generate_chart(result)

                        if fig:

                            st.subheader(
                                "📈 Visualization"
                            )

                            st.plotly_chart(
                                fig,
                                use_container_width=True
                            )

                        # -------------------------------
                        # AI INSIGHTS
                        # -------------------------------
                        st.subheader(
                            "🧠 AI Insights"
                        )

                        insights = generate_insights(
                            llm,
                            question,
                            result
                        )

                        st.write(
                            insights
                        )

                        # -------------------------------
# DOWNLOAD REPORT
# -------------------------------
                        rows_returned = len(result)

                        numeric_cols = result.select_dtypes(
                            include=["number"]
                        ).columns.tolist()

                        average_value = "N/A"

                        if numeric_cols:

                         average_value = round(
                            result[
                               numeric_cols[0]
                            ].mean(),
                            2
                        )

# Timestamp for filename
                        # -------------------------------
# DOWNLOAD REPORT
# -------------------------------

# File name date
                        timestamp = datetime.now().strftime(
                        "%Y-%m-%d"
                        )

                        file_name = (
                        f"query_result_"
                        f"{timestamp}.csv"
                        )

# Clean date columns
                        for col in result.columns:

                          if "date" in col.lower():
                              try:
                                  result[col] = (
                                  result[col]
                                  .astype(str)
                                  .str[:10]
                                  )
                              except:
                                pass


# Round numeric columns
                        numeric_cols = result.select_dtypes(
                        include=["number"]
                        ).columns

                        result[numeric_cols] = result[
                        numeric_cols
                        ].round(2)


# Create professional report
                        generated_report = f""" ══════════════════════════════════════════════════════ 
              AI SQL DATA ANALYST REPORT                               
 ══════════════════════════════════════════════════════

📅 Report Date:
{timestamp}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📌 USER QUESTION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{question}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🛠 GENERATED SQL QUERY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{sql}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 QUERY SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Rows Returned: {rows_returned}
• Average Value: {average_value}
• Total Columns: {len(result.columns)}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📁 QUERY RESULT DATA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""

# Add query result
                        # Show only first 20 rows

                        generated_report += result.to_csv(
                           index=False
                        )

# Mention omitted rows
                        

# Footer
                        generated_report += """

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Report generated successfully using
AI SQL Data Analyst Agent
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""


# Download button
                        st.download_button(
    label="⬇ Download Results CSV",
    data=generated_report,
    file_name=file_name,
    mime="text/csv"
)

                        
                except Exception as query_error:

                    st.error(
                         "❌ Unable to process this query. Please try another question."
                    )

    except Exception as file_error:

        st.error(
            f"❌ File Error: {file_error}"
        )