import pandas as pd

# Static A-band salary data
grades_data = [
    {"Grade": "112A", "Minimum": 32240, "Midpoint": 34600, "Maximum": 43700},
    {"Grade": "113A", "Minimum": 32240, "Midpoint": 38000, "Maximum": 48000},
    {"Grade": "114A", "Minimum": 32800, "Midpoint": 41900, "Maximum": 52500},
    {"Grade": "115A", "Minimum": 34400, "Midpoint": 45900, "Maximum": 57600},
    {"Grade": "116A", "Minimum": 38000, "Midpoint": 50600, "Maximum": 63700},
    {"Grade": "117A", "Minimum": 41600, "Midpoint": 55500, "Maximum": 69700},
]

# Score to increase rate mapping
score_increase = {
    1: 0.00,
    2: 0.01,
    3: 0.02,
    4: 0.025,
    5: 0.03
}


def simulate_grade_progression(performance_scores):
    """
    Simulates salary progression for each A-grade over 5 years given performance scores.

    Args:
        performance_scores (list): List of 5 performance scores (1–5 scale)

    Returns:
        pd.DataFrame: Salary projections and exceeded year information
    """
    if len(performance_scores) != 5:
        raise ValueError("You must provide exactly 5 performance scores (one per year).")

    grades_df = pd.DataFrame(grades_data)
    projection_results = []

    for _, row in grades_df.iterrows():
        grade = row["Grade"]
        max_salary = row["Maximum"]
        current_salary = row["Midpoint"]
        exceeded_year = None
        salary_progression = []

        for year in range(1, 6):
            score = performance_scores[year - 1]
            increase_rate = score_increase.get(score, 0.00)
            current_salary *= (1 + increase_rate)
            current_salary = round(current_salary, 2)
            salary_progression.append(current_salary)

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

    return pd.DataFrame(projection_results)

def main():
    # Define the performance scores for 5 years
    performance_scores = [3, 3, 3, 3, 3]  # Modify this list as needed

    # Run the simulation
    results_df = simulate_grade_progression(performance_scores)

    # Print the result
    print("\nSalary Projection Based on Performance Scores:")
    print(results_df)

main()