import pandas as pd

# Step 1: Define the A band salary data
grades_data = [
    {"Grade": "112A", "Minimum": 32240, "Midpoint": 34600, "Maximum": 43700},
    {"Grade": "113A", "Minimum": 32240, "Midpoint": 38000, "Maximum": 48000},
    {"Grade": "114A", "Minimum": 32800, "Midpoint": 41900, "Maximum": 52500},
    {"Grade": "115A", "Minimum": 34400, "Midpoint": 45900, "Maximum": 57600},
    {"Grade": "116A", "Minimum": 38000, "Midpoint": 50600, "Maximum": 63700},
    {"Grade": "117A", "Minimum": 41600, "Midpoint": 55500, "Maximum": 69700},
]

# Convert to DataFrame
grades_df = pd.DataFrame(grades_data)

# Step 2: Define simulation parameters
annual_increase_rate = 0.02  # 2% increase each year
years_to_simulate = 5

# Step 3: Check salary projection and whether it exceeds bands.
projection_results = []

for _, row in grades_df.iterrows():
    grade = row["Grade"]
    max_salary = row["Maximum"]
    current_salary = row["Midpoint"]
    exceeded_year = None
    salary_progression = []

    for year in range(1, years_to_simulate + 1):
        current_salary *= (1 + annual_increase_rate)
        salary_progression.append(round(current_salary, 2))
        if exceeded_year is None and current_salary > max_salary:
            exceeded_year = year

    projection_results.append({
        "Grade": grade,
        "Initial Midpoint": row["Midpoint"],
        "Max Salary": max_salary,
        "Year 1": salary_progression[0],
        "Year 2": salary_progression[1],
        "Year 3": salary_progression[2],
        "Year 4": salary_progression[3],
        "Year 5": salary_progression[4],
        "Exceeded Year": exceeded_year if exceeded_year else "Within Range"
    })

# Step 4: Display results
results_df = pd.DataFrame(projection_results)
print(results_df)
