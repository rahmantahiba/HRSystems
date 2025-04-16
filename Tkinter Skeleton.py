import tkinter as tk
from tkinter import ttk
import employee_manager  # Import the separate feature module

class HRPerformanceEvaluatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("HR Performance Evaluator")
        self.root.geometry("600x500")
        self.root.minsize(600, 500)
        self.root.configure(bg="#f0f4f8")

        # Main frame for navigation
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

        # Navigation buttons
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

    def open_add_edit_employee(self):
        employee_manager.show_employee_manager(self.root)

    def open_performance_eval(self):
        window = tk.Toplevel(self.root)
        window.title("Performance Evaluation")
        window.geometry("400x300")
        window.minsize(600, 500)
        window.configure(bg="#f0f4f8")
        tk.Label(
            window,
            text="Performance Evaluation",
            font="Montserrat 16 bold",
            bg="#f0f4f8",
            fg="#000000"
        ).pack(pady=10)
        tk.Label(
            window,
            text="Feature under development",
            font="Montserrat 12",
            bg="#f0f4f8",
            fg="#000000"
        ).pack(pady=20)

    def open_salary_forecast(self):
        window = tk.Toplevel(self.root)
        window.title("Salary Forecast")
        window.geometry("400x300")
        window.minsize(600, 500)
        window.configure(bg="#f0f4f8")
        tk.Label(
            window,
            text="Salary Forecast",
            font="Montserrat 16 bold",
            bg="#f0f4f8",
            fg="#000000"
        ).pack(pady=10)
        tk.Label(
            window,
            text="Feature under development",
            font="Montserrat 12",
            bg="#f0f4f8",
            fg="#000000"
        ).pack(pady=20)

    def open_band_limits(self):
        window = tk.Toplevel(self.root)
        window.title("Check Band Limits")
        window.geometry("400x300")
        window.minsize(600, 500)
        window.configure(bg="#f0f4f8")
        tk.Label(
            window,
            text="Check Band Limits",
            font="Montserrat 16 bold",
            bg="#f0f4f8",
            fg="#000000"
        ).pack(pady=10)
        tk.Label(
            window,
            text="Feature under development",
            font="Montserrat 12",
            bg="#f0f4f8",
            fg="#000000"
        ).pack(pady=20)

    def open_generate_report(self):
        window = tk.Toplevel(self.root)
        window.title("Generate Report")
        window.geometry("400x300")
        window.minsize(600, 500)
        window.configure(bg="#f0f4f8")
        tk.Label(
            window,
            text="Generate Report",
            font="Montserrat 16 bold",
            bg="#f0f4f8",
            fg="#000000"
        ).pack(pady=10)
        tk.Label(
            window,
            text="Feature under development",
            font="Montserrat 12",
            bg="#f0f4f8",
            fg="#000000"
        ).pack(pady=20)

    def open_help(self):
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
    app = HRPerformanceEvaluatorApp(root)
    root.mainloop()