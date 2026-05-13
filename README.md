# 📊 AI SQL Data Analyst Agent

An AI-powered data analysis application that allows users to upload any CSV dataset and interact with it using natural language. The system automatically converts user questions into SQL queries, executes them using SQLite, generates interactive visualizations, provides AI-powered insights, and enables report download.

---
---

## 🚀 Features

✅ Universal CSV Upload Support  
✅ Natural Language to SQL Conversion  
✅ Automatic SQL Query Generation  
✅ SQL Validation and Auto Fix  
✅ Interactive Data Visualizations  
✅ AI-Powered Insights  
✅ Query History  
✅ Downloadable Query Reports  
✅ Supports Multiple CSV Datasets  

---

## 🧠 How It Works

1. Upload any CSV dataset.
2. The system automatically analyzes the dataset schema.
3. Ask questions in natural language.
4. AI converts the question into SQL.
5. SQL query is executed dynamically using SQLite.
6. Results are displayed in tabular form.
7. Charts are generated automatically.
8. AI provides insights based on query results.
9. Reports can be downloaded for analysis.

---

## 📌 Example Questions

### Sales Dataset
- Trend of sales_amount over sale_date
- Average sales_amount by region
- Count by payment_method
- Relationship between unit_price and sales_amount

### Telecom Dataset
- Count by churn
- Average monthlycharges by contract
- Relationship between tenure and monthlycharges

### House Price Dataset
- Trend of square_footage over year_built
- Relationship between square_footage and house_price
- Highest house_price

---

## 📊 Supported Visualizations

- 📈 Line Charts (Trend Analysis)
- 📊 Bar Charts (Category Comparisons)
- 🥧 Pie Charts (Small Category Distribution)
- 📉 Scatter Plots (Relationship Analysis)

---

## 🛠️ Technology Stack

| Component | Technology |
|------------|-------------|
| Frontend | Streamlit |
| Backend | Python |
| Database | SQLite |
| AI Model | Groq Llama 3 |
| Framework | LangChain |
| Visualization | Plotly |
| Data Processing | Pandas |

---

## 📂 Project Structure

```text
AI_SQL_Data_Analyst/
│── streamlit_app.py
│── requirements.txt
│── README.md
│
├── utils/
│   ├── sql_generator.py
│   ├── database.py
│
├── data/
│   └── sales.csv


⚙️ Installation & Setup
Step 1: Open Project Folder

Move to the project directory:

cd ai-sql-agent
Step 2: Create Virtual Environment
python -m venv venv
Step 3: Activate Virtual Environment
Windows (PowerShell)
venv\Scripts\Activate
Windows (CMD)
venv\Scripts\activate.bat
Step 4: Install Required Libraries
pip install -r requirements.txt
Step 5: Run the Application
streamlit run streamlit_app.py

📸 Sample Workflow
Upload a CSV dataset
Ask questions in natural language
AI generates SQL automatically
View results and visualizations
Read AI-generated insights
Download the generated report
🎯 Project Objective

The objective of this project is to simplify data analysis by enabling users to analyze datasets using natural language instead of manually writing SQL queries. This makes data analytics more accessible to both technical and non-technical users.

🔥 Key Highlights
Works with any CSV dataset
No manual SQL writing required
Automatic visualization generation
AI-powered analytical insights
Downloadable analytical reports
Easy-to-use interface
