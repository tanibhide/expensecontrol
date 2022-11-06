from msilib import schema
import mysql.connector
import time
import datetime

from xml.dom.minidom import parse
import xml.dom.minidom

import xml.etree.ElementTree as ET
  
def insert_types(cursor):
    types = ["Books/Media", "Car Rental", "Entertainment", "Fuel", "Hardware", "Lodging", "Meals", "Software", "Travel"]
    sql = "insert into expense_types (type)  values(%s)"
    for type in types:
        val = (type,)
        cursor.execute(sql, val)

def insert_currencies(cursor):
    tree = ET.parse("./currencies.xml")
    root = tree.getroot()


    # DOMTree = xml.dom.minidom.parse("./currencies.xml")
    # collection = DOMTree.documentElement
    # root = collection.getElementsByTagName("ISO_4217")
    # print(root)
    # ccytbl = root[0].getElementsByTagName("CcyTbl")
    # currencies = ccytbl[0].getElementsByTagName("CcyNtry")
    for curr in  root.findall('./CcyTbl/CcyNtry'):
        # for item in curr:
        #     print("Key : {}".format(item))
        ccy = curr.find('Ccy')
        if ccy is not None:
            ccy = ccy.text
            sql = 'select ccy from currencies where ccy = %s'
            val = (ccy,)
            cursor.execute(sql, val)
            entry = cursor.fetchone()
            if not entry:
                ccy_name = curr.find('CcyNm').text
                country_name = curr.find('CtryNm').text
                print(ccy + ", " + ccy_name + ", " + country_name)
                sql = "insert into currencies (ccy, ccy_name, country_name)  values(%s, %s, %s)"
                val = (ccy, ccy_name, country_name, )
                cursor.execute(sql, val)

db = mysql.connector.connect(
  host ="localhost",
  user ="expensecontrol",
  passwd ="Snickers123",
  database = 'expensecontrol'
)

cursor = db.cursor()

sql = "delete from expenses"
cursor.execute(sql)

sql = "delete from expense_reports"
cursor.execute(sql)

sql = "delete from employees"
cursor.execute(sql)
db.commit()


sql = "insert into employees ( employee_number, \
        password, employee_name, employee_email, bank_name, account_number, ifsc_code) \
        values (%s, %s, %s, %s, %s, %s, %s)"
val = ('1', '1234', 'Tanisha Bhide', 'tanisha.demo@gmail.com', 'Deutsche Bank', '12345678', 'DEUTINPBC')
cursor.execute(sql, val)

sql = "insert into roles (employee_number, role) values (%s, %s)"
val = ('1', 'ADMIN')
cursor.execute(sql, val)
val = ('1', 'APPROVER')
cursor.execute(sql, val)
val = ('1', 'SUBMITTER')
cursor.execute(sql, val)

sql = "insert into employees ( employee_number, \
        password, employee_name, employee_email, bank_name, account_number, ifsc_code) \
        values (%s, %s, %s, %s, %s, %s, %s)"
val = ('2', '1234', 'Jackie Sanders', 'jackie.sanders@gmail.com', 'Deutsche Bank', '12345678', 'DEUTINPBC')
cursor.execute(sql, val)

sql = "insert into roles (employee_number, role) values (%s, %s)"
val = ('2', 'APPROVER')
cursor.execute(sql, val)
val = ('2', 'SUBMITTER')
cursor.execute(sql, val)

sql = "insert into employees ( employee_number, \
        password, employee_name, employee_email, bank_name, account_number, ifsc_code) \
        values (%s, %s, %s, %s, %s, %s, %s)"
val = ('3', '1234', 'Ryan Woods', 'ryan.woods@gmail.com', 'Deutsche Bank', '12345678', 'DEUTINPBC')
cursor.execute(sql, val)

sql = "insert into roles (employee_number, role) values (%s, %s)"
val = ('3', 'SUBMITTER')
cursor.execute(sql, val)

insert_types(cursor)
insert_currencies(cursor=cursor)

sql = "insert into expense_reports ( employee_number, \
        create_ts, \
        last_update_ts, \
        title, \
        status) \
        values (%s, %s, %s, %s, %s)"

ts = time.time()
timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
val = ('1', timestamp, timestamp, 'Travel to The Burrow', 'CREATED')
cursor.execute(sql, val)
report_id = cursor.lastrowid
print(report_id)

sql = "insert into expenses (expense_report_id, type, create_ts, location, \
    amount, \
    currency, \
    purpose) values (%s, %s, %s, %s, %s, %s, %s)"

val = (str(report_id), "Travel", timestamp, "London", "12000.50", "GBP", "Time travel to London")
cursor.execute(sql, val)

val = (str(report_id), "Travel", timestamp, "London", "23", "GBP", "Food on the way")
cursor.execute(sql, val)

val = (str(report_id), "Books/Media", timestamp, "The Burrow", "12", "GBP", "Harry Potter books")
cursor.execute(sql, val)

val = (str(report_id), "Travel", timestamp, "Malfoy Manor", "45", "GBP", "Manor sight-seeing")
cursor.execute(sql, val)

val = (str(report_id), "Meals", timestamp, "Shell Cottage", "22", "GBP", "Dinner")
cursor.execute(sql, val)

sql = "insert into expense_reports ( employee_number, \
        create_ts, \
        last_update_ts, \
        title, \
        status) \
        values (%s, %s, %s, %s, %s)"

val = ('1', timestamp, timestamp, 'Travel to Hawkins, Indiana', 'CREATED')
cursor.execute(sql, val)
report_id = cursor.lastrowid
print(report_id)

sql = "insert into expenses (expense_report_id, type, create_ts, location, \
    amount, \
    currency, \
    purpose) values (%s, %s, %s, %s, %s, %s, %s)"

val = (str(report_id), "Travel", timestamp, "Mumbai", "1200", "USD", "Flight ticket")
cursor.execute(sql, val)

val = (str(report_id), "Travel", timestamp, "Hawkins", "68", "USD", "Train to Hawkins")
cursor.execute(sql, val)

val = (str(report_id), "Books/Media", timestamp, "Hawkins", "20", "USD", "Stranger Things media")
cursor.execute(sql, val)

val = (str(report_id), "Software", timestamp, "Hawkins", "400", "USD", "Time travel software")
cursor.execute(sql, val)


sql = "insert into expense_reports ( employee_number, \
        create_ts, \
        last_update_ts, \
        title, \
        status) \
        values (%s, %s, %s, %s, %s)"

val = ('3', timestamp, timestamp, 'Sightseeing in Pune', 'CREATED')
cursor.execute(sql, val)
report_id = cursor.lastrowid
print(report_id)

sql = "insert into expenses (expense_report_id, type, create_ts, location, \
    amount, \
    currency, \
    purpose) values (%s, %s, %s, %s, %s, %s, %s)"

val = (str(report_id), "Travel", timestamp, "Pune", "50", "INR", "Metro ticket")
cursor.execute(sql, val)

val = (str(report_id), "Meals", timestamp, "Pune", "250", "INR", "Breakfast at Vaishali")
cursor.execute(sql, val)

val = (str(report_id), "Travel", timestamp, "Lonavala", "500", "INR", "Visit to Lonavala")
cursor.execute(sql, val)

val = (str(report_id), "Travel", timestamp, "Pune", "400", "INR", "Visit to old town")
cursor.execute(sql, val)

val = (str(report_id), "Travel", timestamp, "Pune", "1200", "INR", "Train to Delhi")
cursor.execute(sql, val)

db.commit()
db.close()
