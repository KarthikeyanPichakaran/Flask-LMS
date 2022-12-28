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
        fields = (
            "emp_name",
            "desig",
            "gender",
            "el_leave",
            "leave_taken",
            "remain_leave",
            "reporting_to"
            )
# custdata table schema
emp_schema = EmpSchema()
emp_schema = EmpSchema(many=True)

@app.route('/')
def admin_login():
    emp_all_data = empdata.query.all()
    return render_template("emp_index.html", employees=emp_all_data)


# main function
if __name__ == "__main__":
    """run flask application"""
    app.run(debug=True)
