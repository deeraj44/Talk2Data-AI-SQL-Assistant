# 🧠 Talk2Data (powered by LLaMA 3 + SQLite)

This is a Python-based AI assistant that lets you **query any CSV dataset using plain English**. It automatically converts your natural language question into an accurate SQL query using Groq's **LLaMA 3.3 70B model**, runs the query on a local SQLite database, and returns a human-readable result.

---

## 🚀 Features

- Upload **any CSV file**
- Dynamically creates a **SQLite table**
- Understands your **natural language questions**
- Converts your question into a smart **SQL query using LLaMA**
- Executes the query and returns **formatted, readable results**
- Supports operations like:
  - Average, sum, count
  - Filters, max/min
  - Most common values
  - Multi-column retrieval

---

## 📸 Demo

```bash
📂 Enter path to your CSV file: Employee.csv
✅ CSV 'Employee.csv' loaded into 'database.db' as table 'Employee'

❓ Ask a question about your data: What is the average salary?

🧠 Generated SQL Query:
SELECT AVG(Salary) FROM Employee;

💡 The average is 84500.0.
