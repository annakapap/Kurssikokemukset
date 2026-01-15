from flask import Flask, render_template, request, redirect, url_for, session, flash, abort
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_db, close_db, init_db
import os

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

        db = get_db()
        user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()

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
    db = get_db()

    if q:
        rows = db.execute(
            """
            SELECT e.*, u.username
            FROM experiences e
            JOIN users u ON u.id = e.user_id
            WHERE e.course_name LIKE ? OR e.content LIKE ?
            ORDER BY e.created_at DESC
            """,
            (f"%{q}%", f"%{q}%"),
        ).fetchall()
    else:
        rows = db.execute(
            """
            SELECT e.*, u.username
            FROM experiences e
            JOIN users u ON u.id = e.user_id
            ORDER BY e.created_at DESC
            """
        ).fetchall()

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

        db = get_db()
        db.execute(
            "INSERT INTO experiences (user_id, course_name, content) VALUES (?, ?, ?)",
            (current_user_id(), course_name, content),
        )
        db.commit()
        return redirect(url_for("experience_list"))

    return render_template("experience_form.html", mode="create", exp=None)

@app.route("/experiences/<int:experience_id>/edit", methods=["GET", "POST"])
def experience_edit(experience_id):
    require_login()
    db = get_db()

    exp = db.execute("SELECT * FROM experiences WHERE id = ?", (experience_id,)).fetchone()
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

        db.execute(
            """
            UPDATE experiences
            SET course_name = ?, content = ?, updated_at = datetime('now')
            WHERE id = ?
            """,
            (course_name, content, experience_id),
        )
        db.commit()
        return redirect(url_for("experience_list"))

    return render_template("experience_form.html", mode="edit", exp=exp)

@app.route("/experiences/<int:experience_id>/delete", methods=["POST"])
def experience_delete(experience_id):
    require_login()
    db = get_db()

    exp = db.execute("SELECT * FROM experiences WHERE id = ?", (experience_id,)).fetchone()
    if exp is None:
        abort(404)
    if exp["user_id"] != current_user_id():
        abort(403)

    db.execute("DELETE FROM experiences WHERE id = ?", (experience_id,))
    db.commit()
    return redirect(url_for("experience_list"))

if __name__ == "__main__":
    app.run(debug=True)
