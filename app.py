from flask import Flask, render_template, request, redirect, url_for, session, flash, abort
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_db, close_db, init_db
from users_repository import get_user_by_username
from experiences_repository import list_experiences, get_experience_by_id
import os
from experiences_repository import (
    list_experiences,
    get_experience_by_id,
    create_experience,
    update_experience,
    delete_experience,
)

app = Flask(__name__)
app.config["SECRET_KEY"] = "dev-secret"  # vaihda myöhemmin

os.makedirs("instance", exist_ok=True)

app.teardown_appcontext(close_db)
init_db(app)

def current_user_id():
    return session.get("user_id")

def require_login():
    if current_user_id() is None:
        abort(403)

@app.route("/")
def index():
    return redirect(url_for("experience_list"))

# --- Auth ---
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            flash("Käyttäjätunnus ja salasana ovat pakollisia.")
            return render_template("register.html")

        db = get_db()
        try:
            db.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username, generate_password_hash(password)),
            )
            db.commit()
        except Exception:
            flash("Käyttäjätunnus on jo käytössä.")
            return render_template("register.html")

        flash("Tunnus luotu. Kirjaudu sisään.")
        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = get_user_by_username(username)
 

        if user is None or not check_password_hash(user["password_hash"], password):
            flash("Väärä käyttäjätunnus tai salasana.")
            return render_template("login.html")

        session.clear()
        session["user_id"] = user["id"]
        session["username"] = user["username"]
        return redirect(url_for("experience_list"))

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# --- Experiences (CRUD + list + search) ---
@app.route("/experiences")
def experience_list():
    q = request.args.get("q", "").strip()
    rows = list_experiences(q)
    return render_template("experience_list.html", experiences=rows, q=q)

@app.route("/experiences/new", methods=["GET", "POST"])
def experience_create():
    require_login()

    if request.method == "POST":
        course_name = request.form.get("course_name", "").strip()
        content = request.form.get("content", "").strip()

        if not course_name or not content:
            flash("Kurssin nimi ja kokemus ovat pakollisia.")
            return render_template("experience_form.html", mode="create", exp=None)

        create_experience(current_user_id(), course_name, content)

        return redirect(url_for("experience_list"))

    return render_template("experience_form.html", mode="create", exp=None)

@app.route("/experiences/<int:experience_id>/edit", methods=["GET", "POST"])
def experience_edit(experience_id):
    require_login()
    db = get_db()

    exp = get_experience_by_id(experience_id)

    if exp is None:
        abort(404)
    if exp["user_id"] != current_user_id():
        abort(403)

    if request.method == "POST":
        course_name = request.form.get("course_name", "").strip()
        content = request.form.get("content", "").strip()

        if not course_name or not content:
            flash("Kurssin nimi ja kokemus ovat pakollisia.")
            return render_template("experience_form.html", mode="edit", exp=exp)

        update_experience(experience_id, course_name, content)

        return redirect(url_for("experience_list"))

    return render_template("experience_form.html", mode="edit", exp=exp)

@app.route("/experiences/<int:experience_id>/delete", methods=["POST"])
def experience_delete(experience_id):
    require_login()
    db = get_db()

    exp = db.execute(
    "SELECT id, user_id FROM experiences WHERE id = ?",
    (experience_id,),
).fetchone()

    if exp is None:
        abort(404)
    if exp["user_id"] != current_user_id():
        abort(403)

    delete_experience(experience_id)
    return redirect(url_for("experience_list"))

if __name__ == "__main__":
    app.run(debug=True)
