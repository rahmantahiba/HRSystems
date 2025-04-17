import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import os

# Static band limits from performance_evaluation.py
grades_data = [
    {"Grade": "112A", "Maximum": 43700},
    {"Grade": "113A", "Maximum": 48000},
    {"Grade": "114A", "Maximum": 52500},
    {"Grade": "115A", "Maximum": 57600},
    {"Grade": "116A", "Maximum": 63700},
    {"Grade": "117A", "Maximum": 69700},
]

def init_database(db_file):
    """Initialize employees.db with employees and band_limits tables."""
    if not os.path.exists(db_file):
        if messagebox.askyesno(
            "Database Not Found",
            "No database found. Would you like to create one?"
        ):
            conn = sqlite3.connect(db_file)
            c = conn.cursor()
            # Employees table
            c.execute('''
                CREATE TABLE employees (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    title TEXT NOT NULL,
                    classification TEXT NOT NULL,
                    pay REAL NOT NULL,
                    band TEXT NOT NULL,
                    is_active INTEGER NOT NULL
                )
            ''')
            # Band limits table
            c.execute('''
                CREATE TABLE band_limits (
                    band TEXT PRIMARY KEY,
                    max_salary REAL NOT NULL
                )
            ''')
            # Insert band limits
            band_limits = [(grade["Grade"], grade["Maximum"]) for grade in grades_data]
            c.executemany(
                "INSERT INTO band_limits (band, max_salary) VALUES (?, ?)",
                band_limits
            )
            conn.commit()
            conn.close()
        else:
            return False
    return True

def show_employee_form(parent, db_file, tree=None, employee=None, emp_id=None):
    """Show form to add or edit an employee."""
    form_window = tk.Toplevel(parent)
    form_window.title("Add Employee" if not employee else "Edit Employee")
    form_window.geometry("400x350")
    form_window.configure(bg="#f0f4f8")

    tk.Label(
        form_window,
        text="Add Employee" if not employee else "Edit Employee",
        font="Montserrat 16 bold",
        bg="#f0f4f8",
        fg="#000000"
    ).pack(pady=10)

    # Form fields
    tk.Label(
        form_window,
        text="Name:",
        font="Montserrat 12",
        bg="#f0f4f8",
        fg="#000000"
    ).pack()
    name_entry = ttk.Entry(form_window)
    name_entry.pack(pady=5)

    tk.Label(
        form_window,
        text="Title:",
        font="Montserrat 12",
        bg="#f0f4f8",
        fg="#000000"
    ).pack()
    title_entry = ttk.Entry(form_window)
    title_entry.pack(pady=5)

    tk.Label(
        form_window,
        text="Classification:",
        font="Montserrat 12",
        bg="#f0f4f8",
        fg="#000000"
    ).pack()
    classification_combo = ttk.Combobox(
        form_window,
        values=["Full-time", "Part-time", "Adjunct"],
        state="readonly"
    )
    classification_combo.pack(pady=5)

    tk.Label(
        form_window,
        text="Band:",
        font="Montserrat 12",
        bg="#f0f4f8",
        fg="#000000"
    ).pack()
    band_combo = ttk.Combobox(
        form_window,
        values=["112A", "113A", "114A", "115A", "116A", "117A"],
        state="readonly"
    )
    band_combo.pack(pady=5)

    tk.Label(
        form_window,
        text="Pay ($):",
        font="Montserrat 12",
        bg="#f0f4f8",
        fg="#000000"
    ).pack()
    pay_entry = ttk.Entry(form_window)
    pay_entry.pack(pady=5)

    # Pre-fill for edit
    if employee:
        name_entry.insert(0, employee[0])
        title_entry.insert(0, employee[1])
        classification_combo.set(employee[2])
        pay_entry.insert(0, str(employee[3]))
        band_combo.set(employee[4])

    def save_employee():
        name = name_entry.get().strip()
        title = title_entry.get().strip()
        classification = classification_combo.get()
        band = band_combo.get()
        try:
            pay = float(pay_entry.get())
            if pay <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Pay must be a positive number.")
            return
        if not all([name, title, classification, band]):
            messagebox.showerror("Error", "All fields are required.")
            return

        conn = sqlite3.connect(db_file)
        c = conn.cursor()
        if emp_id:
            c.execute(
                "UPDATE employees SET name = ?, title = ?, classification = ?, pay = ?, band = ? WHERE id = ?",
                (name, title, classification, pay, band, emp_id)
            )
        else:
            c.execute(
                "INSERT INTO employees (name, title, classification, pay, band, is_active) VALUES (?, ?, ?, ?, ?, 1)",
                (name, title, classification, pay, band)
            )
        conn.commit()
        conn.close()
        if tree:
            load_employees(db_file, tree)
        form_window.destroy()

    ttk.Button(
        form_window,
        text="Save",
        style="Nav.TButton",
        command=save_employee
    ).pack(pady=10)
    ttk.Button(
        form_window,
        text="Cancel",
        style="Nav.TButton",
        command=form_window.destroy
    ).pack(pady=5)

