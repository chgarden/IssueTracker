#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 17 16:28:01 2020

@author: crystalhiggins
"""

from flask import Flask, render_template, request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pymysql
from sqlalchemy.util import b64encode



pymysql.install_as_MySQLdb()
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "pdf", "png"}

app = Flask(__name__)
app.secret_key = "MustangRunOnHighHopes"

app.config['SQLALCHEMY_DATABASE_URI']= 'mysql://admin:cs506project@issuetracker.c4yrqykdjpgb.us-east-2.rds.amazonaws.com:3306/issuetracker'
app.config["ALLOWED_IMAGE_EXTENSIONS"] = ["JPEG", "JPG", "PNG", "GIF"]
app.config["MAX_IMAGE_FILESIZE"] = 0.5 * 1024 * 1024

db = SQLAlchemy(app)

def allowed_image(filename):
    if not "." in filename:
        return False

    ext = filename.rsplit(".", 1)[1]

    if ext.upper() in app.config["ALLOWED_IMAGE_EXTENSIONS"]:
        return True
    else:
        return False

def allowed_image_filesize(filesize):
    if int(filesize) <= app.config["MAX_IMAGE_FILESIZE"]:
        return True
    else:
        return False

class Issue(db.Model):
    issue_id = db.Column(db.Integer, unique=True, primary_key=True)
    project = db.Column(db.String(40))
    priority = db.Column(db.String(20))
    status = db.Column(db.String(20))
    summary = db.Column(db.String(50))
    description = db.Column(db.String(500))
    assignee = db.Column(db.String(40))
    date_created = db.Column(db.Date, default=datetime.now())
    attached_image = db.Column(db.BLOB)

@app.route("/")
def list():
    all_data = db.session.query(Issue).all()
    print(all_data)

    return render_template('index.html', title='IssueTracker', issues = all_data)


@app.route("/update/<int:id>", methods=["POST", "GET"])
def update(id):
    if request.method == "POST":
        issue_id = request.form["issue_id"]
        project = request.form["project"]
        priority = request.form["priority"]
        status = request.form["status"]
        summary = request.form["summary"]
        description = request.form["description"]
        assignee = request.form["assignee"]

        if "delete" in request.form:
            db.session.query(Issue).filter(Issue.issue_id == issue_id).delete()

            db.session.commit()
            flash("Issue Deleted")
            return redirect(url_for("add"))
        else:
            one_issue = db.session.query(Issue).filter(Issue.issue_id == issue_id).first()
            one_issue.project = project
            one_issue.priority=priority
            one_issue.status=status
            one_issue.summary=summary
            one_issue.description=description
            one_issue.assignee=assignee

            db.session.commit()
            flash("Issue Updated")
            return redirect(request.host_url)
    else:
        one_issue = db.session.query(Issue).filter(Issue.issue_id==id).first()
        if (one_issue is None):
            flash("Issue Not Found")
            return redirect(url_for("find"))

        new_image = b64encode(one_issue.attached_image)
        one_issue.attached_image = new_image
        return render_template('update.html', title='Update Issue', issue = one_issue)

@app.route("/add", methods=["POST", "GET"])
def add():
    if request.method == "POST":
        project = request.form["project"]
        priority = request.form["priority"]
        status = request.form["status"]
        summary = request.form["summary"]
        description = request.form["description"]
        assignee = request.form["assignee"]
        file = request.files["file"]

        if not (file.filename == ""):
            if "filesize" in request.cookies:
                if not allowed_image_filesize(request.cookies["filesize"]):
                    print("Filesize exceeded maximum limit")
                    return redirect(request.url)

                if not allowed_image(file.filename):
                    print("That file extension is not allowed")
                    return redirect(request.url)

        issue = Issue(  project=project,
                        priority=priority,
                        status=status,
                        summary=summary,
                        description=description,
                        assignee=assignee,
                        attached_image=file.read())

        db.session.add(issue)
        db.session.commit()
        flash("Issue Added")

        return redirect(request.host_url)
    else:
        return render_template('add.html', title='Add Issue')


@app.route("/find", methods=["POST", "GET"])
def find():
    if request.method == "POST":
       # issue_id = request.form["issue_id"]
       # one_issue = db.session.query(Issue).filter(Issue.issue_id == id).first()
        return redirect(url_for("update", id=request.form["issue_id"]))
    else:
        return render_template('find.html', title='Find Issue')

if __name__ == "__main__":
    app.run(debug=True)
