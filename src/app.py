from logging import exception
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
# from flask_modals import Modal, render_template_modal

import os
import re
import time
import datetime

mysql = MySQL()
app = Flask(__name__)
app.config['MYSQL_USER'] = 'expensecontrol'
app.config['MYSQL_PASSWORD'] = 'Snickers123'
app.config['MYSQL_DB'] = 'expensecontrol'
app.config['MYSQL_HOST'] = 'localhost'
mysql.init_app(app)

# modal = Modal(app)

app.secret_key = os.urandom(12)


@app.route('/expensecontrol/', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msg = 'Incorrect credentials'
    # Check if "employee_number" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'employee_number' in request.form and 'password' in request.form:
        # Create variables for easy access
        employee_number = request.form['employee_number']
        password = request.form['password']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM employees WHERE employee_number = %s AND password = %s', (employee_number, password,))
        # Fetch one record and return result
        account = cursor.fetchone()
        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = str(account['id'])
            session['employee_number'] = account['employee_number']
            session['employee_name'] = account['employee_name']

            cursor.execute('select role from roles where employee_number = %s', (employee_number,))
            roles = cursor.fetchall()
            role_list = []
            for r in roles:
                role_list.append(r['role'])
            session['roles'] = role_list
            print(session['roles'])
            # Redirect to home page
            return redirect(url_for('home'))
        else:
            # Account doesnt exist or employee_number/password incorrect
            msg = 'Incorrect employee_number/password!'
    return render_template('index.html', msg=msg)

@app.route('/expensecontrol/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('employee_number', None)
   # Redirect to login page
   return redirect(url_for('login'))

# http://localhost:5000/pythinlogin/register - this will be the registration page, we need to use both GET and POST requests
@app.route('/expensecontrol/register', methods=['GET', 'POST'])
def register():
    if 'loggedin' in session:
        if 'ADMIN' in session['roles']:
            # Output message if something goes wrong...
            msg = ''
            # Check if "employee_number", "password" and "email" POST requests exist (user submitted form)
            if request.method == 'POST' and \
                    'employee_number' in request.form and \
                    'password' in request.form and \
                    'email' in request.form and \
                    'employee_name' in request.form and \
                    'bank_name' in request.form and \
                    'account_number' in request.form and \
                    'ifsc_code' in request.form:
                # Create variables for easy access
                employee_number = request.form['employee_number']
                password = request.form['password']
                email = request.form['email']
                employee_name = request.form['employee_name']
                bank_name = request.form['bank_name']
                account_number = request.form['account_number']
                ifsc_code = request.form['ifsc_code']
                approver = 'role_approver' in request.form

                # Check if account exists using MySQL
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute('SELECT * FROM employees WHERE employee_number = %s', (employee_number,))
                account = cursor.fetchone()
                # If account exists show error and validation checks
                if account:
                    msg = 'Account already exists!'
                elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                    msg = 'Invalid email address!'
                elif not re.match(r'[A-Za-z0-9]+', employee_name):
                    msg = 'Username must contain only characters and numbers!'
                elif not employee_number or not employee_name or not password or not email:
                    msg = 'Please fill out the form!'
                else:
                    # Account doesnt exists and the form data is valid, now insert new account into accounts table
                    cursor.execute('INSERT INTO employees VALUES (NULL, %s, %s, %s, %s, %s, %s, %s)', 
                        (employee_number, password, employee_name, email, bank_name, account_number, ifsc_code,))
                    # Add roles
                    sql = "insert into roles (employee_number, role) values (%s, %s)"
                    val = (employee_number, 'SUBMITTER')
                    cursor.execute(sql, val)

                    if approver:
                        val = (employee_number, 'APPROVER')
                        cursor.execute(sql, val)

                    mysql.connection.commit()

                    msg = 'You have successfully registered!'
            elif request.method == 'POST':
                # Form is empty... (no POST data)
                msg = 'Please fill out the form!'
            # Show registration form with message (if any)
            return render_template('register.html', msg=msg)
        else:
            return redirect(url_for('home'))
    else:
        return redirect(url_for('login'))


@app.route('/expensecontrol/home')
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        expense_reports = get_expense_reports(employee_number=session['employee_number'])
        return render_template('home.html', employee_number=session['employee_number'], 
        employee_name=session['employee_name'], expense_reports=expense_reports)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

def get_expense_reports(employee_number):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM expense_reports WHERE employee_number = %s', (employee_number,))
    results = cursor.fetchall()
    cursor.close()
    return results

@app.route('/expensecontrol/create_new_expense_report')
def create_new_expense_report():
    return render_template('create_new_expense_report.html')

@app.route('/expensecontrol/profile')
def profile():
    # Check if user is loggedin
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM employees WHERE id = %s', (session['id'],))
        account = cursor.fetchone()
        # Show the profile page with account info
        return render_template('profile.html', account=account)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


@app.route('/expensecontrol/reportdetails/<report_id>')
def expense_report_details(report_id):
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * from expense_reports where id = %s', (report_id))
        report = cursor.fetchone()
        cursor.execute('SELECT * FROM expenses WHERE expense_report_id = %s', (report_id,))
        expenses = cursor.fetchall()
        cursor.execute('select sum(e.amount) as total from expense_reports r, expenses e where \
            e.expense_report_id = r.id and \
            r.id = %s', (report_id,))
        report_total = cursor.fetchone()

        cursor.execute("select u.employee_number as employee_number, u.employee_name as employee_name from \
                        employees u, roles r where \
                        r.role = 'APPROVER' and \
                        r.employee_number = u.employee_number and \
                        u.employee_number <> %s", (session['employee_number'],))
        approvers = cursor.fetchall()

        if report['approver_employee_number']:
            cursor.execute('select employee_name from employees where employee_number = %s', 
            (report['approver_employee_number'],))
            report['approver_employee_name'] = cursor.fetchone()['employee_name']
        cursor.close()
        return render_template('reportdetails.html', report=report, 
                            expenses=expenses, report_total=report_total, approvers=approvers)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route('/expensecontrol/add_expense_to_report/<report_id>')
def add_expense_to_report(report_id):
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * from expense_reports where id = %s', (report_id))
        report = cursor.fetchone()

        cursor.execute('select * from expense_types')
        expense_types = cursor.fetchall()

        cursor.execute('select ccy from currencies')
        currencies = cursor.fetchall()
        cursor.close()

        return render_template('add_expense_to_report.html', 
                    report=report, expense_types=expense_types, currencies=currencies)
    return redirect(url_for('login'))

@app.route('/expensecontrol/add_new_expense_report', methods=['GET', 'POST'])
def add_new_expense_report():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        sql = "insert into expense_reports ( employee_number, \
        create_ts, \
        last_update_ts, \
        title, \
        status) \
        values (%s, %s, %s, %s, %s)"

        ts = time.time()
        timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        val = (session['employee_number'], timestamp, timestamp, 
                request.form['report_title'], 'CREATED')
        cursor.execute(sql, val)
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('home'))
    return redirect(url_for('login'))

@app.route('/expensecontrol/add_expense', methods=['GET', 'POST'])
def add_expense():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    sql = "insert into expenses (expense_report_id, type, create_ts, location, \
        amount, \
        currency, \
        purpose) values (%s, %s, %s, %s, %s, %s, %s)"

    ts = time.time()
    timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

    val = (str(request.form['report_id']), request.form['type'], timestamp, 
                request.form['location'], request.form['amount'], request.form['currency'], 
                request.form['purpose'])
    cursor.execute(sql, val)
    mysql.connection.commit()
    cursor.close()
    return redirect(url_for('expense_report_details', report_id=request.form['report_id']))

@app.route('/expensecontrol/edit_expense/<report_id>/<expense_id>')
def edit_expense(report_id, expense_id):
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('select * from expense_reports where id = %s', (report_id,))
        report = cursor.fetchone()
        cursor.execute('select * from expenses where id = %s', (expense_id,))
        expense = cursor.fetchone()

        cursor.execute('select * from expense_types')
        expense_types = cursor.fetchall()

        cursor.execute('select ccy from currencies')
        currencies = cursor.fetchall()
        cursor.close()
        return render_template('edit_expense.html', report=report, expense=expense, 
        expense_types=expense_types, currencies=currencies)
    return redirect(url_for('login'))

@app.route('/expensecontrol/execute_edit_expense', methods=['GET', 'POST'])
def execute_edit_expense():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    cursor.execute("update expenses set type = %s, location = %s, amount = %s, \
                    currency = %s, purpose = %s \
            where id = %s", (request.form['type'], request.form['location'], 
            request.form['amount'], request.form['currency'], 
            request.form['purpose'], request.form['expense_id'],))
    mysql.connection.commit()
    cursor.close()
    return redirect(url_for('expense_report_details', report_id=request.form['report_id']))

@app.route('/expensecontrol/delete_expense/<report_id>/<expense_id>')
def delete_expense(report_id, expense_id):
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('delete from expenses where id = %s', (str(expense_id),))
        cursor.close()
        mysql.connection.commit()
        return redirect(url_for('expense_report_details', report_id=report_id))
    return redirect(url_for('login'))

@app.route('/expensecontrol/delete_report/<report_id>')
def delete_report(report_id):
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('delete from expense_reports where id = %s', (str(report_id),))
        cursor.close()
        mysql.connection.commit()
        return redirect(url_for('home'))
    return redirect(url_for('login'))


@app.route('/expensecontrol/submit_report', methods=['POST'])
def submit_report():
    if 'loggedin' in session:
        report_id = request.form['report_id']
        update_report_status(report_id=report_id, status='SUBMITTED', approver_employee_number=request.form['approver'])
        return redirect(url_for('expense_report_details', report_id=report_id))
    return redirect(url_for('login'))


@app.route('/expensecontrol/approve_report,<report_id>')
def approve_report(report_id):
    if 'loggedin' in session:
        update_report_status(report_id=report_id, status='APPROVED', approver_employee_number=session['employee_number'])
        return redirect(url_for('list_of_reports_for_approval'))
    return redirect(url_for('login'))

@app.route('/expensecontrol/revoke_report', methods=['POST'])
def revoke_report():
    if 'loggedin' in session:
        report_id = request.form['report_id']
        update_report_status(report_id=report_id, status='REVOKED')
        return redirect(url_for('expense_report_details', report_id=report_id))
    return redirect(url_for('login'))

def get_report_by_id(report_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * from expense_reports where id = %s', (report_id))
    report = cursor.fetchone()
    cursor.close()
    return report

def update_report_status(report_id, status, approver_employee_number=None):
    ts = time.time()
    timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('update expense_reports set status = %s, last_update_ts = %s where id = %s', 
                    (status, timestamp, str(report_id),))
    cursor.execute('delete from expense_report_approval_queue where report_id = %s and \
        approver_employee_number = %s', (report_id, approver_employee_number,))
    if status == 'SUBMITTED':
        # Add to approval queue
        cursor.execute('insert into expense_report_approval_queue (report_id, approver_employee_number) \
                        values (%s, %s)', (report_id, approver_employee_number,))
    if status == 'APPROVED':
        cursor.execute("update expense_reports set approver_employee_number = %s where id = %s",
                (approver_employee_number, report_id,))        

    cursor.close()
    mysql.connection.commit()


@app.route('/expensecontrol/list_of_reports_for_approval')
def list_of_reports_for_approval():
    if 'loggedin' in session:
        if 'APPROVER' in session['roles']:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT e.*, u.employee_name FROM expense_reports e, expense_report_approval_queue q, employees u \
                            WHERE e.id = q.report_id and \
                            e.employee_number = u.employee_number and \
                            e.employee_number <> %s and \
                            q.approver_employee_number = %s", (session['employee_number'], 
                            session['employee_number'],))
            results = cursor.fetchall()
            cursor.close()
            return render_template('list_of_reports_approval.html', expense_reports=results)
        else:
            return redirect(url_for('home'))
    return redirect(url_for('login'))