def load_employees(db_file, tree, is_active=1):
    """Load employees into the Treeview (active or archived)."""
    for item in tree.get_children():
        tree.delete(item)

    conn = sqlite3.connect(db_file)
    c = conn.cursor()

    # Get band limits
    c.execute("SELECT band, max_salary FROM band_limits")
    band_limits = {row[0]: row[1] for row in c.fetchall()}

    # Get employees
    c.execute(
        "SELECT id, name, title, classification, pay, band FROM employees WHERE is_active = ?",
        (is_active,)
    )
    exceedances = []
    for row in c.fetchall():
        emp_id, name, title, classification, pay, band = row
        flag = ""
        tag = ""
        if band in band_limits and pay > band_limits[band]:
            flag = "Exceeds Limit"
            tag = "exceed"
            exceedances.append(f"{name}: Pay ${pay:.2f} exceeds {band} limit ${band_limits[band]:.2f}")
        tree.insert(
            "",
            "end",
            values=(name, title, classification, f"{pay:.2f}", flag),
            tags=(tag,),
            iid=str(emp_id)
        )

    conn.close()

    # Save exceedances (only for active employees)
    if is_active:
        with open("exceedances.txt", "w") as f:
            f.write("\n".join(exceedances) if exceedances else "No exceedances.")

def show_archived_employees(parent, db_file):
    """Show a window with archived employees."""
    window = tk.Toplevel(parent)
    window.title("Archived Employees")
    window.geometry("900x500")
    window.minsize(900, 500)
    window.configure(bg="#f0f4f8")

    # Title
    tk.Label(
        window,
        text="Archived Employees",
        font="Montserrat 16 bold",
        bg="#f0f4f8",
        fg="#000000"
    ).pack(pady=10)

    # Treeview
    tree_frame = tk.Frame(window, bg="#f0f4f8")
    tree_frame.pack(pady=10, padx=10, fill="both", expand=True)

    columns = ("Name", "Title", "Classification", "Pay", "Flag")
    tree = ttk.Treeview(
        tree_frame,
        columns=columns,
        show="headings",
        height=10
    )
    tree.heading("Name", text="Name")
    tree.heading("Title", text="Title")
    tree.heading("Classification", text="Classification")
    tree.heading("Pay", text="Pay ($)")
    tree.heading("Flag", text="Flag")
    tree.column("Name", width=250)
    tree.column("Title", width=250)
    tree.column("Classification", width=150)
    tree.column("Pay", width=150)
    tree.column("Flag", width=150)

    # Scrollbar
    scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    tree.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Tag for exceedance
    tree.tag_configure("exceed", background="#ffcccc")

    # Load archived employees
    load_employees(db_file, tree, is_active=0)

    # Close button
    ttk.Button(
        window,
        text="Close",
        style="Nav.TButton",
        command=window.destroy
    ).pack(pady=10)

