import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import pathlib
import pandas as pd

# ------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------
# Shared database file used by performance_evaluation.py
DATABASE_FILE = pathlib.Path("employee_performance.db")

# Grade definitions copied from performance_evaluation.py so both
# scripts stay in‑sync. DO NOT edit here without also updating the
# other script.
GRADES_DATA = [
    {"Grade": "112A", "Minimum": 32240, "Midpoint": 34600, "Maximum": 43700},
    {"Grade": "113A", "Minimum": 32240, "Midpoint": 38000, "Maximum": 48000},
    {"Grade": "114A", "Minimum": 32800, "Midpoint": 41900, "Maximum": 52500},
    {"Grade": "115A", "Minimum": 34400, "Midpoint": 45900, "Maximum": 57600},
    {"Grade": "116A", "Minimum": 38000, "Midpoint": 50600, "Maximum": 63700},
    {"Grade": "117A", "Minimum": 41600, "Midpoint": 55500, "Maximum": 69700},
]
GRADES_DF = pd.DataFrame(GRADES_DATA).set_index("Grade")

SCORE_OPTIONS = [1, 2, 3, 4, 5]  # Valid performance scores

# ------------------------------------------------------------------
# Database helpers
# ------------------------------------------------------------------

def init_database():
    """Create the employees table if it doesn't exist."""
    conn = sqlite3.connect(DATABASE_FILE)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            grade TEXT NOT NULL,
            current_salary REAL NOT NULL,
            score_y1 INTEGER,
            score_y2 INTEGER,
            score_y3 INTEGER,
            score_y4 INTEGER,
            score_y5 INTEGER
        )
        """
    )
    conn.commit()
    conn.close()


# ------------------------------------------------------------------
# UI helpers
# ------------------------------------------------------------------

def show_employee_form(parent, tree, employee=None, emp_id=None):
    """Popup to add or edit an employee record."""
    form = tk.Toplevel(parent)
    form.title("Add Employee" if employee is None else "Edit Employee")
    form.geometry("450x450")
    form.resizable(False, False)

    # --------------------------------------------------------------
    # Widgets
    # --------------------------------------------------------------
    ttk.Label(form, text=form.title(), font=("Montserrat", 16, "bold")).pack(pady=10)

    # Name
    ttk.Label(form, text="Name:").pack(anchor="w", padx=20)
    name_entry = ttk.Entry(form)
    name_entry.pack(fill="x", padx=20, pady=4)

    # Grade
    ttk.Label(form, text="Grade:").pack(anchor="w", padx=20)
    grade_combo = ttk.Combobox(form, values=list(GRADES_DF.index), state="readonly")
    grade_combo.pack(fill="x", padx=20, pady=4)

    # Salary
    ttk.Label(form, text="Current Salary ($):").pack(anchor="w", padx=20)
    salary_entry = ttk.Entry(form)
    salary_entry.pack(fill="x", padx=20, pady=4)

    # Yearly Scores
    score_entries = []
    for i in range(1, 6):
        ttk.Label(form, text=f"Performance Score Year {i} (1‑5):").pack(anchor="w", padx=20)
        e = ttk.Combobox(form, values=SCORE_OPTIONS, state="readonly", width=5)
        e.pack(padx=20, pady=2, anchor="w")
        score_entries.append(e)

    # Pre‑fill when editing
    if employee:
        name_entry.insert(0, employee[1])  # name
        grade_combo.set(employee[2])       # grade
        salary_entry.insert(0, str(employee[3]))  # current salary
        for idx, e in enumerate(score_entries, start=4):
            val = employee[idx]
            if val is not None:
                e.set(str(val))

    # --------------------------------------------------------------
    # Save logic
    # --------------------------------------------------------------
    def save_record():
        name = name_entry.get().strip()
        grade = grade_combo.get().strip().upper()
        try:
            salary = float(salary_entry.get())
            if salary <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Input", "Salary must be a positive number.")
            return

        # Validate grade
        if grade not in GRADES_DF.index:
            messagebox.showerror("Invalid Grade", f"Grade must be one of: {', '.join(GRADES_DF.index)}")
            return

        # Collect scores
        scores = []
        for cb in score_entries:
            val = cb.get()
            scores.append(int(val) if val else None)

        conn = sqlite3.connect(DATABASE_FILE)
        cur = conn.cursor()
        if emp_id is None:
            cur.execute(
                """INSERT INTO employees
                       (name, grade, current_salary, score_y1, score_y2, score_y3, score_y4, score_y5)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (name, grade, salary, *scores),
            )
        else:
            cur.execute(
                """UPDATE employees
                       SET name=?, grade=?, current_salary=?, score_y1=?, score_y2=?, score_y3=?, score_y4=?, score_y5=?
                       WHERE id=?""",
                (name, grade, salary, *scores, emp_id),
            )
        conn.commit()
        conn.close()
        load_employees(tree)
        form.destroy()

    ttk.Button(form, text="Save", command=save_record).pack(pady=5)
    ttk.Button(form, text="Cancel", command=form.destroy).pack()


