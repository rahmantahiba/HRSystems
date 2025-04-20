import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk
import pandas as pd
import pathlib

# Set database file path
database_file = pathlib.Path("employee_performance.db")

grades_data = [
    {"Grade": "112A", "Minimum": 32240, "Midpoint": 34600, "Maximum": 43700},
    {"Grade": "113A", "Minimum": 32240, "Midpoint": 38000, "Maximum": 48000},
    {"Grade": "114A", "Minimum": 32800, "Midpoint": 41900, "Maximum": 52500},
    {"Grade": "115A", "Minimum": 34400, "Midpoint": 45900, "Maximum": 57600},
    {"Grade": "116A", "Minimum": 38000, "Midpoint": 50600, "Maximum": 63700},
    {"Grade": "117A", "Minimum": 41600, "Midpoint": 55500, "Maximum": 69700},
]
grades_df = pd.DataFrame(grades_data).set_index("Grade")
score_increase = {1: 0.00, 2: 0.01, 3: 0.02, 4: 0.025, 5: 0.03}

# --- Database Logic ---
def create_database():
    conn = sqlite3.connect(database_file)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT,
        last_name TEXT,
        grade TEXT,
        current_salary REAL,
        score_y1 INTEGER,
        score_y2 INTEGER,
        score_y3 INTEGER,
        score_y4 INTEGER,
        score_y5 INTEGER
    )
    """)
    conn.commit()
    conn.close()

def insert_employee(first, last, grade, salary, scores):
    conn = sqlite3.connect(database_file)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO employees (first_name, last_name, grade, current_salary, score_y1, score_y2, score_y3, score_y4, score_y5)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (first, last, grade, salary, *scores))
    conn.commit()
    conn.close()

def fetch_employees():
    with sqlite3.connect(database_file) as conn:
        return conn.cursor().execute("SELECT * FROM employees").fetchall()

def delete_employee(emp_id):
    with sqlite3.connect(database_file) as conn:
        conn.cursor().execute("DELETE FROM employees WHERE id = ?", (emp_id,))

# --- CSV Import/Export ---
def export_to_csv():
    employees = fetch_employees()
    df = pd.DataFrame(employees, columns=[
        "ID", "First Name", "Last Name", "Grade", "Salary", "Y1", "Y2", "Y3", "Y4", "Y5"
    ])
    try:
        df.to_csv("employee_export.csv", index=False)
        messagebox.showinfo("Export", "Data exported to employee_export.csv")
    except Exception as e:
        messagebox.showerror("Export Failed", str(e))

def import_from_csv():
    try:
        df = pd.read_csv("employee_export.csv")
        for _, row in df.iterrows():
            insert_employee(
                row["First Name"],
                row["Last Name"],
                row["Grade"],
                row["Salary"],
                [row["Y1"], row["Y2"], row["Y3"], row["Y4"], row["Y5"]]
            )
        messagebox.showinfo("Import", "Data imported successfully.")
        display_records()
    except Exception as e:
        messagebox.showerror("Import Failed", str(e))

# --- Core Functions ---
def display_records():
    tree.delete(*tree.get_children())
    for emp in fetch_employees():
        emp_id, first, last, grade, salary, y1, y2, y3, y4, y5 = emp
        full_name = f"{first} {last}"
        max_salary = grades_df.loc[grade]["Maximum"]
        sal = salary
        exceeded = None
        for i, score in enumerate([y1, y2, y3, y4, y5]):
            sal *= (1 + score_increase.get(score, 0.02))
            sal = round(sal, 2)
            if exceeded is None and sal > max_salary:
                exceeded = i + 1
        flag = "⚠ Exceeded Band" if exceeded else "✓ Within Band"
        tree.insert("", tk.END, values=(emp_id, full_name, grade, salary, y1, y2, y3, y4, y5, max_salary, exceeded or "—", flag))

def delete_selected_employee():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Select", "Please select a row.")
        return
    emp_id = tree.item(selected[0])['values'][0]
    delete_employee(emp_id)
    display_records()
    messagebox.showinfo("Deleted", f"Employee ID {emp_id} removed.")

def show_salary_budget():
    selected = tree.selection()
    if selected:
        values = tree.item(selected[0])["values"]
        salary = float(values[3])
        scores = list(map(int, values[4:9]))
        total = salary
        for s in scores:
            total *= (1 + score_increase.get(s, 0.02))
            total = round(total, 2)
        messagebox.showinfo("Budget", f"{values[1]}: ${total:,.2f} (5-Year)")
    else:
        totals = [0]*5
        for emp in fetch_employees():
            salary = emp[4]
            for i, s in enumerate(emp[5:10]):
                salary *= (1 + score_increase.get(s, 0.02))
                salary = round(salary, 2)
                totals[i] += salary
        lines = "\n".join([f"Year {i+1}: ${t:,.2f}" for i, t in enumerate(totals)])
        messagebox.showinfo("Combined Budget", lines)

def submit_form():
    first = first_name_entry.get().strip()
    last = last_name_entry.get().strip()
    grade = grade_entry.get().strip().upper()
    try:
        salary = float(salary_entry.get())
        scores = [int(s.get()) for s in score_entries]
        if any(s not in score_increase for s in scores):
            raise ValueError
    except:
        messagebox.showerror("Error", "Invalid input.")
        return
    insert_employee(first, last, grade, salary, scores)
    for e in [first_name_entry, last_name_entry, grade_entry, salary_entry] + score_entries:
        e.delete(0, tk.END)
    display_records()

# --- GUI ---
create_database()
root = tk.Tk()
root.title("Employee Performance Database")

tk.Label(root, text="First Name").grid(row=0, column=0)
tk.Label(root, text="Last Name").grid(row=1, column=0)
tk.Label(root, text="Grade").grid(row=2, column=0)
tk.Label(root, text="Salary").grid(row=3, column=0)
tk.Label(root, text="Scores (Y1-Y5)").grid(row=4, column=0)

first_name_entry = tk.Entry(root)
last_name_entry = tk.Entry(root)
grade_entry = tk.Entry(root)
salary_entry = tk.Entry(root)
score_entries = [tk.Entry(root, width=4) for _ in range(5)]

first_name_entry.grid(row=0, column=1)
last_name_entry.grid(row=1, column=1)
grade_entry.grid(row=2, column=1)
salary_entry.grid(row=3, column=1)
for i, entry in enumerate(score_entries):
    entry.grid(row=4, column=i+1)

# Buttons
tk.Button(root, text="Add Employee", command=submit_form).grid(row=5, column=0)
tk.Button(root, text="Show Budget", command=show_salary_budget).grid(row=5, column=1)
tk.Button(root, text="Delete Selected", command=delete_selected_employee).grid(row=5, column=2)
tk.Button(root, text="Import CSV", command=import_from_csv).grid(row=5, column=3)
tk.Button(root, text="Export CSV", command=export_to_csv).grid(row=5, column=4)

# Treeview
cols = ("ID", "Name", "Grade", "Salary", "Y1", "Y2", "Y3", "Y4", "Y5", "Max Band", "Exceeded Year", "Flag")
tree = ttk.Treeview(root, columns=cols, show="headings")
for col in cols:
    tree.heading(col, text=col)
    tree.column(col, width=100, anchor="center")
tree.grid(row=6, column=0, columnspan=6, pady=10)

display_records()
root.mainloop()
