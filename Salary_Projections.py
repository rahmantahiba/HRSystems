import sqlite3

grades_data = [
    {"Grade": "112A", "Maximum": 43700},
    {"Grade": "113A", "Maximum": 48000},
    {"Grade": "114A", "Maximum": 52500},
    {"Grade": "115A", "Maximum": 57600},
    {"Grade": "116A", "Maximum": 63700},
    {"Grade": "117A", "Maximum": 69700},
]

def salary_projection():
    '''
    returns a list of all employees and their projected salaries and a list of the total
    of projected salaries for each of the 5 years
    '''
    salary_projection_employees = []
    salary_projection_total = [0,0,0,0,0,0]

    # Connect to the database
    conn = sqlite3.connect("employees.db")
    cursor = conn.cursor()

    # SQL query to select data
    cursor.execute("SELECT * FROM employees")

    # Step 4: Fetch all rows from the query result
    rows = cursor.fetchall()

    #Loop through the rows
    for row in rows:
        employee_id = row[0]  # id
        name = row[1]  # name
        pay = row[4]  # pay
        band = row[5]  # band
        employee = ["did not exceed band", employee_id, name, band, pay]
        salary_projection_total[0] += pay
        maximum_pay = get_maximum_pay(band)
        for year in range(1,6):
            pay *= 1.02
            employee.append(pay)
            salary_projection_total[year] += pay
            if pay > maximum_pay:
                employee[0] = "Band exceeded in year " + str(year)
        salary_projection_employees.append(employee)

    # Close the connection
    conn.close()

    return salary_projection_employees, salary_projection_total


def get_maximum_pay(grade):
    # Loop through the grades_data list to find the grade and its maximum pay
    for grade_info in grades_data:
        if grade_info["Grade"] == grade:
            return grade_info["Maximum"]
