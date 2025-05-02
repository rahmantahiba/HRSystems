import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk
import pandas as pd
import pathlib

# Set database file path
database_file = pathlib.Path("employee_performance.db")

# Grade band definitions
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

# --- Database Functions ---

def create_database():
    conn = sqlite3.connect(database_file)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        grade TEXT NOT NULL,
        current_salary REAL NOT NULL,
        score_y1 INTEGER,
        score_y2 INTEGER,
        score_y3 INTEGER,
        score_y4 INTEGER,
        score_y5 INTEGER,
        UNIQUE(name, grade)
    )
    """)
    conn.commit()
    conn.close()

def insert_employee(name, grade, salary, scores):
    conn = sqlite3.connect(database_file)
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO employees (name, grade, current_salary, score_y1, score_y2, score_y3, score_y4, score_y5)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, grade, salary, *scores))
        conn.commit()
    finally:
        conn.close()

def fetch_employees():
    conn = sqlite3.connect(database_file)
    cur = conn.cursor()
    cur.execute("SELECT * FROM employees")
    rows = cur.fetchall()
    conn.close()
    return rows

# --- Data Processing ---

def evaluate_employees():
    employees = fetch_employees()
    results = []

    for emp in employees:
        emp_id, name, grade, salary, *scores = emp
        max_salary = grades_df.loc[grade]["Maximum"]
        exceeded_year = None
        progression = []

        for year, score in enumerate(scores, start=1):
            raise_pct = score_increase.get(score, 0.02)
            salary *= (1 + raise_pct)
            salary = round(salary, 2)
            progression.append(salary)
            if exceeded_year is None and salary > max_salary:
                exceeded_year = year

        projected_salary = emp[3]
        projected_exceed_year = None
        for year in range(1, 6):
            projected_salary *= (1 + score_increase[3])
            projected_salary = round(projected_salary, 2)
            if projected_exceed_year is None and projected_salary > max_salary:
                projected_exceed_year = year
                break

        results.append((name, grade, *progression, exceeded_year if exceeded_year else "Within Range", projected_exceed_year if projected_exceed_year else "Never"))

    return results

def calculate_combined_budget():
    employees = fetch_employees()
    yearly_totals = [0] * 5
    for emp in employees:
        salary = emp[3]
        scores = emp[4:9]
        for i, score in enumerate(scores):
            raise_pct = score_increase.get(score, 0.02)
            salary *= (1 + raise_pct)
            salary = round(salary, 2)
            yearly_totals[i] += salary
    return yearly_totals

# --- CSV I/O ---

def export_to_csv():
    employees = fetch_employees()
    df = pd.DataFrame(employees, columns=["ID", "Name", "Grade", "Salary", "Y1", "Y2", "Y3", "Y4", "Y5"])
    try:
        df.to_csv("employee_export.csv", index=False)
        messagebox.showinfo("Export Successful", "Data exported to 'employee_export.csv'")
    except Exception as e:
        messagebox.showerror("Export Failed", str(e))

def import_from_csv():
    try:
        df = pd.read_csv("employee_export.csv")
        added = 0
        skipped = 0
        existing = {(emp[1].strip().lower(), emp[2].strip().upper()) for emp in fetch_employees()}

        for _, row in df.iterrows():
            key = (row["Name"].strip().lower(), row["Grade"].strip().upper())
            if key in existing:
                skipped += 1
                continue

            insert_employee(
                row["Name"],
                row["Grade"],
                row["Salary"],
                [row["Y1"], row["Y2"], row["Y3"], row["Y4"], row["Y5"]]
            )
            added += 1
            existing.add(key)  # So future rows in the same CSV aren't inserted twice

        display_records()
        messagebox.showinfo("Import Complete", f"Added: {added} entries\nSkipped: {skipped} duplicates.")
    except Exception as e:
        messagebox.showerror("Import Failed", str(e))

# --- UI Functions ---

def show_salary_budget():
    selected = tree.selection()

    if selected:
        # Show total for selected employee
        emp = tree.item(selected[0])['values']
        name = emp[1]
        salary = float(emp[3])
        scores = list(map(int, emp[4:9]))  # Y1-Y5 scores

        total = salary
        for score in scores:
            raise_pct = score_increase.get(score, 0.02)
            total *= (1 + raise_pct)
            total = round(total, 2)

        message = f"Projected 5-Year Total Salary for {name}:\n${total:,.2f}"
        messagebox.showinfo("Employee Salary Projection", message)

    else:
        # Fallback to show total for all employees
        totals = calculate_combined_budget()
        message = "Combined Salary Budget (All Employees):\n"
        message += "\n".join([f"Year {i + 1}: ${totals[i]:,.2f}" for i in range(5)])
        messagebox.showinfo("Combined Budget Forecast", message)

def delete_selected_employee():
    selected_items = tree.selection()
    if not selected_items:
        messagebox.showwarning("No Selection", "Please select one or more rows to delete.")
        return

    confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {len(selected_items)} selected record(s)?")
    if not confirm:
        return

    conn = sqlite3.connect(database_file)
    cur = conn.cursor()
    for item in selected_items:
        emp_id = tree.item(item)['values'][0]
        cur.execute("DELETE FROM employees WHERE id = ?", (emp_id,))
    conn.commit()
    conn.close()
    display_records()
    messagebox.showinfo("Deleted", f"{len(selected_items)} record(s) deleted.")

def submit_form():
    name = name_entry.get()
    grade = grade_entry.get().strip().upper()

    employees = fetch_employees()
    for emp in employees:
        if emp[1].strip().lower() == name.strip().lower() and emp[2].strip().upper() == grade:
            messagebox.showerror("Duplicate Entry", f"Employee '{name}' with Grade '{grade}' already exists.")
            return

    if grade not in grades_df.index:
        messagebox.showerror("Invalid Grade", f"Grade '{grade}' is not recognized.\nValid options: {', '.join(grades_df.index)}")
        return

    try:
        salary = float(salary_entry.get())
        scores = [int(entry.get()) for entry in score_entries]
        if any(score not in score_increase for score in scores):
            raise ValueError("Scores must be between 1 and 5.")
    except ValueError as e:
        messagebox.showerror("Invalid Input", str(e))
        return

    try:
        insert_employee(name, grade, salary, scores)
        messagebox.showinfo("Success", f"Record for {name} added!")
        for entry in [name_entry, grade_entry, salary_entry] + score_entries:
            entry.delete(0, tk.END)
        display_records()
    except sqlite3.IntegrityError:
        messagebox.showerror("Database Error", f"Employee '{name}' with Grade '{grade}' already exists.")

def display_records():
    for row in tree.get_children():
        tree.delete(row)

    for emp in fetch_employees():
        emp_id, name, grade, salary, y1, y2, y3, y4, y5 = emp
        max_salary = grades_df.loc[grade]["Maximum"]
        sal = salary
        exceeded_year = None

        for i, score in enumerate([y1, y2, y3, y4, y5], start=1):
            raise_pct = score_increase.get(score, 0.02)
            sal *= (1 + raise_pct)
            sal = round(sal, 2)
            if exceeded_year is None and sal > max_salary:
                exceeded_year = i

        flag = "✓ Within Band"
        if exceeded_year:
            flag = "⚠ Exceeded Band"
        elif round(sal, 2) == max_salary:
            flag = "⚠ At Band Limit"

        tag = "exceeded" if flag != "✓ Within Band" else "normal"

        tree.insert("", tk.END, values=(
            emp_id, name, grade, salary, y1, y2, y3, y4, y5,
            max_salary, exceeded_year if exceeded_year else "—", flag
        ), tags=(tag,))

    tree.tag_configure("exceeded", background="#ffe6e6")
    tree.tag_configure("normal", background="#e6ffe6")

def search_employees(query):
    for row in tree.get_children():
        tree.delete(row)

    for emp in fetch_employees():
        emp_id, name, grade, salary, y1, y2, y3, y4, y5 = emp
        if query.lower() not in name.lower():
            continue

        max_salary = grades_df.loc[grade]["Maximum"]
        sal = salary
        exceeded_year = None

        for i, score in enumerate([y1, y2, y3, y4, y5], start=1):
            raise_pct = score_increase.get(score, 0.02)
            sal *= (1 + raise_pct)
            sal = round(sal, 2)
            if exceeded_year is None and sal > max_salary:
                exceeded_year = i

        flag = "✓ Within Band"
        if exceeded_year:
            flag = "⚠ Exceeded Band"
        elif round(sal, 2) == max_salary:
            flag = "⚠ At Band Limit"

        tag = "exceeded" if flag != "✓ Within Band" else "normal"

        tree.insert("", tk.END, values=(
            emp_id, name, grade, salary, y1, y2, y3, y4, y5,
            max_salary, exceeded_year if exceeded_year else "—", flag
        ), tags=(tag,))

    tree.tag_configure("exceeded", background="#ffe6e6")
    tree.tag_configure("normal", background="#e6ffe6")

def show_evaluations():
    eval_win = tk.Toplevel(root)
    eval_win.title("Salary Projections")
    cols = ("Name", "Grade", "Y1", "Y2", "Y3", "Y4", "Y5", "Exceeded Year", "Min Score 3 Exceed Year")
    eval_tree = ttk.Treeview(eval_win, columns=cols, show='headings')
    for col in cols:
        eval_tree.heading(col, text=col)
    eval_tree.pack(fill='both', expand=True)

    for row in evaluate_employees():
        eval_tree.insert("", tk.END, values=row)

# --- Build UI ---

create_database()
root = tk.Tk()
root.title("Employee Performance Database")
root.geometry("1000x650")          # Initial size
root.minsize(900, 600)             # Minimum size to ensure layout fits on smaller screens

form_frame = tk.Frame(root)
form_frame.grid(row=0, column=0, columnspan=10, sticky="w", padx=10, pady=5)

tk.Label(form_frame, text="Name").grid(row=0, column=0, sticky="w")
name_entry = tk.Entry(form_frame)
name_entry.grid(row=0, column=1, padx=5)

tk.Label(form_frame, text="Grade").grid(row=1, column=0, sticky="w")
grade_entry = tk.Entry(form_frame)
grade_entry.grid(row=1, column=1, padx=5)

tk.Label(form_frame, text="Current Salary").grid(row=2, column=0, sticky="w")
salary_entry = tk.Entry(form_frame)
salary_entry.grid(row=2, column=1, padx=5)

tk.Label(form_frame, text="Scores (Y1–Y5)").grid(row=3, column=0, sticky="w")

scores_frame = tk.Frame(form_frame)
scores_frame.grid(row=3, column=1, sticky="w", padx=(5, 0))  # << Add this padx

score_entries = [tk.Entry(scores_frame, width=4) for _ in range(5)]
for i, entry in enumerate(score_entries):
    entry.grid(row=0, column=i, padx=4)

# Create a centered button frame
button_frame = tk.Frame(root)
button_frame.grid(row=4, column=0, columnspan=10, pady=10)

submit_btn = tk.Button(button_frame, text="Add Employee", command=submit_form)
submit_btn.pack(side=tk.LEFT, padx=10)

eval_btn = tk.Button(button_frame, text="Show Salary Projections", command=show_evaluations)
eval_btn.pack(side=tk.LEFT, padx=10)

budget_btn = tk.Button(button_frame, text="Show Combined Budget", command=show_salary_budget)
budget_btn.pack(side=tk.LEFT, padx=10)

delete_btn = tk.Button(button_frame, text="Delete Selected", command=delete_selected_employee)
delete_btn.pack(side=tk.LEFT, padx=10)

import_btn = tk.Button(button_frame, text="Import CSV", command=import_from_csv)
import_btn.pack(side=tk.LEFT, padx=10)

export_btn = tk.Button(button_frame, text="Export CSV", command=export_to_csv)
export_btn.pack(side=tk.LEFT, padx=10)

tk.Label(button_frame, text="Search Name:").pack(side=tk.LEFT, padx=5)
search_entry = tk.Entry(button_frame, width=15)
search_entry.pack(side=tk.LEFT, padx=5)

search_btn = tk.Button(button_frame, text="Search", command=lambda: search_employees(search_entry.get()))
search_btn.pack(side=tk.LEFT, padx=5)

cols = ("ID", "Name", "Grade", "Salary", "Y1", "Y2", "Y3", "Y4", "Y5", "Max Band", "Exceeded Year", "Flag")

tree_frame = tk.Frame(root)
tree_frame.grid(row=7, column=0, columnspan=10, pady=10, sticky="nsew")
root.grid_rowconfigure(7, weight=1)
root.grid_columnconfigure(0, weight=1)

x_scroll = tk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
x_scroll.pack(side=tk.BOTTOM, fill=tk.X)

tree = ttk.Treeview(tree_frame, columns=cols, show='headings', xscrollcommand=x_scroll.set, selectmode="extended")
x_scroll.config(command=tree.xview)

for col in cols:
    tree.heading(col, text=col)
    tree.column(col, width=100, anchor='center')

tree.pack(fill='both', expand=True)

display_records()
root.mainloop()