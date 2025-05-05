import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import pathlib

# --- Grade Salary Bands ---
grades_data = [
    {"Grade": "112A", "Maximum": 43700},
    {"Grade": "113A", "Maximum": 48000},
    {"Grade": "114A", "Maximum": 52500},
    {"Grade": "115A", "Maximum": 57600},
    {"Grade": "116A", "Maximum": 63700},
    {"Grade": "117A", "Maximum": 69700},
]

def get_maximum_pay(grade):
    for grade_info in grades_data:
        if grade_info["Grade"] == grade:
            return grade_info["Maximum"]
    return float('inf')  # If grade not found, assume no limit

def salary_projection():
    salary_projection_employees = []
    salary_projection_total = [0, 0, 0, 0, 0, 0]

    # Check DB existence
    db_path = pathlib.Path("employee_performance.db")
    if not db_path.exists():
        messagebox.showerror("Database Error", "Database 'employee_performance.db' not found.")
        return [], []

    conn = sqlite3.connect("employee_performance.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM employees")
    rows = cursor.fetchall()

    for row in rows:
        employee_id = row[0]
        name = row[1]
        band = row[2]
        pay = row[3]
        employee = ["did not exceed band", employee_id, name, band, pay]
        salary_projection_total[0] += pay
        maximum_pay = get_maximum_pay(band)

        # Check if Year 0 salary already exceeds the band
        if pay > maximum_pay:
            employee[0] = "Band exceeded in year 0"

        for year in range(1, 6):
            pay *= 1.02
            employee.append(pay)
            salary_projection_total[year] += pay
            # Only update status if it hasn't been set yet
            if pay > maximum_pay and employee[0] == "did not exceed band":
                employee[0] = "Band exceeded in year " + str(year)

        salary_projection_employees.append(employee)

    conn.close()
    return salary_projection_employees, salary_projection_total

# --- UI Setup ---
window = tk.Tk()
window.title("Salary Projections Report")
window.geometry("1200x700")
window.configure(bg="#f0f4f8")

tk.Label(window, text="Employee Salary Projections", font="Helvetica 16 bold", bg="#f0f4f8").pack(pady=10)

columns = ["status", "id", "name", "grade", "year_0", "year_1", "year_2", "year_3", "year_4", "year_5"]
tree = ttk.Treeview(window, columns=columns, show="headings", height=20)
tree.pack(padx=20, pady=10, fill="x")

headers = ["Status", "ID", "Name", "Grade", "Year 0", "Year 1", "Year 2", "Year 3", "Year 4", "Year 5"]
for col, header in zip(columns, headers):
    tree.heading(col, text=header)
    if col == "status":
        tree.column(col, width=150, anchor=tk.CENTER)
    else:
        tree.column(col, width=100, anchor=tk.CENTER)

# Populate TreeView
employee_data, totals = salary_projection()
if employee_data:
    for emp in employee_data:
        row = emp[:4] + [f"${val:,.2f}" for val in emp[4:]]
        tree.insert("", "end", values=row)

    # Totals Display
    totals_frame = tk.Frame(window, bg="#f0f4f8")
    totals_frame.pack(pady=5)
    tk.Label(totals_frame, text="Total Salary per Year:", font="Helvetica 11 bold", bg="#f0f4f8").grid(row=0, column=0, sticky="w", padx=10)

    for i, total in enumerate(totals):
        tk.Label(totals_frame, text=f"Year {i}: ${total:,.2f}", bg="#f0f4f8").grid(row=i+1, column=0, sticky="w", padx=20)

    # Footnote
    tk.Label(window, text="*Note: Current salary is considered Year 0", font="Helvetica 9 italic", bg="#f0f4f8", fg="#333333").pack(pady=10, anchor="w", padx=20)

window.mainloop()
