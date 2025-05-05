import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sys
import pathlib
import sqlite3

# Import modules but don't run their main code automatically
# We'll use function calls instead of directly importing the modules
import importlib.util

import os

if os.path.exists("employees.db"):
    os.remove("employees.db")

# Recreate the database with correct schema
conn = sqlite3.connect("employees.db")
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        grade TEXT,
        salary REAL
    )
""")
conn.commit()
conn.close()

def update_employees_db_from_csv(df):
    conn = sqlite3.connect("employees.db")
    cursor = conn.cursor()

    for _, row in df.iterrows():
        cursor.execute("""
            INSERT OR REPLACE INTO employees (id, name, grade, salary)
            VALUES (?, ?, ?, ?)
        """, (row["ID"], row["Name"], row["Grade"], row["Salary"]))

    conn.commit()
    conn.close()

def import_module(module_name):
    """Import a module by name without running its main code"""
    # Check if module is already imported
    if module_name in sys.modules:
        return sys.modules[module_name]

    # Import the module without executing main code
    spec = importlib.util.find_spec(module_name)
    if spec is None:
        messagebox.showerror("Module Error", f"Could not find module '{module_name}'")
        return None

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def ensure_pandas_installed():
    try:
        import pandas as pd
    except ImportError:
        root = tk.Tk()
        root.withdraw()  # Hide main window
        response = messagebox.askyesno(
            "Missing Dependency",
            "The 'pandas' package is not installed.\n\nWould you like to install it now?"
        )
        if response:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "pandas"])
                messagebox.showinfo("Success", "'pandas' was successfully installed. Please restart the program.")
                sys.exit(0)
            except Exception as e:
                messagebox.showerror("Installation Failed", f"An error occurred while installing 'pandas':\n{e}")
                sys.exit(1)
        else:
            messagebox.showwarning("Exiting", "This program requires 'pandas'. Exiting.")
            sys.exit(1)

ensure_pandas_installed()
import pandas as pd

def ensure_employees_table_has_columns():
    try:
        conn = sqlite3.connect("employees.db")
        cursor = conn.cursor()

        cursor.execute("PRAGMA table_info(employees)")
        columns = [col[1] for col in cursor.fetchall()]

        if "salary" not in columns:
            cursor.execute("ALTER TABLE employees ADD COLUMN salary REAL")
            print("Added 'salary' column to employees table.")

        if "grade" not in columns:
            cursor.execute("ALTER TABLE employees ADD COLUMN grade TEXT")
            print("Added 'grade' column to employees table.")

        conn.commit()
        conn.close()
    except Exception as e:
        print("Error updating table schema:", e)

class HRPerformanceEvaluatorApp:
    def __init__(self, root):
        print("Initializing main window only")  # Debug to confirm startup
        self.root = root
        self.root.title("HR Performance Evaluator")
        self.root.geometry("600x500")
        self.root.minsize(600, 500)
        self.root.configure(bg="#f0f4f8")

        # Main frame for navigation (no module UIs opened here)
        self.main_frame = tk.Frame(self.root, bg="#f0f4f8")
        self.main_frame.place(relx=0.5, rely=0.45, anchor="center")

        # Title
        tk.Label(
            self.main_frame,
            text="HR Performance Evaluator",
            font="Montserrat 24 bold",
            bg="#f0f4f8",
            fg="#000000"
        ).grid(row=0, column=0, pady=(0, 20))

        # Button style
        style = ttk.Style()
        style.configure(
            "Nav.TButton",
            font="Montserrat 12",
            padding=10,
            background="#3498db",
            foreground="#000000"
        )
        style.map(
            "Nav.TButton",
            background=[("active", "#2980b9")],
            foreground=[("active", "#000000")]
        )
        style.configure(
            "Help.TButton",
            font="Montserrat 10",
            padding=5,
            background="#3498db",
            foreground="#000000"
        )
        style.map(
            "Help.TButton",
            background=[("active", "#2980b9")],
            foreground=[("active", "#000000")]
        )

        # Navigation buttons (only trigger when clicked)
        buttons = [
            ("Add/Edit Employee", self.open_add_edit_employee),
            ("Performance Evaluation", self.open_performance_eval),
            ("View Salary Forecast", self.open_salary_forecast),
            ("Check Band Limits", self.open_band_limits),
            ("Generate Report", self.open_generate_report)
        ]
        for i, (text, command) in enumerate(buttons, 1):
            ttk.Button(
                self.main_frame,
                text=text,
                style="Nav.TButton",
                command=command,
                width=25
            ).grid(row=i, column=0, pady=5, padx=20)

        # Get Help button
        help_frame = tk.Frame(self.root, bg="#f0f4f8")
        help_frame.place(relx=0.05, rely=0.95, anchor="sw")
        ttk.Button(
            help_frame,
            text="Get Help",
            style="Help.TButton",
            command=self.open_help,
            width=10
        ).pack()

    @staticmethod
    def salary_projection():
        GROWTH_RATE = 0.02
        YEARS = 6
        GRADES_MAX = {
            "112A": 43700,
            "113A": 48000,
            "114A": 52500,
            "115A": 57600,
            "116A": 63700,
            "117A": 69700,
        }

        def get_maximum(grade):
            return GRADES_MAX.get(grade, float("inf"))

        salary_projection_employees = []
        salary_projection_total = [0.0 for _ in range(YEARS)]

        try:
            conn = sqlite3.connect("employees.db")
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, grade, salary FROM employees")
            rows = cursor.fetchall()
            print(f"Rows fetched: {rows}")  # <--- Add this line
        except Exception as e:
            print("DB Error:", e)
            return [], []

        for row in rows:
            try:
                emp_id, name, grade, salary = row
                current_salary = float(salary)
                max_band = get_maximum(grade)
            except Exception as e:
                print(f"Skipping invalid row: {e}")
                continue

            projection = ["Did not exceed band", emp_id, name, grade]
            yearly = [round(current_salary, 2)]
            salary_projection_total[0] += yearly[0]

            exceeded = False
            for year in range(1, YEARS):
                if not exceeded:
                    current_salary *= (1 + GROWTH_RATE)
                    current_salary = round(current_salary, 2)
                    if current_salary > max_band:
                        exceeded = True
                        projection[0] = f"Band exceeded in year {year}"
                yearly.append(current_salary)
                salary_projection_total[year] += current_salary

            projection.extend(yearly)
            salary_projection_employees.append(projection)

        conn.close()
        return salary_projection_employees, salary_projection_total

    def open_add_edit_employee(self):
        print("Opening Employee Manager")  # Debug
        employee_manager = import_module("employee_manager")
        if employee_manager:
            employee_manager.show_employee_manager(self.root)

    def open_performance_eval(self):
        print("Opening Performance Evaluation")  # Debug
        performance_evaluation = import_module("performance_evaluation")
        if performance_evaluation:
            # Create database first
            performance_evaluation.create_database()

            # Create window
            window = tk.Toplevel(self.root)
            window.title("Employee Performance Database")
            window.geometry("1200x600")
            window.minsize(600, 500)
            window.configure(bg="#f0f4f8")

            # Input fields
            tk.Label(window, text="Name", bg="#f0f4f8").grid(row=0, column=0, padx=5, pady=5)
            tk.Label(window, text="Grade", bg="#f0f4f8").grid(row=1, column=0, padx=5, pady=5)
            tk.Label(window, text="Current Salary", bg="#f0f4f8").grid(row=2, column=0, padx=5, pady=5)
            tk.Label(window, text="Scores (Y1-Y5)", bg="#f0f4f8").grid(row=3, column=0, padx=5, pady=5)

            name_entry = tk.Entry(window)
            grade_entry = tk.Entry(window)
            salary_entry = tk.Entry(window)
            score_entries = [tk.Entry(window, width=4) for _ in range(5)]

            name_entry.grid(row=0, column=1, padx=5, pady=5)
            grade_entry.grid(row=1, column=1, padx=5, pady=5)
            salary_entry.grid(row=2, column=1, padx=5, pady=5)
            for i, entry in enumerate(score_entries):
                entry.grid(row=3, column=i + 1, padx=2)

            # Set module variables so functions can access them
            performance_evaluation.name_entry = name_entry
            performance_evaluation.grade_entry = grade_entry
            performance_evaluation.salary_entry = salary_entry
            performance_evaluation.score_entries = score_entries
            performance_evaluation.root = window

            # Buttons - use lambda to pass the new instances to functions
            ttk.Button(window, text="Add Employee",
                       command=performance_evaluation.submit_form).grid(row=4, column=0, pady=5)
            ttk.Button(window, text="Show Salary Projections",
                       command=performance_evaluation.show_evaluations).grid(row=4, column=1, pady=5)
            ttk.Button(window, text="Show Combined Budget",
                       command=performance_evaluation.show_salary_budget).grid(row=4, column=2, pady=5)
            ttk.Button(window, text="Delete Selected",
                       command=performance_evaluation.delete_selected_employee).grid(row=4, column=3, pady=5)
            ttk.Button(window, text="Import CSV",
                       command=performance_evaluation.import_from_csv).grid(row=4, column=5, pady=5)
            ttk.Button(window, text="Export CSV",
                       command=performance_evaluation.export_to_csv).grid(row=4, column=6, pady=5)

            # Search
            tk.Label(window, text="Search Name:", bg="#f0f4f8").grid(row=4, column=7, padx=5)
            search_entry = tk.Entry(window)
            search_entry.grid(row=4, column=8, padx=5)
            ttk.Button(window, text="Search",
                       command=lambda: performance_evaluation.search_employees(search_entry.get())).grid(row=4,
                                                                                                         column=9,
                                                                                                         padx=5)

            # Treeview
            cols = ("ID", "Name", "Grade", "Salary", "Y1", "Y2", "Y3", "Y4", "Y5", "Max Band", "Exceeded Year", "Flag")
            tree_frame = tk.Frame(window, bg="#f0f4f8")
            tree_frame.grid(row=7, column=0, columnspan=10, pady=10)

            x_scroll = tk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
            x_scroll.pack(side=tk.BOTTOM, fill=tk.X)

            tree = ttk.Treeview(tree_frame, columns=cols, show='headings', xscrollcommand=x_scroll.set)
            x_scroll.config(command=tree.xview)

            for col in cols:
                tree.heading(col, text=col)
                tree.column(col, width=100, anchor='center')

            tree.pack(fill='both', expand=True)

            # Set tree in the module
            performance_evaluation.tree = tree

            # Call display_records to show data
            performance_evaluation.display_records()

    def open_salary_forecast(self):
        print("Opening salary forecast")  # Debug
        salary_proj = import_module("Salary_Projections")
        print("salary_proj =", salary_proj)  # Debug if import failed

        if not salary_proj:
            messagebox.showerror("Import Error", "Could not load Salary_Projections module.")
            return

        window = tk.Toplevel(self.root)
        window.title("Salary Projections Report")
        window.geometry("1200x600")
        window.configure(bg="#f0f4f8")

        tk.Label(window, text="Employee Salary Projections", font="Helvetica 16 bold", bg="#f0f4f8").pack(pady=10)

        columns = ["status", "id", "name", "grade", "year_0", "year_1", "year_2", "year_3", "year_4", "year_5"]
        headers = ["Status", "ID", "Name", "Grade", "Year 0", "Year 1", "Year 2", "Year 3", "Year 4", "Year 5"]

        tree = ttk.Treeview(window, columns=columns, show="headings", height=20)
        tree.pack(padx=20, pady=10, fill="x")

        for col, header in zip(columns, headers):
            tree.heading(col, text=header)
            tree.column(col, width=100, anchor=tk.CENTER)

        try:
            employee_data, totals = salary_proj.salary_projection()
            print("Employee Data:", employee_data)  # Debug data returned
        except Exception as e:
            messagebox.showerror("Projection Error", f"An error occurred during salary projection:\n{e}")
            return

        if not employee_data:
            messagebox.showinfo("No Data", "No employee salary data found to display.")
            return

        for emp in employee_data:
            try:
                row = emp[:4] + [f"${val:,.2f}" for val in emp[4:]]
                tree.insert("", "end", values=row)
            except Exception as e:
                print(f"Error inserting row {emp}: {e}")

        # Totals
        totals_frame = tk.Frame(window, bg="#f0f4f8")
        totals_frame.pack(pady=5)
        tk.Label(totals_frame, text="Total Salary per Year:", font="Helvetica 11 bold", bg="#f0f4f8").grid(row=0,
                                                                                                           column=0,
                                                                                                           sticky="w",
                                                                                                           padx=10)

        for i, total in enumerate(totals):
            tk.Label(totals_frame, text=f"Year {i}: ${total:,.2f}", bg="#f0f4f8").grid(row=i + 1, column=0, sticky="w",
                                                                                       padx=20)

        tk.Label(window, text="*Note: Current salary is considered Year 0", font="Helvetica 9 italic",
                 bg="#f0f4f8", fg="#333333").pack(pady=10, anchor="w", padx=20)

    def open_band_limits(self):
        print("Opening Band Limits")  # Debug

        window = tk.Toplevel(self.root)
        window.title("Salary Band Limits")
        window.geometry("600x300")
        window.configure(bg="#f0f4f8")

        tk.Label(window, text="Salary Band Limits", font="Helvetica 16 bold", bg="#f0f4f8").pack(pady=10)

        columns = ["grade", "min", "mid", "max"]
        headers = ["Grade", "Minimum", "Midpoint", "Maximum"]

        tree = ttk.Treeview(window, columns=columns, show="headings", height=10)
        tree.pack(padx=20, pady=10, fill="x")

        for col, header in zip(columns, headers):
            tree.heading(col, text=header)
            tree.column(col, width=120, anchor=tk.CENTER)

        # Load static band data
        grades_data = [
            {"Grade": "112A", "Minimum": 32240, "Midpoint": 34600, "Maximum": 43700},
            {"Grade": "113A", "Minimum": 32240, "Midpoint": 38000, "Maximum": 48000},
            {"Grade": "114A", "Minimum": 32800, "Midpoint": 41900, "Maximum": 52500},
            {"Grade": "115A", "Minimum": 34400, "Midpoint": 45900, "Maximum": 57600},
            {"Grade": "116A", "Minimum": 38000, "Midpoint": 50600, "Maximum": 63700},
            {"Grade": "117A", "Minimum": 41600, "Midpoint": 55500, "Maximum": 69700},
        ]

        for row in grades_data:
            tree.insert("", "end", values=(
            row["Grade"], f"${row['Minimum']:,.0f}", f"${row['Midpoint']:,.0f}", f"${row['Maximum']:,.0f}"))

        # Footnote
        tk.Label(
            window,
            text="*Note: Salary bands define acceptable pay ranges for each grade.",
            font="Helvetica 9 italic",
            bg="#f0f4f8",
            fg="#333333"
        ).pack(pady=10, anchor="w", padx=20)

    def open_generate_report(self):
        print("Opening Generate Report")

        grade_bands = {
            "112A": 43700,
            "113A": 48000,
            "114A": 52500,
            "115A": 57600,
            "116A": 63700,
            "117A": 69700,
        }
        forecasted_scores_dict = {}

        conn = sqlite3.connect("employees.db")
        cur = conn.cursor()
        cur.execute("SELECT id, name, grade, salary FROM employees;")
        records = cur.fetchall()
        conn.close()

        window = tk.Toplevel(self.root)
        window.title("Salary Forecast Report")
        window.geometry("1000x600")
        window.configure(bg="#f0f4f8")

        # Title
        tk.Label(window, text="Annual Salary Forecast Report", font="Montserrat 16 bold", bg="#f0f4f8",
                 fg="#000000").grid(row=0, column=0, columnspan=5, pady=10)

        # Treeview 1: Employee Info
        tk.Label(window, text="Employee Information", font="Helvetica 12 bold", bg="#f0f4f8").grid(
            row=1, column=0, columnspan=2, sticky="w", padx=10)
        tree_info = ttk.Treeview(window, columns=("id", "name", "grade", "current_salary"), show="headings", height=15)
        tree_info.grid(row=2, column=0, columnspan=2, padx=10, sticky="w")
        for col, width in zip(["id", "name", "grade", "current_salary"], [50, 150, 80, 120]):
            tree_info.heading(col, text=col.replace("_", " ").title())
            tree_info.column(col, width=width)

        # Treeview 2: Forecast Info
        tk.Label(window, text="Forecast Report", font="Helvetica 12 bold", bg="#f0f4f8").grid(
            row=1, column=2, columnspan=2, sticky="w")
        tree_forecast = ttk.Treeview(window, columns=(
            "forecasted_score", "forecasted_salary", "last_year_forecasted_salary", "exceeds_maximum"), show="headings",
                                     height=15)
        tree_forecast.grid(row=2, column=2, columnspan=2, padx=10, sticky="w")
        for col, width in zip(
                ["forecasted_score", "forecasted_salary", "last_year_forecasted_salary", "exceeds_maximum"],
                [120, 140, 170, 120]):
            header = "Last Year's Forecasted Salary" if col == "last_year_forecasted_salary" else col.replace("_",
                                                                                                              " ").title()
            tree_forecast.heading(col, text=header)
            tree_forecast.column(col, width=width)

        # Entry for year
        tk.Label(window, text="Forecast Year:", bg="#f0f4f8").grid(row=3, column=0, sticky="e", padx=5)
        year_var = tk.StringVar(value="1")
        tk.Entry(window, textvariable=year_var, width=5).grid(row=3, column=1, sticky="w")

        def generate_report():
            year_str = year_var.get().strip()
            if not year_str.isdigit() or int(year_str) < 1:
                messagebox.showerror("Input Error", "Please enter a whole number ≥ 1 for forecast year.")
                return
            year_index = int(year_str)

            tree_info.delete(*tree_info.get_children())
            tree_forecast.delete(*tree_forecast.get_children())

            for emp in records:
                emp_id, name, grade, current_salary = emp
                forecasted_score = forecasted_scores_dict.get(emp_id, 3)
                forecasted_salary = current_salary * (1 + 0.02) ** year_index
                last_year_salary = current_salary * (1 + 0.02) ** (year_index - 1) if year_index > 1 else current_salary
                max_salary = grade_bands.get(grade, 0)
                exceeds = "Yes" if forecasted_salary > max_salary else "No"

                tree_info.insert("", "end", values=(emp_id, name, grade, f"${current_salary:,.2f}"))
                tree_forecast.insert("", "end", values=(
                    forecasted_score, f"${forecasted_salary:,.2f}", f"${last_year_salary:,.2f}", exceeds))

        def edit_forecast_popup():
            popup = tk.Toplevel(window)
            popup.title("Edit Forecasted Score")
            popup.geometry("300x200")
            tk.Label(popup, text="Select Employee ID:").pack(pady=5)
            emp_ids = [str(emp[0]) for emp in records]
            emp_var = tk.StringVar()
            emp_menu = ttk.Combobox(popup, textvariable=emp_var, values=emp_ids, state="readonly")
            emp_menu.pack()
            tk.Label(popup, text="Enter New Forecasted Score (1-5):").pack(pady=5)
            score_var = tk.StringVar()
            tk.Entry(popup, textvariable=score_var).pack()

            def save_edit():
                try:
                    emp_id = int(emp_var.get())
                    score = int(score_var.get())
                    if not (1 <= score <= 5):
                        raise ValueError
                    forecasted_scores_dict[emp_id] = score
                    popup.destroy()
                    generate_report()
                except:
                    messagebox.showerror("Input Error", "Please enter a valid score (1–5).")

            tk.Button(popup, text="Save", command=save_edit).pack(pady=10)

        def apply_same_forecast_popup():
            popup = tk.Toplevel(window)
            popup.title("Set Same Forecast Score")
            popup.geometry("300x150")
            tk.Label(popup, text="Enter Forecasted Score for All Employees (1–5):").pack(pady=10)
            score_var = tk.StringVar()
            tk.Entry(popup, textvariable=score_var).pack()

            def set_all():
                try:
                    score = int(score_var.get())
                    if not (1 <= score <= 5):
                        raise ValueError
                    for emp in records:
                        forecasted_scores_dict[emp[0]] = score
                    popup.destroy()
                    generate_report()
                except:
                    messagebox.showerror("Input Error", "Please enter a valid score (1–5).")

            tk.Button(popup, text="Apply to All", command=set_all).pack(pady=10)

        # Buttons
        ttk.Button(window, text="Generate Report", command=generate_report).grid(row=3, column=2, sticky="w", padx=5)
        ttk.Button(window, text="Edit Forecasted Score", command=edit_forecast_popup).grid(row=4, column=2, sticky="w",
                                                                                           padx=5)
        ttk.Button(window, text="Set Same Forecast for All", command=apply_same_forecast_popup).grid(row=5, column=2,
                                                                                                     sticky="w", padx=5)

        generate_report()

    def open_help(self):
        print("Opening Help")  # Debug
        window = tk.Toplevel(self.root)
        window.title("Help")
        window.geometry("400x300")
        window.minsize(600, 500)
        window.configure(bg="#f0f4f8")
        tk.Label(
            window,
            text="Help",
            font="Montserrat 16 bold",
            bg="#f0f4f8",
            fg="#000000"
        ).pack(pady=10)
        tk.Label(
            window,
            text="Refer to the usage manual (PDF) for instructions.",
            font="Montserrat 12",
            bg="#f0f4f8",
            fg="#000000",
            wraplength=350
        ).pack(pady=20)

if __name__ == "__main__":
    root = tk.Tk()
    ensure_employees_table_has_columns()
    df = pd.read_csv("employee_export.csv")
    update_employees_db_from_csv(df)
    app = HRPerformanceEvaluatorApp(root)
    root.mainloop()

