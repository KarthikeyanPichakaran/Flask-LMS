import json
import os
import datetime
from configparser import ConfigParser  # config file
from flask import (Flask, render_template, session, request, redirect, url_for, flash, g)  # flask framework
from flask_sqlalchemy import SQLAlchemy  # mysql db connection
from flask_httpauth import HTTPBasicAuth  # basic authentication
from flask_marshmallow import Marshmallow  # data serialization

curdata = datetime.datetime.today().strftime("%d%m%Y")

# app initialization
app = Flask(__name__)
app.secret_key = "Secret_Key"  # session

# db configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:" "@localhost/bankapp"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
ma = Marshmallow(app)

class gender(db.Model):
    gen_id = db.Column(db.Integer, primary_key=True)
    gndr = db.Column(db.String(20))

    def __init__(self, gen_id, gndr):
        self.gen_id = gen_id
        self.gendr = gndr
        
class desig(db.Model):
    des_id = db.Column(db.Integer, primary_key=True)
    desg = db.Column(db.String(20))

    def __init__(self, des_id, desg):
        self.des_id = des_id
        self.desg = desg

class leaveType(db.Model):
    leave_id = db.Column(db.Integer, primary_key=True)
    leave_type = db.Column(db.String(20))

    def __init__(self, leave_id, desg):
        self.leave_id = leave_id
        self.desg = desg

class empdata(db.Model):
    """Model creation for emp data"""
    emp_id = db.Column(db.Integer, primary_key=True)
    emp_name = db.Column(db.String(50))
    desig = db.Column(db.String(50))
    gender = db.Column(db.String(20))
    el_leave = db.Column(db.Integer)
    leave_taken = db.Column(db.Integer)
    remain_leave = db.Column(db.Integer)
    reporting_to = db.Column(db.String(50))
    
    def __init__(self, emp_name, desig, gender, el_leave, leave_taken, remain_leave, reporting_to):
        self.emp_name = emp_name
        self.desig = desig
        self.gender = gender
        self.el_leave = el_leave
        self.leave_taken = leave_taken
        self.remain_leave = remain_leave
        self.reporting_to = reporting_to
        
with app.app_context():
    db.create_all()

class EmpSchema(ma.Schema):
    """Data serializaion"""
    class Meta:
        fields = ("emp_name", "desig", "gender", "el_leave", "leave_taken", "remain_leave", "reporting_to")

class GenSchema(ma.Schema):
    class Meta:
        fields = ("gen_id", "gndr")
    
class DesgSchema(ma.Schema):
    class Meta:
        fields = ("des_id", "desg")

class LeaveSchema(ma.Schema):
    class Meta:
        fields = ("leave_id", "leave_type")

# custdata table schema
emp_schema = EmpSchema()
emp_schema = EmpSchema(many=True)
gen_schema = GenSchema()
gen_schema = GenSchema(many=True)
desg_schema = DesgSchema()
desg_schema = DesgSchema(many=True)
lev_schema = LeaveSchema()
lev_schema = LeaveSchema(many=True)

@app.route('/')
def admin_login():
    #emp_all_data = empdata.query.all()
    return render_template("emp_index.html")

@app.route('/insert', methods=['POST'])
def insert():
    if request.method == 'POST':
        emp_name = request.form['emp_name']
        desig = request.form['desig']
        gender = request.form['gender']
        el_leave = request.form['el_leave']
        leave_taken = request.form['leave_taken']
        remain_leave = request.form['remain_leave']
        reporting_to = request.form['reporting_to']
        
        new_data = empdata(emp_name, desig, gender, el_leave, leave_taken, remain_leave, reporting_to)
        db.session.add(new_data)
        db.session.commit()

        flash("New Employee Added Successfully")

        return redirect(url_for('admin_login'))

@app.route('/update', methods=['GET', 'POST'])
def update():
    if request.method == 'POST':
        get_data = empdata.query.get(request.form.get('emp_id'))
        get_data.emp_name = request.form['emp_name']
        get_data.desig = request.form['desig']
        get_data.gender = request.form['gender']
        get_data.el_leave = request.form['el_leave']
        get_data.leave_taken = request.form['leave_taken']
        get_data.remain_leave = request.form['remain_leave']
        get_data.reporting_to = request.form['reporting_to']

        db.session.commit()
        flash("Employee Data Updated Successfully")
        return redirect(url_for('admin_login'))

@app.route('/delete/<emp_id>', methods=['GET', 'POST'])
def delete(emp_id):
    emp_data = empdata.query.get(emp_id)
    db.session.delete(emp_data)
    db.session.commit()
    flash("Customer Data Deleted Successfully")
    return redirect(url_for('admin_login'))

@app.route('/employees/assign/<int:id>', methods=['GET', 'POST'])
def assign_employee(id):
    """
    Assign a department, a paygrade and a role to an employee
    """
    employee = empdata.query.get_or_404(id)

    # prevent admin from being assigned a department or role
    if employee.is_admin:
        abort(403)

    form = EmployeeAssignForm(obj=employee)
    if form.validate_on_submit():
        employee.department = form.department.data
        employee.role = form.role.data
        employee.grade = form.grade.data
        db.session.add(employee)
        db.session.commit()
        flash('You have successfully assigned a department, paygrade and a role.')

        # redirect to the roles page
        return redirect(url_for('admin.list_employees'))

    return render_template('admin/employees/employee.html',
                           employee=employee, form=form,
                           title='Assign Employee')

# main function
if __name__ == "__main__":
    """run flask application"""
    app.run(debug=True)