def load_employees(tree):
    """Populate the Treeview with employee records."""
    # Clear
    for item in tree.get_children():
        tree.delete(item)

    conn = sqlite3.connect(DATABASE_FILE)
    cur = conn.cursor()
    cur.execute("SELECT * FROM employees")
    rows = cur.fetchall()
    conn.close()

    for row in rows:
        emp_id, name, grade, salary, y1, y2, y3, y4, y5 = row

        # Simple flag if salary > grade max
        flag = ""
        try:
            if salary > GRADES_DF.loc[grade, "Maximum"]:
                flag = "Exceeds Max"
        except KeyError:
            flag = "Unknown Grade"

        tree.insert(
            "", "end",
            iid=str(emp_id),
            values=(emp_id, name, grade, f"{salary:,.2f}", y1, y2, y3, y4, y5, flag),
            tags=("exceed",) if flag.startswith("Exceeds") else ()
        )

    tree.tag_configure("exceed", background="#ffcccc")


def edit_selected(tree, parent):
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("No Selection", "Select a record first.")
        return
    emp_id = int(selected[0])
    conn = sqlite3.connect(DATABASE_FILE)
    cur = conn.cursor()
    cur.execute("SELECT * FROM employees WHERE id=?", (emp_id,))
    employee = cur.fetchone()
    conn.close()
    if employee:
        show_employee_form(parent, tree, employee, emp_id)


def delete_selected(tree):
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("No Selection", "Select a record first.")
        return
    emp_id = int(selected[0])
    if not messagebox.askyesno("Confirm", f"Delete employee ID {emp_id}? This cannot be undone."):
        return
    conn = sqlite3.connect(DATABASE_FILE)
    cur = conn.cursor()
    cur.execute("DELETE FROM employees WHERE id=?", (emp_id,))
    conn.commit()
    conn.close()
    load_employees(tree)


def show_employee_manager(parent=None):
    """Entry point: open Employee Manager window."""
    init_database()

    win = tk.Toplevel(parent) if parent else tk.Tk()
    win.title("Employee Manager")
    win.geometry("1000x500")

    # Buttons
    btn_frame = ttk.Frame(win)
    btn_frame.pack(fill="x", pady=5)
    ttk.Button(btn_frame, text="Add New", command=lambda: show_employee_form(win, tree)).pack(side="left", padx=5)
    edit_btn = ttk.Button(btn_frame, text="Edit Selected", command=lambda: edit_selected(tree, win))
    edit_btn.pack(side="left", padx=5)
    del_btn = ttk.Button(btn_frame, text="Delete Selected", command=lambda: delete_selected(tree))
    del_btn.pack(side="left", padx=5)

    # Treeview
    cols = ("ID", "Name", "Grade", "Salary", "Y1", "Y2", "Y3", "Y4", "Y5", "Flag")
    tree = ttk.Treeview(win, columns=cols, show="headings", height=15)
    for col in cols:
        tree.heading(col, text=col)
        tree.column(col, width=90 if col == "ID" else 100, anchor="center")
    tree.pack(fill="both", expand=True, padx=10, pady=5)

    load_employees(tree)

    # Double‑click to edit
    tree.bind("<Double-1>", lambda e: edit_selected(tree, win))

    win.mainloop()


# If run directly, open the manager
if __name__ == "__main__":
    show_employee_manager()
