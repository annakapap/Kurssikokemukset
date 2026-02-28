from flask import Flask, render_template, request, redirect, url_for, session, flash, abort
import secrets
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_db, close_db, init_db
from users_repository import get_user_by_username, create_user
import os
from experiences_repository import (
    list_experiences,
    get_experience_by_id,
    get_experience_detail,
    get_experience_owner,
    create_experience,
    update_experience,
    delete_experience,
    list_experiences_by_user,
    count_experiences_by_user
)
from comments_repository import list_comments, add_comment, count_comments_by_user
from categories_repository import list_categories, set_experience_categories, get_experience_categories
from sqlite3 import IntegrityError

app = Flask(__name__)
app.config["SECRET_KEY"] = "dev-secret"  # !!

os.makedirs("instance", exist_ok=True)

app.teardown_appcontext(close_db)
init_db(app)

def current_user_id():
    return session.get("user_id")

def require_login():
    if current_user_id() is None:
        abort(403)
def get_csrf_token():
    """Return a CSRF token stored in session, creating one if needed."""
    token = session.get("csrf_token")
    if not token:
        token = secrets.token_hex(16)
        session["csrf_token"] = token
    return token


def require_csrf():
    """Validate CSRF token for POST requests."""
    form_token = request.form.get("csrf_token", "")
    session_token = session.get("csrf_token", "")
    if not form_token or not session_token or form_token != session_token:
        abort(403)

app.jinja_env.globals["csrf_token"] = get_csrf_token
@app.route("/")
def index():
    return redirect(url_for("experience_list"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        require_csrf()
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            flash("Käyttäjätunnus ja salasana ovat pakollisia.")
            return render_template("register.html")

        try:
           create_user(username, generate_password_hash(password))
        except IntegrityError:
           flash("Käyttäjätunnus on jo käytössä.")
           return render_template("register.html")

        flash("Tunnus luotu. Kirjaudu sisään.")
        return redirect(url_for("login"))

    return render_template("register.html")
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        require_csrf()
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

@app.route("/users/<username>")
def user_page(username):
    user = get_user_by_username(username)
    if user is None:
        abort(404)

    experiences = list_experiences_by_user(user["id"])
    total_experiences = count_experiences_by_user(user["id"])
    total_comments = count_comments_by_user(user["id"])

    return render_template(
        "user_page.html",
        profile_user=user,
        experiences=experiences,
        total_experiences=total_experiences,
        total_comments=total_comments,
    )

@app.route("/experiences")
def experience_list():
    q = request.args.get("q", "").strip()
    rows = list_experiences(q)
    return render_template("experience_list.html", experiences=rows, q=q)

@app.route("/experiences/new", methods=["GET", "POST"])
def experience_create():
    require_login()

    if request.method == "POST":
        require_csrf()
        course_name = request.form.get("course_name", "").strip()
        content = request.form.get("content", "").strip()

        categories = list_categories()

        if not course_name or not content:
            flash("Kurssin nimi ja kokemus ovat pakollisia.")
            return render_template(
                "experience_form.html",
                mode="create",
                exp=None,
                categories=categories,
                selected_category_ids=[]
            )

        experience_id = create_experience(current_user_id(), course_name, content)

        category_ids = request.form.getlist("category_ids")
        category_ids = [int(x) for x in category_ids]
        set_experience_categories(experience_id, category_ids)

        return redirect(url_for("experience_list"))

    categories = list_categories()
    return render_template(
        "experience_form.html",
        mode="create",
        exp=None,
        categories=categories,
        selected_category_ids=[]
    )



@app.route("/experiences/<int:experience_id>/edit", methods=["GET", "POST"])
def experience_edit(experience_id):
    require_login()

    exp = get_experience_by_id(experience_id)

    if exp is None:
        abort(404)
    if exp["user_id"] != current_user_id():
        abort(403)

    if request.method == "POST":
        require_csrf()
        course_name = request.form.get("course_name", "").strip()
        content = request.form.get("content", "").strip()

        if not course_name or not content:
            flash("Kurssin nimi ja kokemus ovat pakollisia.")
            categories = list_categories()
            selected_category_ids = [
                c["id"] for c in get_experience_categories(experience_id)
            ]
            return render_template(
                "experience_form.html",
                mode="edit",
                exp=exp,
                categories=categories,
                selected_category_ids=selected_category_ids
            )

        update_experience(experience_id, course_name, content)

       
        category_ids = request.form.getlist("category_ids")
        category_ids = [int(x) for x in category_ids]
        set_experience_categories(experience_id, category_ids)

        return redirect(url_for("experience_list"))

   
    categories = list_categories()
    selected_category_ids = [
        c["id"] for c in get_experience_categories(experience_id)
    ]

    return render_template(
        "experience_form.html",
        mode="edit",
        exp=exp,
        categories=categories,
        selected_category_ids=selected_category_ids
    )


@app.route("/experiences/<int:experience_id>/delete", methods=["POST"])
def experience_delete(experience_id):
    require_login()
    require_csrf()

    exp = get_experience_owner(experience_id)
    if exp is None:
        abort(404)
    if exp["user_id"] != current_user_id():
        abort(403)

    delete_experience(experience_id)
    return redirect(url_for("experience_list"))

@app.route("/experiences/<int:experience_id>")
def experience_detail(experience_id):
    exp = get_experience_detail(experience_id)
    if exp is None:
        abort(404)

    comments = list_comments(experience_id)
    categories = get_experience_categories(experience_id)

    return render_template(
        "experience_detail.html",
        exp=exp,
        comments=comments,
        categories=categories,
    )

@app.route("/experiences/<int:experience_id>/comment")
def comment_form(experience_id):
    require_login()

    exp = get_experience_detail(experience_id)
    if exp is None:
        abort(404)

    return render_template("comment_form.html", exp=exp)

@app.route("/experiences/<int:experience_id>/comments", methods=["POST"])
def comment_create(experience_id):
    require_login()
    require_csrf()

    content = request.form.get("content", "").strip()
    if not content:
        flash("Kommentti ei voi olla tyhjä.")
        return redirect(url_for("experience_detail", experience_id=experience_id))

    exp = get_experience_detail(experience_id)
    if exp is None:
        abort(404)

    add_comment(experience_id, current_user_id(), content)
    return redirect(url_for("experience_detail", experience_id=experience_id))

if __name__ == "__main__":
    app.run(debug=True)
