from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import (
    login_user,
    logout_user,
    login_required,
    current_user
)

from database.database import db
from backend.models.user import User
from backend.models.analysis_history import AnalysisHistory


# ==========================================
# CREATE AUTHENTICATION BLUEPRINT
# ==========================================

auth = Blueprint("auth", __name__)


# ==========================================
# USER REGISTRATION
# ==========================================

@auth.route("/register", methods=["GET", "POST"])
def register():

    if current_user.is_authenticated:
        return redirect(url_for("auth.dashboard"))

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        # Validate input
        if not name or not email or not password:
            flash("Please fill in all fields.", "danger")
            return redirect(url_for("auth.register"))

        if len(password) < 8:
            flash("Password must contain at least 8 characters.", "danger")
            return redirect(url_for("auth.register"))

        # Check existing user
        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            flash("This email is already registered.", "warning")
            return redirect(url_for("auth.register"))

        # Create new user
        new_user = User(
            name=name,
            email=email
        )

        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! Please log in.", "success")

        return redirect(url_for("auth.login"))

    return render_template("register.html")


# ==========================================
# USER LOGIN
# ==========================================

@auth.route("/login", methods=["GET", "POST"])
def login():

    if current_user.is_authenticated:
        return redirect(url_for("auth.dashboard"))

    if request.method == "POST":

        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not email or not password:
            flash("Please enter your email and password.", "danger")
            return redirect(url_for("auth.login"))

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):

            login_user(user)

            flash("Login successful!", "success")

            next_page = request.args.get("next")

            # Avoid redirecting to an external website.
            if next_page and next_page.startswith("/") and not next_page.startswith("//"):
                return redirect(next_page)

            return redirect(url_for("auth.dashboard"))

        flash("Invalid email or password.", "danger")

    return render_template("login.html")


# ==========================================
# USER LOGOUT
# ==========================================

@auth.route("/logout")
@login_required
def logout():

    logout_user()

    flash("You have been logged out successfully.", "success")

    return redirect(url_for("auth.login"))


# ==========================================
# USER DASHBOARD
# ==========================================

@auth.route("/dashboard")
@login_required
def dashboard():

    # 1. Get analyses belonging to the logged-in user.
    analyses = (
        AnalysisHistory.query
        .filter_by(user_id=current_user.id)
        .order_by(AnalysisHistory.created_at.desc())
        .all()
    )

    total_analyses = len(analyses)

    # 2. Calculate ATS statistics.
    if total_analyses > 0:

        average_score = round(
            sum(item.ats_score or 0 for item in analyses)
            / total_analyses
        )

        best_score = max(
            (item.ats_score or 0 for item in analyses),
            default=0
        )

    else:
        average_score = 0
        best_score = 0

    # 3. Calculate job matching statistics.
    job_matches = [
        item.match_percentage or 0
        for item in analyses
        if (item.match_percentage or 0) > 0
    ]

    total_job_matches = len(job_matches)

    if total_job_matches > 0:

        average_job_match = round(
            sum(job_matches) / total_job_matches
        )

        highest_job_match = max(job_matches)

    else:
        average_job_match = 0
        highest_job_match = 0

    # 4. Determine performance category.
    if average_score >= 80:
        performance_category = "Excellent"

    elif average_score >= 60:
        performance_category = "Good"

    elif average_score >= 40:
        performance_category = "Average"

    else:
        performance_category = "Needs Improvement"

    # 5. Prepare recent analyses.
    recent_analyses = analyses[:5]

    # 6. Prepare chart data.
    chart_analyses = [
        item for item in reversed(analyses[:10])
        if item.created_at
    ]

    chart_labels = [
        item.created_at.strftime("%d %b %Y")
        for item in chart_analyses
    ]

    chart_scores = [
        item.ats_score or 0
        for item in chart_analyses
    ]

    # 7. Display dashboard.
    return render_template(
        "dashboard.html",
        user=current_user,
        total_analyses=total_analyses,
        average_score=average_score,
        best_score=best_score,
        average_job_match=average_job_match,
        highest_job_match=highest_job_match,
        total_job_matches=total_job_matches,
        performance_category=performance_category,
        recent_analyses=recent_analyses,
        chart_labels=chart_labels,
        chart_scores=chart_scores
    )