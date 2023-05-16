from flask import Flask, request, jsonify
from settings import handle_exceptions, logger, connection

app = Flask(__name__)


# create employee
@app.route('/employee/insert', methods=['POST'])
@handle_exceptions
def add_employee():
    cur, conn = connection()
    logger(__name__).warning("starting the data base connection to create employee")
    if "name" and "hourly_rate" and "no_of_working_days" and "workinghours" not in request.json:
        raise Exception("details missing")
    data = request.get_json()
    name = data.get('name')
    hourly_rate = data.get('hourly_rate')
    no_of_workingdays = data.get('no_of_workingdays')
    workinghours = data.get('workinghours')
    # Insert new employee into the database
    cur.execute("INSERT INTO employee_data (name, hourly_rate, no_of_workingdays, workinghours) VALUES (%s, %s,%s, %s)", (name, hourly_rate,no_of_workingdays, workinghours))
    conn.commit()
    return jsonify({'message': 'Employee added successfully'})


# update data
@app.route('/employee/update/<int:employee_id>', methods=['PUT'])
def update_employee(employee_id):
    cur, conn = connection()
    if not employee_id:
        return "employee_id not found"
    data = request.get_json()
    new_hourly_rate = data['hourly_rate']


    # Update employee hourly rate in the database
    cur.execute("UPDATE employee_data SET hourly_rate = %s  WHERE employee_id = %s", (new_hourly_rate,  employee_id))
    conn.commit()

    return jsonify({'message': 'Employee updated successfully'})


# fetch information of a id
@app.route('/employee/<int:employee_id>', methods=['GET'], endpoint="employee_data")
@handle_exceptions
def employee_data(employee_id):
    cur, conn = connection()
    logger(__name__).warning("starting the data base connection to get information of employee")
    cur.execute("SELECT name, hourly_rate FROM employee_data WHERE employee_id = %s", (employee_id,))
    row = cur.fetchone()
    if not row:
        return jsonify({"message": "employee_id ID not found"})

    name, hourly_rate = row
    data = {
        "name": name,
        "hourly_rate": hourly_rate
    }
    conn.commit()
    return jsonify({"message": "report of employee_id", "details": data}), 200


# fetch all id's information
@app.route("/employees/all", methods=["GET"], endpoint="all_employees")
@handle_exceptions
def all_employess():
    cur, conn = connection()
    logger(__name__).warning("starting the database connection")
    cur.execute('SELECT *  FROM employee_data')
    rows = cur.fetchall()
    print(rows)
    if not rows:
        return jsonify({"message": f"No rows found "})
    data_list = []
    for row in rows:
        empolyee_id,name,hourly_rate,no_of_workingdays,salary,workinghours = row
        data ={
            "empolyee_id" : empolyee_id,
            "name" : name,
             "hourly_rate" : hourly_rate,
            "no_of_workingdays" : no_of_workingdays,
            "salary" : salary,
            "workinghours" : workinghours

        }
        data_list.append(data)
        logger(__name__).warning("close the database connection")

    return jsonify({"message":"all employee's","details":data_list})


# calculate salary
@app.route('/employee/salary/<int:employee_id>', methods=['PUT'], endpoint="calculate_salary")
@handle_exceptions
def calculate_salary(employee_id):
        cur, conn = connection()

        # Retrieve the hourly rate, number of working days, and working hours from the database
        cur.execute("SELECT hourly_rate, no_of_workingdays, workinghours FROM employee_data WHERE employee_id = %s",
                    (employee_id,))
        result = cur.fetchone()

        if result:
            hourly_rate, no_of_workingdays, workinghours = result
        else:
            return jsonify({'error': 'Employee not found'}), 404
        workinghours
        # Calculate the salary
        salary = hourly_rate * no_of_workingdays * workinghours

        # Save the calculated salary in the database
        cur.execute("UPDATE employee_data SET salary = %s WHERE employee_id = %s", (salary, employee_id))
        conn.commit()

        return jsonify({'salary': salary}), 200


# delete an employee
@app.route("/delete/<int:employee_id>", methods=["DELETE"], endpoint="delete_employee")
@handle_exceptions
def delete_account(employee_id):
    cur, conn = connection()
    logger(__name__).warning("starting the database connection")
    cur.execute("DELETE FROM employee_data WHERE employee_id = %s", (employee_id,))
    conn.commit()
    return "Record deleted successfully"


# update information
@app.route("/update/<int:employee_id>", methods=["PUT"], endpoint="update_data")
def update_data(employee_id):
    cur, conn = connection()
    logger(__name__).warning("starting the database connection")
    data = request.get_json()
    no_of_workingdays = data['no_of_workingdays']
    workinghours = data['workinghours']
    cur.execute("SELECT hourly_rate, salary, no_of_workingdays, workinghours FROM employee_data WHERE employee_id = %s",
                (employee_id,))
    result = cur.fetchone()
    if result:
        hourly_rate, old_salary, old_no_of_workingdays, old_workinghours = result
        new_salary = no_of_workingdays * workinghours * hourly_rate
        cur.execute('UPDATE employee_data SET salary=%s, no_of_workingdays=%s, workinghours=%s WHERE employee_id = %s',
                    (new_salary, no_of_workingdays, workinghours, employee_id))
        conn.commit()
        return jsonify({'message': 'Employee data updated successfully'}), 200
    else:
        return jsonify({'error': 'Employee not found'}), 404


# get particular employee salary
@app.route('/salary/<int:employee_id>', methods=['GET'], endpoint="employee_salary")
@handle_exceptions
def employee_salary(employee_id):
    cur, conn = connection()
    logger(__name__).warning("starting the data base connection to get information of employee")
    cur.execute("SELECT name, salary FROM employee_data WHERE employee_id = %s", (employee_id,))
    row = cur.fetchone()
    if not row:
        return jsonify({"message": "employee_id ID not found"})

    name, salary = row
    data = {
        "name": name,
        "salary": salary
    }
    conn.commit()
    return jsonify({"message": "report of employee_id", "details": data}), 200


@app.route("/highest_salary", methods=["GET"],endpoint="get_highest_salary")
def get_highest_salary():
    cur, conn = connection()
    logger(__name__).warning("starting the database connection")
    cur.execute("SELECT name, salary FROM employee_data WHERE salary = (SELECT MAX(salary) FROM employee_data)")
    result = cur.fetchone()
    if result :
        name, highest_salary = result
        return jsonify({'highest_salary': highest_salary,'name':name}), 200
    else:
        return jsonify({'error': 'No employees found or salary data missing'}), 404

if __name__ == '__main__':
    app.run(debug=True)
