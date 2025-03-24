from flask import Blueprint, render_template, current_app, redirect, url_for, Response, request
from flask_login import login_user, logout_user, current_user, LoginManager
from authentication.utils import bcrypt, login_manager
from authentication.models import User
from extensions.db_config import db

auth_blueprint = Blueprint('authentication', __name__)

@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).get(int(user_id))

@auth_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = bcrypt.generate_password_hash(request.form["password"]).decode("utf-8")

        if db.session.query(User).filter_by(username=username).first():
            return "User already exists!", 400

        new_user = User(username=username, password_hash=password)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for("main_page.index"))

    return render_template("auth/registration.html")


@auth_blueprint.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = db.session.query(User).filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for("main_page.index"))

        return "Invalid credentials!", 401

    return render_template("auth/login.html")