def show_employee_manager(parent):
    """Show the employee management window."""
    db_file = "employees.db"
    if not init_database(db_file):
        messagebox.showinfo("Info", "Feature unavailable without database.")
        return

    window = tk.Toplevel(parent)
    window.title("Add/Edit Employee")
    window.geometry("900x500")
    window.minsize(900, 500)
    window.configure(bg="#f0f4f8")

    # Title
    tk.Label(
        window,
        text="Add or Edit Employee",
        font="Montserrat 16 bold",
        bg="#f0f4f8",
        fg="#000000"
    ).pack(pady=10)

    # Button frame
    button_frame = tk.Frame(window, bg="#f0f4f8")
    button_frame.pack(pady=5)
    ttk.Button(
        button_frame,
        text="Add New Employee",
        style="Nav.TButton",
        command=lambda: show_employee_form(window, db_file)
    ).pack(side="left", padx=10)
    edit_button = ttk.Button(
        button_frame,
        text="Edit Selected Employee",
        style="Nav.TButton",
        command=lambda: edit_selected_employee(window, db_file, tree),
        state="disabled"
    )
    edit_button.pack(side="left", padx=10)
    archive_button = ttk.Button(
        button_frame,
        text="Archive Selected Employee",
        style="Nav.TButton",
        command=lambda: archive_selected_employee(db_file, tree),
        state="disabled"
    )
    archive_button.pack(side="left", padx=10)
    ttk.Button(
        button_frame,
        text="Show Archived Employees",
        style="Nav.TButton",
        command=lambda: show_archived_employees(window, db_file)
    ).pack(side="left", padx=10)

    # Treeview
    tree_frame = tk.Frame(window, bg="#f0f4f8")
    tree_frame.pack(pady=10, padx=10, fill="both", expand=True)

    columns = ("Name", "Title", "Classification", "Pay", "Flag")
    tree = ttk.Treeview(
        tree_frame,
        columns=columns,
        show="headings",
        height=10
    )
    tree.heading("Name", text="Name")
    tree.heading("Title", text="Title")
    tree.heading("Classification", text="Classification")
    tree.heading("Pay", text="Pay ($)")
    tree.heading("Flag", text="Flag")
    tree.column("Name", width=250)
    tree.column("Title", width=250)
    tree.column("Classification", width=150)
    tree.column("Pay", width=150)
    tree.column("Flag", width=150)

    # Scrollbar
    scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    tree.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Tag for exceedance
    tree.tag_configure("exceed", background="#ffcccc")

    # Bindings
    tree.bind("<Double-1>", lambda event: edit_selected_employee(window, db_file, tree))
    tree.bind("<<TreeviewSelect>>", lambda event: on_tree_select(edit_button, archive_button, tree))

    # Load active employees
    load_employees(db_file, tree, is_active=1)

def on_tree_select(edit_button, archive_button, tree):
    """Enable/disable buttons based on selection."""
    selected = tree.selection()
    state = "normal" if selected else "disabled"
    edit_button.configure(state=state)
    archive_button.configure(state=state)

def edit_selected_employee(parent, db_file, tree):
    """Edit the selected employee."""
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Warning", "Please select an employee.")
        return
    emp_id = selected[0]
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    c.execute(
        "SELECT name, title, classification, pay, band FROM employees WHERE id = ?",
        (emp_id,)
    )
    employee = c.fetchone()
    conn.close()
    if employee:
        show_employee_form(parent, db_file, tree, employee, emp_id)

def archive_selected_employee(db_file, tree):
    """Archive the selected employee."""
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Warning", "Please select an employee.")
        return
    emp_id = selected[0]
    if messagebox.askyesno(
        "Confirm Archive",
        "Archive this employee? They will no longer appear in the active list."
    ):
        conn = sqlite3.connect(db_file)
        c = conn.cursor()
        c.execute("UPDATE employees SET is_active = 0 WHERE id = ?", (emp_id,))
        conn.commit()
        conn.close()
        load_employees(db_file, tree, is_active=1)