# Users stuff
@app.route('/expensecontrol/list_users')
def list_users():
    if 'loggedin' in session:
        if 'ADMIN' in session['roles']:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

            cursor.execute('select distinct role from roles')
            all_roles = cursor.fetchall()
            cursor.execute('select id, employee_number, employee_name, employee_email from employees')
            users = cursor.fetchall()
            for u in users:
                cursor.execute('select role from roles where employee_number = %s', (u['employee_number'],))
                user_roles = cursor.fetchall()
                role_list = []
                for ur in user_roles:
                    role_list.append(ur['role'])
                u['roles'] = role_list
            cursor.close()

            return render_template('list_users.html', users=users, all_roles=all_roles)
        else:
            return redirect(url_for('home'))
    else:
        return redirect(url_for('login'))


@app.route('/expensecontrol/delete_user/<user_id>')
def delete_user(user_id):
    if 'loggedin' in session:
        if 'ADMIN' in session['roles']:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('delete from employees where id = %s', (str(user_id),))
            cursor.close()
            mysql.connection.commit()
        return redirect(url_for('list_users'))
    return redirect(url_for('login'))

def add_user():
    # Output message if something goes wrong...
    msg = ''
    # Check if "employee_number", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and \
            'employee_number' in request.form and \
            'password' in request.form and \
            'email' in request.form and \
            'employee_name' in request.form and \
            'bank_name' in request.form and \
            'account_number' in request.form and \
            'ifsc_code' in request.form:
        # Create variables for easy access
        employee_number = request.form['employee_number']
        password = request.form['password']
        email = request.form['email']
        employee_name = request.form['employee_name']
        bank_name = request.form['bank_name']
        account_number = request.form['account_number']
        ifsc_code = request.form['ifsc_code']

        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM employees WHERE employee_number = %s', (employee_number,))
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', employee_name):
            msg = 'Username must contain only characters and numbers!'
        elif not employee_number or not employee_name or not password or not email:
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO employees VALUES (NULL, %s, %s, %s, %s, %s, %s, %s)', 
                (employee_number, password, employee_name, email, bank_name, account_number, ifsc_code,))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)
