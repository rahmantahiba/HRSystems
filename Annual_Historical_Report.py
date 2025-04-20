from tkinter import *
from tkinter import ttk, messagebox
import pathlib
import sqlite3

# Setup window
window = Tk()
window.title("Salary Forecast Report")
window.geometry("1000x600")
window.configure(bg="#f0f4f8")

# Database connection
database_file = pathlib.Path("employee_performance.db")
if not database_file.exists():
    messagebox.showerror("DATABASE ERROR", "Database not found. Closing program.")
    quit()

conn = sqlite3.connect(database_file)
cur = conn.cursor()
cur.execute("SELECT id, name, grade, current_salary, score_y1, score_y2, score_y3, score_y4, score_y5 FROM employees;")
records = cur.fetchall()

# Grade bands mapping to Maximum Salary
grade_bands = {
    "112A": 43700,
    "113A": 48000,
    "114A": 52500,
    "115A": 57600,
    "116A": 63700,
    "117A": 69700,
}

# Global variable to track forecast scores
forecasted_scores_dict = {}

# Title
Label(window, text="Annual Salary Forecast Report", font="Montserrat 16 bold", bg="#f0f4f8", fg="#000000").grid(row=0, column=0, columnspan=5, pady=10)

# Treeview 1: Current Employee Info
Label(window, text="Employee Information", font="Helvetica 12 bold", bg="#f0f4f8").grid(row=1, column=0, columnspan=2, sticky=W, padx=10)
tree_info = ttk.Treeview(window, columns=("id", "name", "grade", "current_salary"), show="headings", height=15)
tree_info.grid(row=2, column=0, columnspan=2, padx=10, sticky=W)

for col, width in zip(["id", "name", "grade", "current_salary"], [50, 150, 80, 120]):
    tree_info.heading(col, text=col.replace("_", " ").title())
    tree_info.column(col, width=width)

# --- Treeview 2: Forecast Info ---
Label(window, text="Forecast Report", font="Helvetica 12 bold", bg="#f0f4f8").grid(row=1, column=2, columnspan=2, sticky=W)
tree_forecast = ttk.Treeview(window, columns=("forecasted_score", "forecasted_salary", "last_year_forecasted_salary", "exceeds_maximum"), show="headings", height=15)
tree_forecast.grid(row=2, column=2, columnspan=2, padx=10, sticky=W)

# Update column headings
for col, width in zip(["forecasted_score", "forecasted_salary", "last_year_forecasted_salary", "exceeds_maximum"], [120, 140, 170, 120]):
    if col == "last_year_forecasted_salary":
        tree_forecast.heading(col, text="Last Year's Forecasted Salary")
    else:
        tree_forecast.heading(col, text=col.replace("_", " ").title())
    tree_forecast.column(col, width=width)

# Generate Report Function
def generate_report():
    year = year_var.get()
    if not year.isdigit() or int(year) < 1:
        messagebox.showerror("Input Error", "Please enter a valid forecast year (Ex: 1, 5, 10...)")
        return
    year_index = int(year)

    tree_info.delete(*tree_info.get_children())
    tree_forecast.delete(*tree_forecast.get_children())

    for emp in records:
        emp_id, name, grade, current_salary = emp[0], emp[1], emp[2], emp[3]
        forecasted_score = forecasted_scores_dict.get(emp_id, 3)

        forecasted_salary = current_salary * (1 + 0.02) ** year_index
        last_year_salary = current_salary * (1 + 0.02) ** (year_index - 1) if year_index > 1 else current_salary

        # Check if forecasted salary exceeds the maximum salary of the grade band
        max_salary = grade_bands.get(grade, 0)
        exceeds_max = "Yes" if forecasted_salary > max_salary else "No"

        # Insert into info tree
        tree_info.insert("", "end", values=(emp_id, name, grade, f"${current_salary:,.2f}"))
        # Insert into forecast tree
        tree_forecast.insert("", "end", values=(forecasted_score, f"${forecasted_salary:,.2f}", f"${last_year_salary:,.2f}", exceeds_max))

# Edit Forecasted Score
def edit_forecast_popup():
    popup = Toplevel(window)
    popup.title("Edit Forecasted Score")
    popup.geometry("300x200")

    Label(popup, text="Select Employee ID:").pack(pady=5)
    emp_ids = [str(emp[0]) for emp in records]
    emp_var = StringVar()
    emp_menu = ttk.Combobox(popup, textvariable=emp_var, values=emp_ids, state="readonly")
    emp_menu.pack()

    Label(popup, text="Enter New Forecasted Score (1-5):").pack(pady=5)
    score_var = StringVar()
    Entry(popup, textvariable=score_var).pack()

    def save_edit():
        try:
            emp_id = int(emp_var.get())
            score = int(score_var.get())
            if score < 1 or score > 5:
                raise ValueError
            forecasted_scores_dict[emp_id] = score
            popup.destroy()
            generate_report()
        except:
            messagebox.showerror("Input Error", "Please enter a valid score (1–5).")

    Button(popup, text="Save", command=save_edit).pack(pady=10)

# --- Apply Same Score to All ---
def apply_same_forecast_popup():
    popup = Toplevel(window)
    popup.title("Set Same Forecast Score")
    popup.geometry("300x150")

    Label(popup, text="Enter Forecasted Score for All Employees (1–5):").pack(pady=10)
    score_var = StringVar()
    Entry(popup, textvariable=score_var).pack()

    def set_all():
        try:
            score = int(score_var.get())
            if score < 1 or score > 5:
                raise ValueError
            for emp in records:
                forecasted_scores_dict[emp[0]] = score
            popup.destroy()
            generate_report()
        except:
            messagebox.showerror("Input Error", "Please enter a valid score (1–5).")

    Button(popup, text="Apply to All", command=set_all).pack(pady=10)

# --- Controls ---
Label(window, text="Forecast Year:", bg="#f0f4f8").grid(row=3, column=0, sticky=E, padx=5)
year_var = StringVar()
Entry(window, textvariable=year_var, width=5).grid(row=3, column=1, sticky=W)

Button(window, text="Generate Report", command=generate_report).grid(row=3, column=2, sticky=W, padx=5)
Button(window, text="Edit Forecasted Score", command=edit_forecast_popup).grid(row=4, column=2, sticky=W, padx=5)
Button(window, text="Set Same Forecast for All", command=apply_same_forecast_popup).grid(row=5, column=2, sticky=W, padx=5)

window.mainloop()
