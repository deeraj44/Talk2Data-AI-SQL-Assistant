import streamlit as st
import pandas as pd
import sqlite3
import requests
import re
import os
import tempfile

GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

def clean_sql_query(response_text):
    match = re.search(r"SELECT .*?;", response_text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(0).strip()
    return None

def get_column_names(table_name, db_file):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns_info = cursor.fetchall()
    conn.close()
    return [col[1] for col in columns_info]

def query_database_with_llama(user_query, table_name, db_file):
    try:
        column_names = get_column_names(table_name, db_file)
        schema_hint = f"The table '{table_name}' has the following columns: {', '.join(column_names)}."

        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json",
        }

        messages = [
            # {"role": "system", "content": f"You are an SQL expert. Only respond with a valid SQLite query for the table '{table_name}'. {schema_hint}"},
            {"role": "system", "content": f"You are an expert in generating valid SQLite queries. "
            "The user will ask natural language questions about a table named 'data' which can contain any dataset structure. "
            "Only respond with a syntactically correct SQLite query. "
            "If comparing strings (like city or gender), use LOWER() for case-insensitive comparison. "
            "Do not include explanations or extra text — only return the SQL query."},
            {"role": "user", "content": f"Convert this question into an SQLite query: {user_query}"},
        ]

        data = {
            "model": "llama-3.3-70b-versatile",
            "messages": messages,
        }

        response = requests.post(GROQ_API_URL, headers=headers, json=data)
        if response.status_code != 200:
            return None, f"❌ Error: {response.status_code} - {response.json()}"

        sql_query = clean_sql_query(response.json()["choices"][0]["message"]["content"])
        if not sql_query:
            return None, "❌ Error: Could not extract a valid SQL query."

        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        cursor.execute(sql_query)
        result = cursor.fetchall()
        conn.close()

        return sql_query, result

    except Exception as e:
        return None, f"❌ Error: {str(e)}"

def format_result(result):
    if not result:
        return "No results found."
    if len(result) == 1 and len(result[0]) == 1:
        value = result[0][0]
        if isinstance(value, float):
            value = round(value, 2)
        return f"💡 The result is: {value}"
    formatted = []
    for row in result:
        formatted.append("• " + " | ".join(str(item) for item in row))
    return "\n\n".join(formatted)

# STREAMLIT UI
st.set_page_config(page_title="🧠 Natural Language SQL Assistant", layout="centered")
st.title("🧠 Talk2Data: AI SQL Assistant")
st.markdown("Natural Language SQL Assistant")
st.markdown("Query any CSV file using plain English! Powered by **LLaMA 3** and SQLite.")

uploaded_file = st.file_uploader("📂 Upload a CSV file", type=["csv"])

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
        st.success("✅ File uploaded and read successfully!")

        temp_dir = tempfile.TemporaryDirectory()
        db_path = os.path.join(temp_dir.name, "database.db")
        table_name = "data"
        df.to_sql(table_name, sqlite3.connect(db_path), if_exists="replace", index=False)

        st.subheader("🔍 Ask a question about your data:")
        user_query = st.text_input("For example: What is the average age?")

        if user_query:
            with st.spinner("Thinking..."):
                sql, result = query_database_with_llama(user_query, table_name, db_path)

            if sql:
                st.code(sql, language="sql")
                st.markdown(format_result(result))
            else:
                st.error(result)

        with st.expander("📊 Preview Dataset"):
            st.dataframe(df)

    except Exception as e:
        st.error(f"❌ Failed to process file: {e}")
