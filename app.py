from flask import Flask, render_template, request, redirect, url_for, session
import json
import os

from PyPDF2 import PdfReader
from docx import Document

from backend import recommend_job_roles, get_skill_gap, get_learning_path
from user_management import register_user, authenticate_user


app = Flask(__name__)

app.secret_key = "skill-job-recommender-secret"


@app.route("/")
def home():

    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        success, message = register_user(
            username,
            email,
            password
        )

        if success:
            return redirect(url_for("login"))

        return render_template(
            "register.html",
            error=message
        )

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        if authenticate_user(username, password):

            session["user"] = username

            return redirect(url_for("skills"))

        return render_template(
            "login.html",
            error="Invalid username or password"
        )

    return render_template("login.html")


@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("home"))


@app.route("/skills", methods=["GET", "POST"])
def skills():

    if "user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":

        skills_text = request.form["skills"]

        skills_list = [
            skill.strip().lower()
            for skill in skills_text.split(",")
            if skill.strip()
        ]

        session["skills"] = skills_list

        experience = request.form["experience"]

        session["experience"] = experience

        return redirect(url_for("recommend"))

    return render_template("skills.html")

@app.route("/recommend")
def recommend():

    if "user" not in session:
        return redirect(url_for("login"))

    skills = session.get("skills", [])

    experience = session.get(
        "experience",
        "entry"
    )

    if not skills:
        return redirect(url_for("skills"))

    recommendations = recommend_job_roles(
        skills,
        experience
    )

    for job in recommendations:

        job["missing_skills"] = get_skill_gap(
            skills,
            job
        )

        job["learning_path"] = get_learning_path(
            job["missing_skills"]
    )
    return render_template(
        "recommend.html",
        recommendations=recommendations,
        skills=skills
    )
@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect(url_for("login"))

    skills = session.get("skills", [])

    experience = session.get(
        "experience",
        "entry"
    )

    recommendations = recommend_job_roles(
        skills,
        experience
    )

    for job in recommendations:

        job["missing_skills"] = get_skill_gap(
            skills,
            job
        )

        job["learning_path"] = get_learning_path(
            job["missing_skills"]
        )

    top_job = None

    if recommendations:
        top_job = recommendations[0]

    return render_template(
        "dashboard.html",
        username=session["user"],
        skills=skills,
        top_job=top_job
    )
@app.route("/parse_resume", methods=["POST"])
def parse_resume():

    if "user" not in session:
        return redirect(url_for("login"))

    file = request.files.get("resume")

    if not file:
        return redirect(url_for("skills"))

    filename = file.filename.lower()

    text = ""

    if filename.endswith(".pdf"):

        reader = PdfReader(file)

        for page in reader.pages:
            text += page.extract_text() or ""

    elif filename.endswith(".docx"):

        document = Document(file)

        for paragraph in document.paragraphs:
            text += paragraph.text + " "

    else:

        return "Only PDF and DOCX files are allowed"

    possible_skills = [
        "python",
        "java",
        "c",
        "c++",
        "sql",
        "html",
        "css",
        "javascript",
        "react",
        "node.js",
        "flask",
        "django",
        "pandas",
        "numpy",
        "matplotlib",
        "machine learning",
        "deep learning",
        "tensorflow",
        "scikit-learn",
        "statistics",
        "git",
        "github",
        "mongodb",
        "mysql",
        "database",
        "data analysis",
        "power bi",
        "excel",
        "aws",
        "cloud computing"
    ]
    text = text.lower()

    found_skills = []

    for skill in possible_skills:

        if skill in text:
            found_skills.append(skill)

    session["skills"] = found_skills

    session["experience"] = "entry"

    return redirect(url_for("recommend"))

       


if __name__ == "__main__":

    app.run(debug=True)